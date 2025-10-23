from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies.users import get_current_user
from core.models import User
from core.models.db_helper import db_helper
from core.schemas.comments import CommentCreate, CommentResponse, CommentUpdate
from core.services.comments import comment_services


router = APIRouter(prefix=settings.prefix.comments, tags=["Comments"])


@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
async def create_comments_for_task(
    task_id: int,
    comment_data: CommentCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Автоматически привязываем comment к task
    comment_create = CommentCreate(
        content=comment_data.content,
        task_id=task_id,
        note_id=None,
    )

    comment = await comment_services.create_comment(
        comment_create=comment_create,
        session=session,
        current_user=current_user,
    )

    return comment


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_task_comments(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Получаем все task comments
    comments = await comment_services.get_task_comments(
        task_id=task_id,
        session=session,
        current_user=current_user,
    )

    return comments


@router.post("/notes/{note_id}/comments", response_model=CommentResponse)
async def create_comment_for_note(
    note_id: int,
    comment_data: CommentCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Автоматически привязываем comment к note
    comment_create = CommentCreate(
        content=comment_data.content,
        task_id=None,
        note_id=note_id,
    )

    comment = await comment_services.create_comment(
        comment_create=comment_create,
        session=session,
        current_user=current_user,
    )

    return comment


@router.get("/notes/{note_id}/comments", response_model=list[CommentResponse])
async def get_note_comments(
    note_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Получаем все note comments
    comments = await comment_services.get_note_comments(
        note_id=note_id,
        session=session,
        current_user=current_user,
    )

    return comments


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Обновляем comment
    comment = await comment_services.update_comment(
        comment_id=comment_id,
        comment_update=comment_update,
        session=session,
        current_user=current_user,
    )

    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Удаляем comment
    await comment_services.delete_comment(
        comment_id=comment_id,
        session=session,
        current_user=current_user,
    )

    return {"message": "Comment deleted successfully"}
