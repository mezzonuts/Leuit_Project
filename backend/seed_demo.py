"""Seed database with dummy data for demo."""
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.core.database import get_session, init_database
from app.models.ingredient import Ingredient
from app.models.menu import MenuItem, RecipeItem
from app.models.outlet import Outlet
from app.models.purchase import InventoryPurchase, PaymentMethod, PaymentStatus
from app.models.supplier import Supplier
from app.models.transaction import IngredientDailyUsage, SalesTransaction


def main():
    # Init DB
    init_database("dummy-demo-key")

    db = next(get_session())

    # Check if already seeded
    if db.query(Ingredient).count() > 0:
        print("Already seeded. Skipping.")
        db.close()
        return

    # 1. Outlets
    outlets = [
        Outlet(name="Cafe Dago", address="Jl. Ir. H. Juanda No. 123, Bandung", phone="081234567890"),
        Outlet(name="Cafe Antapani", address="Jl. Antapani No. 45, Bandung", phone="081234567891"),
    ]
    db.add_all(outlets)
    db.flush()

    # 2. Suppliers
    suppliers = [
        Supplier(name="PT Susu Segar Jaya", phone_whatsapp="081298765432", payment_terms_days=14),
        Supplier(name="CV Gula Makmur", phone_whatsapp="081398765433", payment_terms_days=0),
        Supplier(name="Toko Kopi Nusantara", phone_whatsapp="081498765434", payment_terms_days=7),
        Supplier(name="PT Tepung Terigu", phone_whatsapp="081598765435", payment_terms_days=14),
        Supplier(name="UD Coklat Premium", phone_whatsapp="081698765436", payment_terms_days=0),
    ]
    db.add_all(suppliers)
    db.flush()

    # 3. Ingredients
    ingredients = [
        Ingredient(barcode_sku="8991234567890", name="Susu Segar UHT", unit="ml", cost_per_unit=8000,
                   shelf_life_days=7, current_stock=150, min_stock_threshold=50, lead_time_days=2, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567891", name="Susu UHT Coklat", unit="ml", cost_per_unit=9000,
                   shelf_life_days=7, current_stock=80, min_stock_threshold=30, lead_time_days=2, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567892", name="Gula Pasir", unit="gram", cost_per_unit=13000,
                   shelf_life_days=365, current_stock=500, min_stock_threshold=100, lead_time_days=3, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567893", name="Kopi Bubuk Robusta", unit="gram", cost_per_unit=45000,
                   shelf_life_days=180, current_stock=300, min_stock_threshold=80, lead_time_days=5, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567894", name="Teh Hijau Bubuk", unit="gram", cost_per_unit=35000,
                   shelf_life_days=365, current_stock=200, min_stock_threshold=50, lead_time_days=7, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567895", name="Coklat Bubuk", unit="gram", cost_per_unit=50000,
                   shelf_life_days=365, current_stock=250, min_stock_threshold=60, lead_time_days=7, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567896", name="Tepung Terigu", unit="gram", cost_per_unit=8000,
                   shelf_life_days=180, current_stock=1000, min_stock_threshold=200, lead_time_days=3, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567897", name="Telur Ayam", unit="pcs", cost_per_unit=2500,
                   shelf_life_days=30, current_stock=60, min_stock_threshold=20, lead_time_days=2, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567898", name="Mentega", unit="gram", cost_per_unit=30000,
                   shelf_life_days=60, current_stock=40, min_stock_threshold=20, lead_time_days=3, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567899", name="Whipped Cream", unit="ml", cost_per_unit=15000,
                   shelf_life_days=45, current_stock=50, min_stock_threshold=20, lead_time_days=3, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567900", name="Sirup Vanila", unit="ml", cost_per_unit=20000,
                   shelf_life_days=365, current_stock=100, min_stock_threshold=30, lead_time_days=5, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567901", name="Sirup Coklat", unit="ml", cost_per_unit=18000,
                   shelf_life_days=365, current_stock=120, min_stock_threshold=30, lead_time_days=5, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567902", name="Air Mineral (Galon)", unit="pcs", cost_per_unit=6000,
                   shelf_life_days=365, current_stock=20, min_stock_threshold=5, lead_time_days=1, outlet_id=outlets[0].id),
        Ingredient(barcode_sku="8991234567903", name="Es Batu", unit="kg", cost_per_unit=2000,
                   shelf_life_days=1, current_stock=30, min_stock_threshold=10, lead_time_days=1, outlet_id=outlets[0].id),
    ]
    db.add_all(ingredients)
    db.flush()

    # 4. Menu Items + Recipes
    menu_data = [
        ("Kopi Susu Gula Aren", 25000, "POS-001", [(3, 20), (2, 30), (1, 150), (13, 100), (14, 150)]),
        ("Es Kopi Susu", 22000, "POS-002", [(3, 20), (2, 30), (1, 100), (13, 200), (14, 100)]),
        ("Cappuccino", 28000, "POS-003", [(3, 25), (1, 180), (10, 20)]),
        ("Latte", 28000, "POS-004", [(3, 25), (1, 200), (10, 20)]),
        ("Matcha Latte", 30000, "POS-005", [(4, 15), (1, 200), (2, 30), (13, 200), (14, 100)]),
        ("Coklat Klasik", 25000, "POS-006", [(5, 30), (2, 40), (1, 200), (13, 200), (14, 100)]),
        ("Teh Manis", 15000, "POS-007", [(4, 10), (2, 30), (13, 250), (14, 150)]),
        ("Teh Hangat", 15000, "POS-008", [(4, 10), (2, 30), (13, 250)]),
        ("Croissant Coklat", 20000, "POS-009", [(7, 80), (8, 40), (5, 20), (2, 20)]),
        ("Caramel Latte", 32000, "POS-010", [(3, 25), (1, 200), (11, 30), (10, 20)]),
    ]

    menus = []
    for name, price, pos_id, recipes in menu_data:
        menu = MenuItem(pos_item_id=pos_id, name=name, sale_price=price)
        menus.append(menu)
        db.add(menu)
    db.flush()

    for menu, (_, _, _, recipes) in zip(menus, menu_data):
        for ing_id, qty in recipes:
            db.add(RecipeItem(menu_item_id=menu.id, ingredient_id=ing_id, quantity_required=qty))

    # 5. Sales Transactions (last 30 days)
    import hashlib
    for day in range(30):
        date = datetime.now(UTC) - timedelta(days=day)
        # 3-8 sales per day
        for sale in range(3 + (day % 6)):
            menu = menus[(day + sale) % len(menus)]
            tx_time = date.replace(hour=9 + (sale * 2), minute=(15 + (sale * 10)) % 60, second=0)
            raw = f"POS-{day}-{sale}_{tx_time.isoformat()}_{menu.pos_item_id}"
            tx_hash = hashlib.sha256(raw.encode()).hexdigest()
            db.add(SalesTransaction(
                transaction_hash=tx_hash,
                pos_reference_id=f"POS-{day}-{sale}",
                menu_item_id=menu.id,
                quantity=1 + (sale % 3),
                transaction_time=tx_time,
            ))

    # 6. Daily Usage
    for day in range(30):
        date = (datetime.now(UTC) - timedelta(days=day)).date()
        for ing in ingredients:
            # Random-ish usage based on position
            usage = 5 + ((day + ing.id) % 30) * 2
            db.add(IngredientDailyUsage(
                usage_date=date,
                ingredient_id=ing.id,
                total_quantity_used=float(usage),
            ))

    # 7. Purchases
    purchase_data = [
        (ingredients[0].id, suppliers[0].id, 500, 4000000, PaymentMethod.CREDIT, PaymentStatus.UNPAID, 14),
        (ingredients[2].id, suppliers[1].id, 1000, 13000000, PaymentMethod.CASH, PaymentStatus.PAID, 0),
        (ingredients[3].id, suppliers[2].id, 500, 22500000, PaymentMethod.CREDIT, PaymentStatus.PAID, 7),
        (ingredients[5].id, suppliers[4].id, 300, 15000000, PaymentMethod.CASH, PaymentStatus.PAID, 0),
        (ingredients[6].id, suppliers[3].id, 2000, 16000000, PaymentMethod.CREDIT, PaymentStatus.UNPAID, 14),
        (ingredients[7].id, suppliers[1].id, 100, 250000, PaymentMethod.CASH, PaymentStatus.PAID, 0),
        (ingredients[1].id, suppliers[0].id, 300, 2700000, PaymentMethod.CREDIT, PaymentStatus.UNPAID, 14),
        (ingredients[10].id, suppliers[2].id, 200, 4000000, PaymentMethod.CASH, PaymentStatus.PAID, 0),
    ]

    for ing_id, sup_id, qty, cost, method, status, days in purchase_data:
        purchase_date = datetime.now(UTC) - timedelta(days=days if days > 0 else 1)
        due = purchase_date + timedelta(days=days) if days > 0 else None
        db.add(InventoryPurchase(
            purchase_date=purchase_date,
            ingredient_id=ing_id,
            supplier_id=sup_id,
            quantity=float(qty),
            total_cost=float(cost),
            payment_method=method,
            payment_status=status,
            due_date=due,
        ))

    db.commit()
    db.close()

    # Create security keyring for unlock
    from nacl.public import PublicKey

    from app.core.config import settings
    from app.core.security.key_envelope import KeyEnvelope
    from app.models.security import SecurityKeyring

    db2 = next(get_session())
    dev_pub_path = Path(settings.PUBLIC_KEY_PATH)
    if dev_pub_path.exists():
        dev_pub_hex = dev_pub_path.read_text().strip()
        dev_public_key = PublicKey(bytes.fromhex(dev_pub_hex))
        dek = KeyEnvelope.generate_dek()
        envelope = KeyEnvelope.create_envelope(dek, "123456", dev_public_key)
        keyring = SecurityKeyring(
            encrypted_dek_owner=envelope["encrypted_dek_owner"],
            encrypted_dek_developer=envelope["encrypted_dek_developer"],
        )
        db2.add(keyring)
        db2.commit()
        print("  Security keyring created (PIN: 123456)")
    db2.close()

    print("=" * 50)
    print("  DEMO DATA SEEDED SUCCESSFULLY!")
    print("=" * 50)
    print("  2 Outlets")
    print("  5 Suppliers")
    print("  14 Ingredients")
    print("  10 Menu Items + 50 Recipe Items")
    print("  ~150 Sales Transactions (30 days)")
    print("  ~420 Daily Usage Records")
    print("  8 Purchases (Cash + Credit)")
    print("=" * 50)
    print("  Login PIN: 123456")
    print("=" * 50)


if __name__ == "__main__":
    main()