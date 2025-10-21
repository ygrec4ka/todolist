from fastapi import Request, HTTPException, status
from fastapi.params import Depends
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt_manager import jwt_manager
from core.models import User
from core.models.db_helper import db_helper


async def get_current_user_from_cookie(
    request: Request,
) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = jwt_manager.verify_access_token(token)
    if payload.get("type") != "access":
        raise InvalidTokenError("Not an access token")

    if "sub" not in payload:
        raise InvalidTokenError("Missing 'sub' in token")

    return payload


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    payload = await get_current_user_from_cookie(request)
    user_id = int(payload["sub"])

    user: User | None = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
