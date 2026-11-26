import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "api"))

from api.main import app


client = TestClient(app)


def test_root_returns_static_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "Laboratory Catalog API" in response.json()["info"]["title"]


def test_catalog_items_endpoint():
    response = client.get("/catalog-items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_categories_endpoint():
    response = client.get("/categories")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_locations_endpoint():
    response = client.get("/physical-locations")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_users_endpoint():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_logs_endpoint():
    response = client.get("/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_catalog_item():
    payload = {
        "standardized_name": "Equipo QA Client",
        "technical_description": "Prueba automatizada TestClient",
        "category_id": 1,
        "location_id": 1,
    }
    response = client.post("/catalog-items", json=payload)
    assert response.status_code == 201
    assert response.json()["standardized_name"] == payload["standardized_name"]


def test_update_existing_catalog_item():
    items = client.get("/catalog-items").json()
    assert items
    item_id = items[0]["item_id"]
    response = client.put(
        f"/catalog-items/{item_id}",
        json={"technical_description": "Actualizado por prueba automatizada"},
    )
    assert response.status_code == 200
    assert response.json()["item_id"] == item_id


def test_update_missing_catalog_item():
    response = client.put(
        "/catalog-items/999999",
        json={"technical_description": "No debe existir"},
    )
    assert response.status_code == 404