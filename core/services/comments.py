from typing import Sequence

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from core.models import Comment, User, Task, Note
from core.schemas.comments import CommentCreate, CommentUpdate


class CommentServices:
    @staticmethod
    async def create_comment(
        comment_create: CommentCreate,
        session: AsyncSession,
        current_user: User,
    ):
        try:
            if not comment_create.task_id and not comment_create.note_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Comment must be attached to a task or note",
                )

            if comment_create.task_id:
                task = await session.get(Task, comment_create.task_id)
                if not task:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Task note found",
                    )

            if comment_create.note_id:
                note = await session.get(Note, comment_create.note_id)
                if not note:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Note note found",
                    )

            comment = Comment(
                **comment_create.model_dump(),
                user_id=current_user.id,
            )

            session.add(comment)
            await session.commit()
            await session.refresh(comment)

            return comment

        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Comment creation failed. Please try again",
            )

    @staticmethod
    async def get_task_comments(
        task_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[Comment]:
        task = await session.get(Task, task_id)
        # Проверяем что задача существует и принадлежит пользователю
        if not task or task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        stmt = (
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())  # Сортируем по дате
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
        # Проверяем что записка существует и принадлежит пользователю
        if not note or note.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )

        stmt = (
            select(Comment)
            .where(Comment.note_id == note_id)
            .order_by(Comment.created_at.asc())  # Сортируем по дате
        )
        result: Result = await session.execute(stmt)

        return result.scalars().all()

    @staticmethod
    async def get_comment(
        comment_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Comment:
        stmt = select(Comment).where(
            Comment.id == comment_id,
            Comment.user_id == current_user.id,
        )
        result: Result = await session.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )

        return comment

    @staticmethod
    async def update_comment(
        comment_id: int,
        comment_update: CommentUpdate,
        session: AsyncSession,
        current_user: User,
    ) -> Comment:
        # Получаем комментарий (проверяем что он существует и принадлежит пользователю)
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
