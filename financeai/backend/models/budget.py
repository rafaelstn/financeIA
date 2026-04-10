from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float
    is_active: bool = True

    @field_validator('monthly_limit')
    @classmethod
    def limit_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Limite deve ser maior que zero')
        return v


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
