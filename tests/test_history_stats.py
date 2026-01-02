from app.core.config import settings

def test_history_flow(client, auth_headers, stub_model, sample_image_bytes):
    response = client.post("/forward", json={"text": "hello"})
    assert response.status_code == 200

    response = client.post(
        "/forward",
        files={"image": ("sample.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 200

    response = client.get("/history", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["route"] == "/forward"


def test_history_requires_auth(client):
    response = client.get("/history")
    assert response.status_code == 401


def test_history_delete_requires_token(client, auth_headers, stub_model):
    response = client.post("/forward", json={"text": "hello"})
    assert response.status_code == 200

    response = client.delete("/history", headers=auth_headers)
    assert response.status_code == 401


def test_history_delete_success(client, auth_headers, stub_model):
    response = client.post("/forward", json={"text": "hello"})
    assert response.status_code == 200

    response = client.delete(
        "/history",
        headers={**auth_headers, "X-Confirm-Token": settings.delete_token},
    )
    assert response.status_code == 200

    response = client.get("/history", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_stats(client, auth_headers, stub_model, sample_image_bytes):
    client.post("/forward", json={"text": "hello world"})
    client.post(
        "/forward",
        files={"image": ("sample.png", sample_image_bytes, "image/png")},
    )

    response = client.get("/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["durations_ms"]["count"] == 2
    assert data["text"]["count"] == 1
    assert data["images"]["count"] == 1
    assert data["durations_ms"]["p50"] is not None


def test_stats_requires_auth(client):
    response = client.get("/stats")
    assert response.status_code == 401
