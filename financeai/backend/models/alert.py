from pydantic import BaseModel
from typing import Optional
from datetime import date


class AlertResponse(BaseModel):
    id: str
    message: str
    level: str  # 'warning' | 'danger'
    due_date: Optional[date] = None
    amount: Optional[float] = None
    source: str  # 'transaction' | 'invoice'
