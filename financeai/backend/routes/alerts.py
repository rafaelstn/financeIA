from fastapi import APIRouter
from services.alert_service import get_active_alerts

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/")
async def list_alerts():
    return get_active_alerts()
