from datetime import datetime
from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    created_at: datetime
    method: str
    route: str
    status_code: int
    duration_ms: int
    input_type: str
    text_length: int | None
    token_count: int | None
    image_width: int | None
    image_height: int | None
    payload_json: str | None
    header_params: str | None
    error_message: str | None

    class Config:
        from_attributes = True
