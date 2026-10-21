from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_session

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict:
    """Basic application health check."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/db")
async def health_check_db(session: AsyncSession = Depends(get_session)) -> dict:
    """Database connectivity health check."""
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar_one()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}