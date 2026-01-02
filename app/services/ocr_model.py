import base64
from io import BytesIO
from typing import Any

import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

from app.core.config import settings


class ModelError(Exception):
    pass


def _parse_ocr_result(ocr_result: Any) -> list[dict[str, Any]]:
    if not ocr_result:
        return []

    lines_data = ocr_result
    if isinstance(ocr_result, list) and ocr_result and isinstance(ocr_result[0], list):
        if ocr_result and ocr_result[0] and isinstance(ocr_result[0][0], list):
            lines_data = ocr_result[0]

    lines: list[dict[str, Any]] = []
    for line in lines_data or []:
        if isinstance(line, dict):
            text = line.get("text")
            score = line.get("score")
            if text is not None and score is not None:
                lines.append({"text": text, "score": float(score)})
            continue
        if not isinstance(line, list) or len(line) < 2:
            continue
        text_info = line[1]
        if isinstance(text_info, dict):
            text = text_info.get("text")
            score = text_info.get("score")
            if text is not None and score is not None:
                lines.append({"text": text, "score": float(score)})
            continue
        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
            text, score = text_info[0], text_info[1]
            lines.append({"text": text, "score": float(score)})
    return lines


class OCRModel:
    def __init__(self) -> None:
        self.ocr = PaddleOCR(use_angle_cls=True, lang=settings.ocr_lang)

    def forward_text(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("fail"):
            raise ModelError("model failed")
        text = payload.get("text")
        if text is None:
            raise ValueError("missing text")
        return {
            "label": "ocr-text",
            "score": 0.5,
            "echo": text,
        }

    def forward_image(self, image_bytes: bytes, params: dict[str, Any]) -> dict[str, Any]:
        if params.get("fail"):
            raise ModelError("model failed")
        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image)
            ocr_result = self.ocr.ocr(image_array, cls=True)
            lines = _parse_ocr_result(ocr_result)
        except Exception as exc:
            raise ModelError("model failed") from exc

        output = BytesIO()
        image.save(output, format="PNG")
        encoded = base64.b64encode(output.getvalue()).decode("ascii")
        text = " ".join([line["text"] for line in lines])
        return {
            "label": "ocr",
            "score": 0.5,
            "text": text,
            "lines": lines,
            "image_base64": encoded,
        }


model = OCRModel()
