"""Load validated CSV files into already-created PostgreSQL tables."""
from pathlib import Path
import pandas as pd
from sqlalchemy import inspect
from db_config import get_engine

root = Path(__file__).resolve().parents[1]
data_dir = root / "data"

# Lista de importación en orden estricto: primero padres (categories, physical_locations, users),
# luego hijos con llaves foráneas (catalog_items y audit_logs).
imports = [
    ("categories", "categories.csv", ["category_id", "name"]),
    ("physical_locations", "physical_locations.csv", ["location_id", "building", "lab", "shelf_cabinet"]),
    ("users", "users.csv", ["user_id", "full_name", "email", "role"]),
    ("catalog_items", "catalog_items.csv", [
        "item_id", "internal_code", "serial_number", "standardized_name", 
        "technical_description", "brand", "model", "category_id", "location_id"
    ]),
    ("audit_logs", "audit_logs.csv", [
        "log_id", "item_id", "user_id", "action_performed", "timestamp", "modified_attributes"
    ]),
]

# Una sola transacción: si todos los archivos cargan con éxito se aplica, si falla uno se revierte todo.
with get_engine().begin() as connection:
    inspector = inspect(connection)
    for table, filename, expected_columns in imports:
        if not inspector.has_table(table, schema="public"):
            raise RuntimeError(f"Table '{table}' is missing. Run create_schema.py")
        
        csv_path = data_dir / filename
        # Tratamos códigos internos o números de serie como texto para evitar pérdida de formato
        frame = pd.read_csv(csv_path, dtype={
            "internal_code": "string", 
            "serial_number": "string"
        })
        
        if list(frame.columns) != expected_columns:
            raise ValueError(f"Incorrect CSV columns in {filename}. Expected {expected_columns}, got {list(frame.columns)}")
        
        if frame.empty:
            raise ValueError(f"Empty file: {filename}")
        
        # Permitimos valores nulos solo en columnas opcionales (como serial_number o brand)
        frame.to_sql(
            table, 
            con=connection, 
            if_exists="append", 
            index=False, 
            method="multi"
        )
        print(f"Imported {len(frame)} rows into {table}")

print("Import completed successfully.")