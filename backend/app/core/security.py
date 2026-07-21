from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(subject: UUID) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(subject), "exp": expires_at},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def get_token_subject(token: str = Depends(oauth2_scheme)) -> UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise AuthenticationError("Token has no subject")
        return UUID(subject)
    except (JWTError, ValueError) as exc:
        raise AuthenticationError("Invalid or expired access token") from exc
