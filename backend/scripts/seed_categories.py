"""Seed default ingredient categories."""
from app.core.database import get_session, init_database
from app.models.category import IngredientCategory

DEFAULT_CATEGORIES = [
    {"name": "Susu & Dairy", "color": "#3b82f6"},
    {"name": "Kopi & Teh", "color": "#8b5cf6"},
    {"name": "Gula & Pemanis", "color": "#f59e0b"},
    {"name": "Coklat & Powder", "color": "#78350f"},
    {"name": "Tepung & Bahan Kering", "color": "#a16207"},
    {"name": "Telur", "color": "#ca8a04"},
    {"name": "Mentega & Lemak", "color": "#eab308"},
    {"name": "Sirup & Flavoring", "color": "#06b6d4"},
    {"name": "Air & Minuman", "color": "#0ea5e9"},
    {"name": "Es & Pendingin", "color": "#67e8f9"},
]

def main():
    init_database("dev-mode")
    db = next(get_session())
    existing = db.query(IngredientCategory).count()
    if existing > 0:
        print("Categories already seeded.")
        db.close()
        return
    for cat_data in DEFAULT_CATEGORIES:
        db.add(IngredientCategory(**cat_data))
    db.commit()
    print(f"Seeded {len(DEFAULT_CATEGORIES)} categories.")
    db.close()

if __name__ == "__main__":
    main()
