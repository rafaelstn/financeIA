from pydantic import BaseModel, field_validator
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
    next_due_date: Optional[date] = None
    use_business_day: bool = False
    business_day_number: Optional[int] = None  # e.g., 5 = 5th business day
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('business_day_number')
    @classmethod
    def business_day_valid_range(cls, v):
        if v is not None and (v < 1 or v > 23):
            raise ValueError('Dia util deve ser entre 1 e 23')
        return v


class RecurringUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    day_of_month: Optional[int] = None
    is_active: Optional[bool] = None
    next_due_date: Optional[date] = None
    use_business_day: Optional[bool] = None
    business_day_number: Optional[int] = None
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
    use_business_day: bool = False
    business_day_number: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
