"""Outlets API endpoints for multi-outlet management."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.models.outlet import Outlet
from app.schemas.outlet_schema import (
    OutletCreate,
    OutletListResponse,
    OutletResponse,
    OutletUpdate,
)

router = APIRouter(prefix="/outlets", tags=["Outlets"])


@router.get("", response_model=OutletListResponse)
def list_outlets(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> OutletListResponse:
    """List all outlets."""
    outlets = db.query(Outlet).filter(Outlet.is_active).all()
    return OutletListResponse(
        items=[OutletResponse(
            id=o.id,
            name=o.name,
            address=o.address,
            phone=o.phone,
            is_active=o.is_active,
            settings=o.settings,
            created_at=o.created_at.isoformat() if o.created_at else None,
            updated_at=o.updated_at.isoformat() if o.updated_at else None,
        ) for o in outlets],
        total=len(outlets),
    )


@router.post("", response_model=OutletResponse)
def create_outlet(
    data: OutletCreate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> OutletResponse:
    """Create a new outlet."""
    outlet = Outlet(**data.model_dump())
    db.add(outlet)
    db.commit()
    db.refresh(outlet)
    return OutletResponse(
        id=outlet.id,
        name=outlet.name,
        address=outlet.address,
        phone=outlet.phone,
        is_active=outlet.is_active,
        settings=outlet.settings,
        created_at=outlet.created_at.isoformat() if outlet.created_at else None,
        updated_at=outlet.updated_at.isoformat() if outlet.updated_at else None,
    )


@router.get("/{outlet_id}", response_model=OutletResponse)
def get_outlet(
    outlet_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> OutletResponse:
    """Get an outlet by ID."""
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return OutletResponse(
        id=outlet.id,
        name=outlet.name,
        address=outlet.address,
        phone=outlet.phone,
        is_active=outlet.is_active,
        settings=outlet.settings,
        created_at=outlet.created_at.isoformat() if outlet.created_at else None,
        updated_at=outlet.updated_at.isoformat() if outlet.updated_at else None,
    )


@router.put("/{outlet_id}", response_model=OutletResponse)
def update_outlet(
    outlet_id: int,
    data: OutletUpdate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> OutletResponse:
    """Update an outlet."""
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(outlet, field, value)

    db.commit()
    db.refresh(outlet)
    return OutletResponse(
        id=outlet.id,
        name=outlet.name,
        address=outlet.address,
        phone=outlet.phone,
        is_active=outlet.is_active,
        settings=outlet.settings,
        created_at=outlet.created_at.isoformat() if outlet.created_at else None,
        updated_at=outlet.updated_at.isoformat() if outlet.updated_at else None,
    )
