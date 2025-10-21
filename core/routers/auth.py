from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form

from pydantic import EmailStr

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User
from core.models.db_helper import db_helper
from core.schemas.auth import TokenPair
from core.dependencies.users import get_current_user

from auth.services import auth_services
from auth.utils import set_jwt_cookie


router = APIRouter(
    prefix=settings.prefix.jwt,
    tags=["JWT"],
)


@router.post("/register")
async def registration_user(
    response: Response,  # Ответ
    email: Annotated[EmailStr, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Регистрируем пользователя по переданным cred.
    user = await auth_services.register_user(email, username, password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    # Создаем пару токенов для этого пользователя
    token_info = await auth_services.create_tokens(user, session)
    # Устанавливаем оба токена в Куки
    set_jwt_cookie(
        response,
        access_token=token_info.access_token,
        refresh_token=token_info.refresh_token,
    )
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenPair)
async def login_user(
    response: Response,  # Ответ
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Получаем АУТЕНТИФИЦИРОВАННОГО пользователя
    user = await auth_services.authenticate_user(username, password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаём пару токенов для данного пользователя
    token_pair = await auth_services.create_tokens(user, session)
    # Устанавливаем ОБА токена в Куки
    set_jwt_cookie(
        response,
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )

    return token_pair


@router.post("/refresh", response_model=TokenPair)
async def refresh_token_for_user(
    response: Response,
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Получаем refresh token из Кук
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    # Обновляем токены для пользователя
    token_pair = await auth_services.refresh_token(
        refresh_token=refresh_token,
        session=session,
    )
    # Устанавливаем ОБА токена в Куки
    set_jwt_cookie(
        response,
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )

    return token_pair


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Получаем refresh token из Кук
    refresh_token = request.cookies.get("refresh_token")
    # Вызываем из сервиса функцию logout
    result = await auth_services.logout_user(
        user=current_user,
        refresh_token=refresh_token,
        session=session,
    )
    # Удаляем Куки
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return result


@router.post("/logout-all")
async def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await auth_services.logout_all_devices(
        user=current_user,
        session=session,
    )
    # Удаляем Куки текущей сессии
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return result


@router.post("/change-password")
async def change_password():
    pass
