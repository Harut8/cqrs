from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError

from app.helpers.exceptions import (
    AuthenticationFailedError,
    JWTExpiredSignatureError,
    JWTInvalidTokenError,
    JWTTokenError,
)
from app.settings import APP_SETTINGS

JWT_SECRET = APP_SETTINGS.JWT.JWT_ACCESS_SECRET
ALGORITHM = APP_SETTINGS.JWT.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = REFRESH_TOKEN_EXPIRE_DAYS = APP_SETTINGS.JWT.VERIFICATION_MINUTES
AES_KEY = APP_SETTINGS.WIDGET.ENCRYPTION_KEY


def jwt_exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ExpiredSignatureError:
            raise JWTExpiredSignatureError
        except InvalidTokenError:
            raise JWTInvalidTokenError
        except PyJWTError:
            raise JWTTokenError
        except Exception as ex:
            # Exception unrelated to JWT
            raise AuthenticationFailedError from ex

    return wrapper


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt_encode(to_encode)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


@jwt_exception_handler
def jwt_decode(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])


@jwt_exception_handler
def jwt_encode(data: dict):
    return jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)


def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
