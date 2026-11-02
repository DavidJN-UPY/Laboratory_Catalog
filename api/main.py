from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from scripts.db_config import get_engine

app = FastAPI(
    title="Laboratory Catalog API",
    description="API de inventario para el laboratorio de PCB",
    version="1.0.0"
)

engine = get_engine()


@app.get("/")
def root():
    return {"message": "Servidor de Laboratory Catalog funcionando"}


@app.get("/categories")
def list_categories():
    query = text("SELECT * FROM categories ORDER BY category_id")
    try:
        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/physical-locations")
def list_physical_locations():
    query = text("SELECT * FROM physical_locations ORDER BY location_id")
    try:
        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users")
def list_users():
    query = text("SELECT * FROM users ORDER BY user_id")
    try:
        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/catalog-items")
def list_catalog_items():
    query = text("SELECT * FROM catalog_items ORDER BY item_id")
    try:
        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit-logs")
def list_audit_logs():
    query = text("SELECT * FROM audit_logs ORDER BY log_id DESC")
    try:
        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))