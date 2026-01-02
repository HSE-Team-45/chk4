from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.db.session import get_db
from app.models.history import RequestHistory

router = APIRouter(prefix="/stats", tags=["stats"])


def _quantile(values: list[int], q: float) -> float | None:
    if not values:
        return None
    values_sorted = sorted(values)
    idx = int(round((len(values_sorted) - 1) * q))
    return float(values_sorted[idx])


def _mean(values: list[int]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


@router.get("")
def get_stats(db: Session = Depends(get_db), _user=Depends(require_admin)):
    items = db.execute(select(RequestHistory)).scalars().all()
    durations = [item.duration_ms for item in items if item.duration_ms is not None]

    text_lengths = [item.text_length for item in items if item.text_length is not None]
    token_counts = [item.token_count for item in items if item.token_count is not None]
    image_sizes = [
        {"width": item.image_width, "height": item.image_height}
        for item in items
        if item.image_width is not None and item.image_height is not None
    ]

    return {
        "durations_ms": {
            "mean": _mean(durations),
            "p50": _quantile(durations, 0.5),
            "p95": _quantile(durations, 0.95),
            "p99": _quantile(durations, 0.99),
            "count": len(durations),
        },
        "text": {
            "mean_length": _mean(text_lengths),
            "mean_tokens": _mean(token_counts),
            "count": len(text_lengths),
        },
        "images": {
            "sizes": image_sizes,
            "count": len(image_sizes),
        },
    }
