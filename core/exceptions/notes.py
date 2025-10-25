from . import NotFoundException, AccessDeniedException


class NoteNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(detail="Note not found")


class NoteAccessDeniedException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="Access denied to note")
