from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from core.models import User
from core.schemas.tasks import TaskCreate, TaskUpdate
from core.models.tasks import Task
from core.exceptions.tasks import TaskNotFoundException, TaskAccessDeniedException
from core.exceptions import ValidationException


class TaskServices:
    @staticmethod
    async def create_task(
        task_create: TaskCreate,
        session: AsyncSession,
        current_user: User,
    ) -> Task:
        try:
            task = Task(
                **task_create.model_dump(),
                user_id=current_user.id,
            )

            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

        except Exception:
            await session.rollback()
            raise ValidationException("Task creation failed. Please try again")

    @staticmethod
    async def get_task(
        task_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Task:
        stmt = (
            select(Task).options(selectinload(Task.comments)).where(Task.id == task_id)
        )
        result: Result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise TaskNotFoundException()
        if task.user_id != current_user.id:
            raise TaskAccessDeniedException()

        return task

    @staticmethod
    async def get_all_tasks(
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[Task]:
        stmt = (
            select(Task)
            .where(Task.user_id == current_user.id)
            .order_by(Task.created_at.desc())
        )
        result: Result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_task(
        task_id: int,
        data: TaskUpdate,
        session: AsyncSession,
        current_user: User,
    ) -> Task:
        task = await TaskServices.get_task(task_id, session, current_user)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)

        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def delete_task(
        task_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> None:
        task = await TaskServices.get_task(task_id, session, current_user)
        await session.delete(task)
        await session.commit()


task_services = TaskServices()
