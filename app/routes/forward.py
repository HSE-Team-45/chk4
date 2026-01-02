import json
import time
from io import BytesIO
from typing import Any

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
from PIL import Image
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.history_service import record_history
from app.services.ocr_model import ModelError, model

router = APIRouter()
BAD_REQUEST = PlainTextResponse("bad request", status_code=400)
MODEL_FAILED = PlainTextResponse(
    "модель не смогла обработать данные", status_code=403)


def _token_count(text: str) -> int:
    return len(text.split())


def _duration_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def _record(
    db: Session,
    *,
    status_code: int,
    duration_ms: int,
    input_type: str,
    text: str | None = None,
    image_size: tuple[int, int] | None = None,
    payload: dict[str, Any] | None = None,
    header_params: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> None:
    text_length = len(text) if text is not None else None
    token_count = _token_count(text) if text is not None else None
    image_width = image_size[0] if image_size is not None else None
    image_height = image_size[1] if image_size is not None else None
    record_history(
        db,
        method="POST",
        route="/forward",
        status_code=status_code,
        duration_ms=duration_ms,
        input_type=input_type,
        text_length=text_length,
        token_count=token_count,
        image_width=image_width,
        image_height=image_height,
        payload=payload,
        header_params=header_params,
        error_message=error_message,
    )


def _extract_header_params(request: Request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    raw = request.headers.get("x-params")
    if raw:
        try:
            params.update(json.loads(raw))
        except json.JSONDecodeError:
            params["x-params"] = raw
    for key, value in request.headers.items():
        if key.lower().startswith("x-param-"):
            params[key[8:]] = value
    return params


@router.post("/forward")
async def forward(request: Request, db: Session = Depends(get_db)):
    start = time.perf_counter()
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("application/json"):
        return await _handle_json(request, db, start)

    if content_type.startswith("multipart/form-data"):
        return await _handle_multipart(request, db, start)

    return BAD_REQUEST


async def _handle_json(request: Request, db: Session, start: float):
    try:
        payload = await request.json()
    except Exception:
        return BAD_REQUEST

    if not isinstance(payload, dict):
        return BAD_REQUEST

    text = payload.get("text")
    if text is None or not isinstance(text, str):
        return BAD_REQUEST

    try:
        result = model.forward_text(payload)
        _record(
            db,
            status_code=200,
            duration_ms=_duration_ms(start),
            input_type="json",
            text=text,
            payload=payload,
        )
        return JSONResponse(result)
    except ModelError:
        _record(
            db,
            status_code=403,
            duration_ms=_duration_ms(start),
            input_type="json",
            text=text,
            payload=payload,
            error_message="model failed",
        )
        return MODEL_FAILED
    except Exception:
        _record(
            db,
            status_code=400,
            duration_ms=_duration_ms(start),
            input_type="json",
            text=text,
            payload=payload,
            error_message="bad request",
        )
        return BAD_REQUEST


async def _handle_multipart(request: Request, db: Session, start: float):
    form = await request.form()
    file: UploadFile | None = form.get("image")
    if file is None:
        return BAD_REQUEST

    image_bytes = await file.read()
    try:
        image = Image.open(BytesIO(image_bytes))
        image.verify()
        image = Image.open(BytesIO(image_bytes))
        image_size = image.size
    except Exception:
        return BAD_REQUEST

    header_params = _extract_header_params(request)
    payload = {"filename": file.filename}

    try:
        result = model.forward_image(image_bytes, header_params)
        _record(
            db,
            status_code=200,
            duration_ms=_duration_ms(start),
            input_type="image",
            image_size=image_size,
            payload=payload,
            header_params=header_params,
        )
        return JSONResponse(result)
    except ModelError:
        _record(
            db,
            status_code=403,
            duration_ms=_duration_ms(start),
            input_type="image",
            image_size=image_size,
            payload=payload,
            header_params=header_params,
            error_message="model failed",
        )
        return MODEL_FAILED
    except Exception:
        _record(
            db,
            status_code=400,
            duration_ms=_duration_ms(start),
            input_type="image",
            image_size=image_size,
            payload=payload,
            header_params=header_params,
            error_message="bad request",
        )
        return BAD_REQUEST
