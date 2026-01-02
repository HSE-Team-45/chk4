from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.core.config import settings
from app.db.session import get_db
from app.models.history import RequestHistory
from app.schemas.history import HistoryItem

router = APIRouter(prefix="/history", tags=["history"])


def _require_delete_token(confirm_token: str | None) -> None:
    if confirm_token != settings.delete_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")


@router.get("", response_model=list[HistoryItem])
def get_history(db: Session = Depends(get_db), _user=Depends(require_admin)):
    return db.execute(select(RequestHistory).order_by(RequestHistory.id)).scalars().all()


@router.delete("")
def delete_history(
    db: Session = Depends(get_db),
    confirm_token: str | None = Header(default=None, alias="X-Confirm-Token"),
    _user=Depends(require_admin),
):
    _require_delete_token(confirm_token)
    db.execute(delete(RequestHistory))
    db.commit()
    return {"status": "deleted"}
