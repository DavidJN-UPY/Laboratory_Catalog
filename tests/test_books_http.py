import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_catalog_item():
    payload = {
        "standardized_name": "Equipo Test",
        "category_id": 1,
        "location_id": 1
    }

    response = requests.post(
        f"{BASE_URL}/catalog-items",
        json=payload,
        timeout=5
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    assert response.status_code in (200, 201)