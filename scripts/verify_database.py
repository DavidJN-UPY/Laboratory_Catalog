"""Check sample row counts and display joined catalog information."""
from sqlalchemy import text
from db_config import get_engine

expected = {
    "categories": 4, 
    "physical_locations": 3, 
    "users": 3,
    "catalog_items": 8, 
    "audit_logs": 2
}

query = text("""
    SELECT i.internal_code, i.standardized_name, c.name AS category, 
           CONCAT(p.building, ' - ', p.lab, ' (', p.shelf_cabinet, ')') AS location
    FROM catalog_items AS i
    JOIN categories AS c ON c.category_id = i.category_id
    JOIN physical_locations AS p ON p.location_id = i.location_id
    ORDER BY i.item_id;
""")

with get_engine().connect() as connection:
    for table, wanted in expected.items():
        found = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar_one()
        print(f"{table}: {found} rows (expected {wanted})")
        if found != wanted:
            raise AssertionError(f"Unexpected count for {table}")

    rows = connection.execute(query).mappings().all()
    if len(rows) != expected["catalog_items"]:
        raise AssertionError("Some catalog items have broken references")
    
    print("\n--- Catálogo de Equipos Vinculados ---")
    for row in rows:
        print(f"[{row['internal_code']}] {row['standardized_name']} | Categoria: {row['category']} | Ubicacion: {row['location']}")

print("\nAll sample checks passed successfully!")