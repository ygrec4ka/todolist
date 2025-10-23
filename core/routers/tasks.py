from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies.users import get_current_user
from core.models import User
from core.models.db_helper import db_helper
from core.schemas.tasks import TaskResponse, TaskCreate, TaskUpdate
from core.services.tasks import task_services

router = APIRouter(prefix=settings.prefix.tasks, tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_create: TaskCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Создаем task
    task = await task_services.create_task(
        task_create=task_create,
        session=session,
        current_user=current_user,
    )

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Получаем конкретную task
    task = await task_services.get_task(
        task_id=task_id,
        session=session,
        current_user=current_user,
    )

    return task


@router.get("/", response_model=list[TaskResponse])
async def get_all_tasks(
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Получаем все user tasks
    tasks = await task_services.get_all_tasks(
        session=session,
        current_user=current_user,
    )

    return tasks


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Обновляем task
    task = await task_services.update_task(
        task_id=task_id,
        task_update=task_update,
        session=session,
        current_user=current_user,
    )

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Удаляем task
    await task_services.delete_task(
        task_id=task_id,
        session=session,
        current_user=current_user,
    )

    return {"message": "Task deleted successfully"}
