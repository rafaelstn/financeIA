from pydantic import BaseModel, field_validator
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

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('description')
    @classmethod
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Descricao nao pode ser vazia')
        return v.strip()


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('description')
    @classmethod
    def description_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Descricao nao pode ser vazia')
        return v.strip() if v else v


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
