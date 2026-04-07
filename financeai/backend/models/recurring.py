from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class RecurringCreate(BaseModel):
    description: str
    amount: float
    type: str  # income, expense
    category: str
    frequency: str = "monthly"  # monthly, weekly, yearly
    day_of_month: Optional[int] = None
    is_active: bool = True
    next_due_date: date
    notes: Optional[str] = None


class RecurringUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    day_of_month: Optional[int] = None
    is_active: Optional[bool] = None
    next_due_date: Optional[date] = None
    notes: Optional[str] = None


class RecurringResponse(BaseModel):
    id: str
    description: str
    amount: float
    type: str
    category: str
    frequency: str
    day_of_month: Optional[int] = None
    is_active: bool
    next_due_date: date
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
