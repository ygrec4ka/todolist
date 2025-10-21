from fastapi import Response

from datetime import timedelta, datetime, timezone

import jwt

from core.config import settings


def set_jwt_cookie(
    response: Response,
    access_token: str,
    refresh_token: str,
    access_max_age: int = 60 * 15,  # 15 минут
    refresh_max_age: int = 60 * 60 * 24 * 30,  # 30 дней
):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=access_max_age,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=refresh_max_age,
    )
