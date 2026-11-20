from app.api.students import router as students_router
from app.api.attendance import router as attendance_router
from app.api.auth import router as auth_router

__all__ = ["students_router", "attendance_router", "auth_router"]
