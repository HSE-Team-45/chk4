import base64


def test_forward_json_success(client, stub_model):
    response = client.post("/forward", json={"text": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "stub"
    assert data["echo"] == "hello"


def test_forward_json_bad_request(client):
    response = client.post("/forward", json={"message": "no text"})
    assert response.status_code == 400
    assert response.text == "bad request"


def test_forward_json_model_failed(client, stub_model):
    response = client.post("/forward", json={"text": "hello", "fail": True})
    assert response.status_code == 403
    assert response.text == "модель не смогла обработать данные"


def test_forward_image_success(client, stub_model, sample_image_bytes):
    response = client.post(
        "/forward",
        files={"image": ("sample.png", sample_image_bytes, "image/png")},
        headers={"X-Params": '{"foo": "bar"}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "stub"
    assert "image_base64" in data
    assert base64.b64decode(data["image_base64"])


def test_forward_image_bad_request(client):
    response = client.post("/forward", files={})
    assert response.status_code == 400
    assert response.text == "bad request"


def test_forward_image_model_failed(client, stub_model, sample_image_bytes):
    response = client.post(
        "/forward",
        files={"image": ("sample.png", sample_image_bytes, "image/png")},
        headers={"X-Params": '{"fail": true}'},
    )
    assert response.status_code == 403
    assert response.text == "модель не смогла обработать данные"
