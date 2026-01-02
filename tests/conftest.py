import base64
import sys
import types
from io import BytesIO

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.session import get_db


class StubModel:
    def __init__(self) -> None:
        self.last_params = None

    def forward_text(self, payload):
        if payload.get("fail"):
            raise ModelError("model failed")
        return {
            "label": "stub",
            "score": 0.5,
            "echo": payload.get("text"),
        }

    def forward_image(self, image_bytes, params):
        if params.get("fail"):
            raise ModelError("model failed")
        self.last_params = params
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return {
            "label": "stub",
            "score": 0.5,
            "text": "ok",
            "lines": [{"text": "ok", "score": 0.9}],
            "image_base64": encoded,
        }


class ModelError(Exception):
    pass


_stub_module = types.ModuleType("app.services.ocr_model")
_stub_module.ModelError = ModelError
_stub_module.model = StubModel()
sys.modules["app.services.ocr_model"] = _stub_module

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app.db.base import Base
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite+pysqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(client):
    response = client.post(
        "/auth/token",
        data={"username": settings.admin_user, "password": settings.admin_password},
    )
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def stub_model(monkeypatch):
    stub = _stub_module.model
    stub.last_params = None
    return stub


@pytest.fixture()
def sample_image_bytes():
    image = Image.new("RGB", (8, 6), color=(255, 255, 255))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
