from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies.users import get_current_user
from core.models import User
from core.models.db_helper import db_helper
from core.schemas.notes import NoteResponse, NoteCreate, NoteUpdate
from core.services.notes import note_services

router = APIRouter(
    prefix=settings.prefix.notes,
    tags=["Notes"],
)


@router.post("/", response_model=NoteResponse)
async def create_note(
    note_create: NoteCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Создаем note
    note = await note_services.create_note(
        note_create=note_create,
        session=session,
        current_user=current_user,
    )

    return note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Получаем конкретную note
    note = await note_services.get_note(
        note_id=note_id,
        session=session,
        current_user=current_user,
    )

    return note


@router.get("/", response_model=list[NoteResponse])
async def get_all_notes(
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Получаем все user notes
    notes = await note_services.get_all_notes(
        session=session,
        current_user=current_user,
    )

    return notes


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Обновляем note
    note = await note_services.update_note(
        note_id=note_id,
        note_update=note_update,
        session=session,
        current_user=current_user,
    )

    return note


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(get_current_user),
):
    # Удаляем note
    await note_services.delete_note(
        note_id=note_id,
        session=session,
        current_user=current_user,
    )

    return {"message": "Note deleted successfully"}
