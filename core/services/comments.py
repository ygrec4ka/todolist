from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from core.models import Comment, User, Task, Note
from core.schemas.comments import CommentCreate, CommentUpdate
from core.exceptions.comments import (
    CommentNotFoundException,
    CommentAccessDeniedException,
)
from core.exceptions.tasks import TaskNotFoundException
from core.exceptions.notes import NoteNotFoundException
from core.exceptions import ValidationException


class CommentServices:
    @staticmethod
    async def create_comment(
        comment_create: CommentCreate,
        session: AsyncSession,
        current_user: User,
        task_id: int | None = None,
        note_id: int | None = None,
    ) -> Comment:
        try:
            # Проверяем что передан ровно один ID
            if not task_id and not note_id:
                raise ValidationException("Comment must be attached to a task or note")

            if task_id and note_id:
                raise ValidationException(
                    "Comment can only be attached to either a task or note, not both"
                )

            # Проверяем существование задачи или заметки
            if task_id:
                task = await session.get(Task, task_id)
                if not task:
                    raise TaskNotFoundException()
                if task.user_id != current_user.id:
                    raise CommentAccessDeniedException()

            if note_id:
                note = await session.get(Note, note_id)
                if not note:
                    raise NoteNotFoundException()
                if note.user_id != current_user.id:
                    raise CommentAccessDeniedException()

            comment = Comment(
                content=comment_create.content,
                task_id=task_id,
                note_id=note_id,
                user_id=current_user.id,
            )

            session.add(comment)
            await session.commit()
            await session.refresh(comment)

            return comment

        except (
            ValidationException,
            TaskNotFoundException,
            NoteNotFoundException,
            CommentAccessDeniedException,
        ):
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise ValidationException("Comment creation failed. Please try again")

    @staticmethod
    async def get_task_comments(
        task_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[Comment]:
        task = await session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException()
        if task.user_id != current_user.id:
            raise CommentAccessDeniedException()

        stmt = (
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
        )
        result: Result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_note_comments(
        note_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[Comment]:
        note = await session.get(Note, note_id)
        if not note:
            raise NoteNotFoundException()
        if note.user_id != current_user.id:
            raise CommentAccessDeniedException()

        stmt = (
            select(Comment)
            .where(Comment.note_id == note_id)
            .order_by(Comment.created_at.asc())
        )
        result: Result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_comment(
        comment_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Comment:
        stmt = select(Comment).where(Comment.id == comment_id)
        result: Result = await session.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            raise CommentNotFoundException()
        if comment.user_id != current_user.id:
            raise CommentAccessDeniedException()

        return comment

    @staticmethod
    async def update_comment(
        comment_id: int,
        comment_update: CommentUpdate,
        session: AsyncSession,
        current_user: User,
    ) -> Comment:
        comment = await CommentServices.get_comment(comment_id, session, current_user)

        for key, value in comment_update.model_dump(exclude_unset=True).items():
            setattr(comment, key, value)

        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def delete_comment(
        comment_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> None:
        comment = await CommentServices.get_comment(comment_id, session, current_user)
        await session.delete(comment)
        await session.commit()


comment_services = CommentServices()
