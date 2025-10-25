from fastapi import Request
from fastapi.params import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt_manager import jwt_manager
from core.models import User
from core.models.db_helper import db_helper
from core.exceptions.auth import (
    TokenInvalidException,
    TokenExpiredException,
    TokenTypeException,
)
from core.exceptions.users import UserNotFoundException


async def get_current_user_from_cookie(
    request: Request,
) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise TokenInvalidException("Missing access token")

    try:
        payload = jwt_manager.verify_access_token(token)

        if payload.get("type") != "access":
            raise TokenTypeException("Not an access token")

        if "sub" not in payload:
            raise TokenInvalidException("Missing 'sub' in token")

        return payload

    except TokenExpiredException:
        raise TokenExpiredException()
    except TokenInvalidException:
        raise TokenInvalidException()
    except Exception:
        raise TokenInvalidException()


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    try:
        payload = await get_current_user_from_cookie(request)
        user_id = int(payload["sub"])

        user: User | None = await session.get(User, user_id)
        if not user:
            raise UserNotFoundException()

        return user
    except (
        TokenInvalidException,
        TokenExpiredException,
        TokenTypeException,
        UserNotFoundException,
    ):
        raise
    except Exception:
        raise TokenInvalidException()
