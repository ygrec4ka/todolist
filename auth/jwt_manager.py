from datetime import timedelta, datetime, timezone

import jwt
from jwt import PyJWTError

from core.config import settings


class JwtManager:
    # Кодируем токен доступа (кодирование, encode)
    @staticmethod
    def create_access_token(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    ) -> str:
        now = datetime.now(timezone.utc)

        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)

        to_encode = payload.copy()
        to_encode.update(
            exp=expire,
            iat=now,
            type="access",
        )
        encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)

        return encoded

    # Декодируем токен доступа (проверка, валидация)
    @staticmethod
    def verify_access_token(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ) -> dict:
        access = jwt.decode(token, public_key, algorithms=[algorithm])
        if access.get("type") != "access":
            raise PyJWTError("Invalid token type: expected access token")

        return access

    @staticmethod
    def create_refresh_token(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_days: int = settings.auth_jwt.refresh_token_expire_days,
    ) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=expire_days)

        jwt_payload = payload.copy()
        jwt_payload.update(
            exp=expire,
            iat=now,
            type="refresh",
        )

        return jwt.encode(jwt_payload, private_key, algorithm)

    @staticmethod
    def verify_refresh_token(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ) -> dict:
        refresh = jwt.decode(token, public_key, algorithms=[algorithm])
        if refresh.get("type") != "refresh":
            raise PyJWTError("Invalid token type: expected refresh token")

        return refresh


jwt_manager = JwtManager()
