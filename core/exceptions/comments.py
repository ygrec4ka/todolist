from . import NotFoundException, AccessDeniedException


class CommentNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(detail="Comment not found")


class CommentAccessDeniedException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="Access denied to comment")
