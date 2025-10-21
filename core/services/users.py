from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from core.schemas.users import UserUpdate

from core.models import User


class UserService:
    @staticmethod
    async def get_user(
        user_id: int,
        session: AsyncSession,
    ) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result: Result = await session.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(
        user: User,
        data: UserUpdate,
        session: AsyncSession,
    ) -> User:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete_user(
        user: User,
        session: AsyncSession,
    ) -> None:
        await session.delete(user)
        await session.commit()


user_services = UserService()
