import uuid
from datetime import datetime, timedelta
from typing import Optional
from datetime import timezone

from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from core.models import User, RefreshToken
from core.schemas.auth import TokenPair

from core.exceptions.auth import (
    InvalidCredentialsException,
    TokenInvalidException,
    TokenExpiredException,
    TokenTypeException,
    RefreshTokenRevokedException,
)
from core.exceptions.users import (
    UserNotFoundException,
    UserNotActiveException,
    UserAlreadyExistsException,
)

from auth.hashing import hashing_password
from auth.jwt_manager import jwt_manager

from starlette.concurrency import run_in_threadpool


class AuthService:

    @staticmethod
    async def authenticate_user(
        username: str,
        password: str,
        session: AsyncSession,
    ) -> Optional[User]:
        try:
            stmt = select(User).where(User.username == username)
            result: Result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise InvalidCredentialsException()

            if not user.is_active:
                raise UserNotActiveException()

            is_valid = await run_in_threadpool(
                hashing_password.validate_password, password, user.hashed_password
            )
            if not is_valid:
                raise InvalidCredentialsException()

            return user

        except (InvalidCredentialsException, UserNotActiveException):
            raise
        except Exception:
            # Логируем неожиданные ошибки
            raise InvalidCredentialsException()

    @staticmethod
    async def register_user(
        email: str,
        username: str,
        password: str,
        session: AsyncSession,
    ) -> User:
        try:
            stmt = select(User).where(
                (User.username == username) | (User.email == email)
            )
            result: Result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise UserAlreadyExistsException()

            hashed_password = await run_in_threadpool(
                hashing_password.hash_password, password
            )
            user = User(email=email, username=username, hashed_password=hashed_password)

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

        except UserAlreadyExistsException:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            # Логируем ошибку
            raise UserAlreadyExistsException()

    @staticmethod
    async def create_tokens(
        user: User,
        session: AsyncSession,
    ) -> TokenPair:
        try:
            current_time = datetime.now(timezone.utc)
            expires_at = current_time + timedelta(
                days=settings.auth_jwt.refresh_token_expire_days
            )

            access_payload = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "jti": str(uuid.uuid4()),
                "type": "access",
                "iai": current_time.timestamp(),
            }

            refresh_payload = {
                "sub": str(user.id),
                "jti": str(uuid.uuid4()),
                "type": "refresh",
                "iai": current_time.timestamp(),
            }

            access_token = jwt_manager.create_access_token(access_payload)
            refresh_token = jwt_manager.create_refresh_token(refresh_payload)

            # Сохраняем refresh token в базу данных
            refresh_token_record = RefreshToken(
                jti=refresh_payload["jti"],
                user_id=user.id,
                expires_at=expires_at,
            )

            session.add(refresh_token_record)
            await session.commit()

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
            )

        except Exception:
            await session.rollback()
            # Логируем ошибку создания токенов
            raise TokenInvalidException()

    @staticmethod
    async def refresh_token(
        refresh_token: str,
        session: AsyncSession,
    ) -> TokenPair:
        try:
            # Проверяем подпись и валидность refresh token
            payload = jwt_manager.verify_refresh_token(refresh_token)

            if payload.get("type") != "refresh":
                raise TokenTypeException("Expected refresh token")

            jti = payload.get("jti")
            if jti:
                stmt = select(RefreshToken).where(
                    (RefreshToken.jti == jti) & (RefreshToken.revoke == True)
                )
                result: Result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    raise RefreshTokenRevokedException()

            # Получаем пользователя
            user_id = int(payload["sub"])
            user = await session.get(User, user_id)

            if not user:
                raise UserNotFoundException()
            if not user.is_active:
                raise UserNotActiveException()

            return await AuthService.create_tokens(user, session)

        except (
            TokenExpiredException,
            TokenInvalidException,
            TokenTypeException,
            RefreshTokenRevokedException,
            UserNotFoundException,
            UserNotActiveException,
        ):
            raise
        except Exception:
            # Логируем неожиданные ошибки
            raise TokenInvalidException()

    @staticmethod
    async def logout_user(
        user: User,
        refresh_token: str | None,
        session: AsyncSession,
    ) -> dict:
        try:
            if refresh_token:
                payload = jwt_manager.verify_refresh_token(refresh_token)
                jti = payload.get("jti")

                if jti:
                    # Находим запись refresh токена в базе
                    stmt = select(RefreshToken).where(
                        (RefreshToken.jti == jti) & (RefreshToken.user_id == user.id)
                    )
                    result: Result = await session.execute(stmt)
                    refresh_token_record = result.scalar_one_or_none()

                    if refresh_token_record:
                        # Помечаем как отозванный
                        refresh_token_record.revoke = True
                        await session.commit()

            return {"message": "Logged out successfully"}

        except (TokenExpiredException, TokenInvalidException):
            # Если токен невалидный, все равно считаем логаут успешным. Логируем ошибку
            return {"message": "Logged out successfully"}

    @staticmethod
    async def logout_all_devices(
        user: User,
        session: AsyncSession,
    ) -> dict:
        try:
            stmt = select(RefreshToken).where(
                (RefreshToken.user_id == user.id) & (RefreshToken.revoke == False)
            )
            result: Result = await session.execute(stmt)
            active_tokens = result.scalars().all()

            for token in active_tokens:
                token.revoke = True

            await session.commit()

            return {"message": "Logged out from all devices successfully"}

        except Exception:
            await session.rollback()
            # Логируем ошибку
            raise


auth_services = AuthService()
