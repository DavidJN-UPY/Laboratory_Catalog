from pathlib import Path
import uuid

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import inspect, text
from scripts.db_config import get_engine

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Laboratory Catalog API",
    description="API de inventario para el laboratorio de PCB",
    version="1.1.0"
)

# Permite que el HTML se abra desde otro origen (archivo local, Live Server, Streamlit 8501)
# y aun así consulte esta API en el puerto 8000.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^(null|https?://(localhost|127\.0\.0\.1)(:\d+)?)$",
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = get_engine()


def _rows(sql: str):
    try:
        with engine.connect() as connection:
            return [dict(r) for r in connection.execute(text(sql)).mappings().all()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _clean(table: str, pk: str, payload: dict):
    """Deja solo columnas que existen en la tabla (y nunca la llave primaria)."""
    valid = {c["name"] for c in inspect(engine).get_columns(table)} - {pk}
    data = {k: v for k, v in payload.items() if k in valid}
    if not data:
        raise HTTPException(status_code=400, detail="No llegó ningún campo válido.")
    return data


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(BASE_DIR.parent / "frontend" / "index.html")


@app.get("/categories")
def list_categories():
    return _rows("SELECT * FROM categories ORDER BY category_id")


@app.get("/physical-locations")
def list_physical_locations():
    return _rows("SELECT * FROM physical_locations ORDER BY location_id")


@app.get("/users")
def list_users():
    return _rows("SELECT * FROM users ORDER BY user_id")


@app.get("/catalog-items")
def list_catalog_items():
    return _rows("SELECT * FROM catalog_items ORDER BY item_id")


@app.get("/audit-logs")
def list_audit_logs():
    return _rows("SELECT * FROM audit_logs ORDER BY log_id DESC")


@app.post("/catalog-items", status_code=201)
def create_catalog_item(payload: dict = Body(...)):
    data = _clean("catalog_items", "item_id", payload)
    # Los formularios mandan null o "" cuando el campo queda vacío: también se genera el código.
    if not str(data.get("internal_code") or "").strip():
        data["internal_code"] = f"LAB-{uuid.uuid4().hex[:10].upper()}"
    cols = ", ".join(data)
    params = ", ".join(f":{k}" for k in data)
    try:
        with engine.begin() as connection:
            item_id = connection.execute(
                text("SELECT COALESCE(MAX(item_id), 0) + 1 FROM catalog_items")
            ).scalar_one()
            data["item_id"] = item_id
            cols = "item_id, " + cols
            params = ":item_id, " + params
            sql = f"INSERT INTO catalog_items ({cols}) VALUES ({params}) RETURNING *"
            return dict(connection.execute(text(sql), data).mappings().one())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/catalog-items/{item_id}")
def update_catalog_item(item_id: int, payload: dict = Body(...)):
    data = _clean("catalog_items", "item_id", payload)
    sets = ", ".join(f"{k} = :{k}" for k in data)
    sql = f"UPDATE catalog_items SET {sets} WHERE item_id = :item_id_ RETURNING *"
    try:
        with engine.begin() as connection:
            row = connection.execute(text(sql), {**data, "item_id_": item_id}).mappings().first()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    if row is None:
        raise HTTPException(status_code=404, detail="El equipo no existe.")
    return dict(row)