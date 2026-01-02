from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise _unauthorized()
    token = create_access_token(user.username, user.is_admin)
    return {"access_token": token, "token_type": "bearer"}
