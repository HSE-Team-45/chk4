from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
TOKEN_TYPE = "access"


class User:
    def __init__(self, username: str, is_admin: bool) -> None:
        self.username = username
        self.is_admin = is_admin


class TokenData:
    def __init__(self, username: str, is_admin: bool) -> None:
        self.username = username
        self.is_admin = is_admin


def authenticate_user(username: str, password: str) -> Optional[User]:
    if username == settings.admin_user and password == settings.admin_password:
        return User(username=username, is_admin=True)
    return None


def create_access_token(username: str, is_admin: bool) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_exp_minutes)
    to_encode = {
        "sub": username,
        "admin": is_admin,
        "iat": now,
        "exp": expire,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "type": TOKEN_TYPE,
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
        if payload.get("type") != TOKEN_TYPE:
            raise credentials_exception
        username: str = payload.get("sub")
        is_admin: bool = bool(payload.get("admin"))
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    return User(username=username, is_admin=is_admin)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin only")
    return user
