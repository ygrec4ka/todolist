from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies.users import get_current_user
from core.models import User
from core.services.users import user_services
from core.models.db_helper import db_helper
from core.schemas.users import UserUpdate, UserResponse

from fastapi import status

router = APIRouter(
    prefix=settings.prefix.users,
    tags=["Users"],
)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    # Получаем auth user
    return current_user


@router.patch(
    "/me/profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Обновляем user
    user = await user_services.update_user(
        current_user=current_user,
        data=data,
        session=session,
    )

    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # Удаляем user
    await user_services.delete_user(
        current_user=current_user,
        session=session,
    )

    return {"message": "User deleted successfully"}
