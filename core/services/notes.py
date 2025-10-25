from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from core.models import User
from core.schemas.notes import NoteCreate, NoteUpdate
from core.models.notes import Note
from core.exceptions.notes import NoteNotFoundException, NoteAccessDeniedException
from core.exceptions import ValidationException


class NoteServices:
    @staticmethod
    async def create_note(
        note_create: NoteCreate,
        session: AsyncSession,
        current_user: User,
    ) -> Note:
        try:
            note = Note(
                **note_create.model_dump(),
                user_id=current_user.id,
            )

            session.add(note)
            await session.commit()
            await session.refresh(note)
            return note

        except Exception:
            await session.rollback()
            raise ValidationException("Note creation failed. Please try again")

    @staticmethod
    async def get_note(
        note_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> Note:
        stmt = (
            select(Note).options(selectinload(Note.comments)).where(Note.id == note_id)
        )
        result: Result = await session.execute(stmt)
        note = result.scalar_one_or_none()

        if not note:
            raise NoteNotFoundException()
        if note.user_id != current_user.id:
            raise NoteAccessDeniedException()

        return note

    @staticmethod
    async def get_all_notes(
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[Note]:
        stmt = (
            select(Note)
            .where(Note.user_id == current_user.id)
            .order_by(Note.created_at.desc())
        )
        result: Result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_note(
        note_id: int,
        data: NoteUpdate,
        session: AsyncSession,
        current_user: User,
    ) -> Note:
        note = await NoteServices.get_note(note_id, session, current_user)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(note, key, value)

        await session.commit()
        await session.refresh(note)
        return note

    @staticmethod
    async def delete_note(
        note_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> None:
        note = await NoteServices.get_note(note_id, session, current_user)
        await session.delete(note)
        await session.commit()


note_services = NoteServices()
