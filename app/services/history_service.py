import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.history import RequestHistory


def record_history(
    db: Session,
    *,
    method: str,
    route: str,
    status_code: int,
    duration_ms: int,
    input_type: str,
    text_length: int | None = None,
    token_count: int | None = None,
    image_width: int | None = None,
    image_height: int | None = None,
    payload: dict[str, Any] | None = None,
    header_params: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> None:
    payload_json = json.dumps(payload, ensure_ascii=True) if payload is not None else None
    header_json = json.dumps(header_params, ensure_ascii=True) if header_params else None
    item = RequestHistory(
        method=method,
        route=route,
        status_code=status_code,
        duration_ms=duration_ms,
        input_type=input_type,
        text_length=text_length,
        token_count=token_count,
        image_width=image_width,
        image_height=image_height,
        payload_json=payload_json,
        header_params=header_json,
        error_message=error_message,
    )
    db.add(item)
    db.commit()
