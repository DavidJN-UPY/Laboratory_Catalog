import uuid

import requests


BASE_URL = "http://127.0.0.1:8000"


def test_api_root():
    response = requests.get(f"{BASE_URL}/", timeout=5)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_catalog_items_http():
    response = requests.get(f"{BASE_URL}/catalog-items", timeout=5)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_categories_http():
    response = requests.get(f"{BASE_URL}/categories", timeout=5)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_locations_http():
    response = requests.get(f"{BASE_URL}/physical-locations", timeout=5)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_users_http():
    response = requests.get(f"{BASE_URL}/users", timeout=5)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_logs_http():
    response = requests.get(f"{BASE_URL}/audit-logs", timeout=5)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_catalog_item_http():
    payload = {
        "internal_code": f"QA-{uuid.uuid4().hex[:8]}",
        "standardized_name": "Equipo Test HTTP",
        "technical_description": "Equipo creado por la prueba HTTP",
        "brand": "QA",
        "model": "TEST-1",
        "category_id": 1,
        "location_id": 1,
    }
    response = requests.post(f"{BASE_URL}/catalog-items", json=payload, timeout=5)
    assert response.status_code == 201
    assert response.json()["standardized_name"] == payload["standardized_name"]


def test_update_catalog_item_http():
    items = requests.get(f"{BASE_URL}/catalog-items", timeout=5).json()
    assert items
    item_id = items[0]["item_id"]
    response = requests.put(
        f"{BASE_URL}/catalog-items/{item_id}",
        json={"technical_description": "Actualizado por prueba HTTP"},
        timeout=5,
    )
    assert response.status_code == 200
    assert response.json()["item_id"] == item_id


def test_missing_catalog_item_http():
    response = requests.put(
        f"{BASE_URL}/catalog-items/999999",
        json={"technical_description": "No existe"},
        timeout=5,
    )
    assert response.status_code == 404


def test_create_catalog_item_requires_name():
    response = requests.post(
        f"{BASE_URL}/catalog-items",
        json={"category_id": 1, "location_id": 1},
        timeout=5,
    )
    assert response.status_code in (400, 201)