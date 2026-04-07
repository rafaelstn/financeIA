from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TransactionCreate(BaseModel):
    description: str
    amount: float
    type: str  # 'income' | 'expense'
    category: str
    status: str = "pending"
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    description: str
    amount: float
    type: str
    category: str
    status: str
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
