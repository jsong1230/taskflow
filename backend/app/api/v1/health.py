from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """서버 상태 확인"""
    return HealthResponse(status="ok", message="TaskFlow API is running")


@router.get("/db", response_model=HealthResponse)
async def health_check_db(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """데이터베이스 연결 상태 확인"""
    await db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", message="Database connection is healthy")
