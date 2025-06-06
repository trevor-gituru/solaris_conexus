# src/utils/exception_handlers.py
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Callable, TypeVar, Optional

from src.utils.logging import logger  # ✅ Import the logger

T = TypeVar("T")

class DBExceptionHandler:
    def __init__(self,
                 integrity_message: str = "Resource already exists",
                 general_message: str = "Internal server error",
                 conflict_message: str = "Conflict detected",
                 auth_fail_message: str = "Invalid credentials"):
        self.integrity_message = integrity_message
        self.general_message = general_message
        self.conflict_message = conflict_message
        self.auth_fail_message = auth_fail_message

    def handle(self, operation: Callable[[], T]) -> T:
        try:
            return operation()
        except IntegrityError as e:
            logger.warning(f"IntegrityError: {e}")
            raise HTTPException(status_code=400, detail=self.integrity_message)
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise HTTPException(status_code=500, detail=self.general_message)
        except Exception as e:
            message = f"Duplicate Error: {e}"
            logger.error(message)
            raise HTTPException(status_code=500, detail=message)


    def check_conflict(self, condition: Optional[T], message: Optional[str] = None):
        if condition:
            log_msg = message or self.conflict_message
            logger.info(f"Conflict detected: {log_msg}")
            raise HTTPException(status_code=400, detail=log_msg)

    def check_auth(self, condition: bool, message: Optional[str] = None):
        if not condition:
            raise HTTPException(status_code=400, detail=message or self.auth_fail_message)

    def check_user_authenticated(self, user: Optional[T], message: str = "User not found or authenticated"):
        if user is None:
            logger.warning(f"Authentication failed: {message}")
            raise HTTPException(status_code=401, detail=message)
    # Inside DBExceptionHandler class
    async def handle_async(self, operation: Callable[[], T], error_message: str = "Operation failed") -> T:
        try:
            return await operation()
        except Exception as e:
            logger.error(f"Async operation failed: {e}")
            raise HTTPException(status_code=500, detail=f"{error_message}: {str(e)}")


