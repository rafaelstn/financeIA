from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class InvestmentCreate(BaseModel):
    name: str
    type: str
    institution: str
    invested_amount: float
    current_amount: float
    start_date: date
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class InvestmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    institution: Optional[str] = None
    invested_amount: Optional[float] = None
    current_amount: Optional[float] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class InvestmentResponse(BaseModel):
    id: str
    name: str
    type: str
    institution: str
    invested_amount: float
    current_amount: float
    start_date: date
    maturity_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
