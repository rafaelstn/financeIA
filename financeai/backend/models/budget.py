from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float
    is_active: bool = True


class BudgetUpdate(BaseModel):
    category: Optional[str] = None
    monthly_limit: Optional[float] = None
    is_active: Optional[bool] = None


class BudgetResponse(BaseModel):
    id: str
    category: str
    monthly_limit: float
    is_active: bool
    created_at: Optional[datetime] = None
