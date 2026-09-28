from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from typing import Optional, List
import pandas as pd
import io
import hashlib
import json
from datetime import datetime, timezone
from app.models.menu import MenuItem

from app.api.v1.deps import get_db, verify_license
from app.schemas.sync_schema import (
    PosSyncUploadResponse,
    PosSyncHistoryItem,
    PosSyncHistoryResponse,
)
from app.schemas.ingredient_schema import IngredientResponse
from app.models.transaction import SalesTransaction, PosSyncLog, IngredientDailyUsage
from app.models.ingredient import Ingredient
from app.models.menu import RecipeItem
from app.core.config import settings

router = APIRouter(prefix="/sync", tags=["POS Sync"])

@router.post("/pos-csv", response_model=PosSyncUploadResponse)
async def upload_pos_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """
    Upload and reconcile POS CSV file.
    Supports Moka, Majoo, Olsera CSV formats.
    Deduplicates using SHA256 hash of (Order_ID + Timestamp + Menu_ID).
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    try:
        # Read CSV
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # Normalize column names (case-insensitive)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Expected columns: order_id, timestamp, item_name/menu_id, qty/quantity
        # Try to map common column names
        col_mapping = {
            'order_id': ['order_id', 'orderid', 'id_transaksi', 'nomor_transaksi'],
            'timestamp': ['timestamp', 'waktu', 'tanggal', 'datetime', 'created_at'],
            'menu_id': ['menu_id', 'item_id', 'id_menu', 'product_id'],
            'item_name': ['item_name', 'nama_item', 'nama_produk', 'menu_name', 'product_name'],
            'qty': ['qty', 'quantity', 'jumlah', 'qty_sold'],
        }

        mapped_cols = {}
        for target, candidates in col_mapping.items():
            for c in candidates:
                if c in df.columns:
                    mapped_cols[target] = c
                    break

        required = ['order_id', 'timestamp', 'qty']
        for req in required:
            if req not in mapped_cols:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required column: {req}. Available: {list(df.columns)}"
                )

        # Create sync log
        sync_log = PosSyncLog(
            file_name=file.filename,
            total_rows_read=len(df),
            new_rows_inserted=0,
            duplicate_rows_skipped=0,
        )
        db.add(sync_log)
        db.flush()

        new_count = 0
        duplicate_count = 0
        stock_deductions = {}  # ingredient_id -> total_qty

        for _, row in df.iterrows():
            # Build unique transaction hash
            order_id = str(row[mapped_cols['order_id']])
            timestamp = str(row[mapped_cols['timestamp']])
            menu_identifier = str(row.get(mapped_cols.get('menu_id'), row.get(mapped_cols.get('item_name'), '')))
            qty = int(row[mapped_cols['qty']])

            raw_hash = f"{order_id}_{timestamp}_{menu_identifier}"
            tx_hash = hashlib.sha256(raw_hash.encode()).hexdigest()

            # Check duplicate
            existing = db.query(SalesTransaction).filter(
                SalesTransaction.transaction_hash == tx_hash
            ).first()

            if existing:
                duplicate_count += 1
                continue

            # Find menu item
            menu_item = None
            if 'menu_id' in mapped_cols:
                menu_item = db.query(MenuItem).filter(
                    MenuItem.pos_item_id == str(row[mapped_cols['menu_id']])
                ).first()

            if not menu_item and 'item_name' in mapped_cols:
                menu_item = db.query(MenuItem).filter(
                    MenuItem.name.ilike(f"%{row[mapped_cols['item_name']]}%")
                ).first()

            if not menu_item:
                # Skip rows with unmatched menu items
                duplicate_count += 1
                continue

            # Insert transaction
            new_tx = SalesTransaction(
                transaction_hash=tx_hash,
                pos_reference_id=order_id,
                menu_item_id=menu_item.id,
                quantity=qty,
                transaction_time=pd.to_datetime(timestamp),
                sync_log_id=sync_log.id,
            )
            db.add(new_tx)
            new_count += 1

            # Calculate stock deductions from BOM
            recipes = db.query(RecipeItem).filter(
                RecipeItem.menu_item_id == menu_item.id
            ).all()

            for recipe in recipes:
                ingredient_id = recipe.ingredient_id
                deduction = float(recipe.quantity_required) * qty
                stock_deductions[ingredient_id] = stock_deductions.get(ingredient_id, 0) + deduction

        # Apply stock deductions
        reconciled_count = 0
        for ing_id, deduct_qty in stock_deductions.items():
            ingredient = db.query(Ingredient).filter(Ingredient.id == ing_id).first()
            if ingredient:
                ingredient.current_stock = max(0.0, float(ingredient.current_stock) - deduct_qty)

                # Record daily usage
                today = datetime.now(timezone.utc).date()
                daily_usage = db.query(IngredientDailyUsage).filter(
                    IngredientDailyUsage.usage_date == today,
                    IngredientDailyUsage.ingredient_id == ing_id
                ).first()

                if daily_usage:
                    daily_usage.total_quantity_used += deduct_qty
                else:
                    daily_usage = IngredientDailyUsage(
                        usage_date=datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc),
                        ingredient_id=ing_id,
                        total_quantity_used=deduct_qty,
                    )
                    db.add(daily_usage)

                reconciled_count += 1

        # Update sync log
        sync_log.new_rows_inserted = new_count
        sync_log.duplicate_rows_skipped = duplicate_count
        sync_log.reconciled_stock_items = reconciled_count

        db.commit()

        return PosSyncUploadResponse(
            status="success",
            new_inserted=new_count,
            duplicates_skipped=duplicate_count,
            message=f"Processed {len(df)} rows: {new_count} new, {duplicate_count} duplicates skipped"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@router.get("/history", response_model=PosSyncHistoryResponse)
def get_sync_history(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Get sync history with pagination."""
    query = db.query(PosSyncLog).order_by(desc(PosSyncLog.uploaded_at))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return PosSyncHistoryResponse(
        items=[PosSyncHistoryItem.model_validate(item) for item in items],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )

@router.get("/history/{sync_id}")
def get_sync_detail(
    sync_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get detailed sync result."""
    sync_log = db.query(PosSyncLog).filter(PosSyncLog.id == sync_id).first()
    if not sync_log:
        raise HTTPException(status_code=404, detail="Sync log not found")

    transactions = db.query(SalesTransaction).filter(
        SalesTransaction.sync_log_id == sync_id
    ).limit(100).all()

    return {
        "sync_log": PosSyncHistoryItem.model_validate(sync_log),
        "transactions": [
            {
                "id": t.id,
                "pos_reference_id": t.pos_reference_id,
                "menu_item_name": t.menu_item.name if t.menu_item else None,
                "quantity": t.quantity,
                "transaction_time": t.transaction_time.isoformat(),
            }
            for t in transactions
        ],
    }