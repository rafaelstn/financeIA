from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime


class DebtCreate(BaseModel):
    creditor: str
    original_amount: float
    current_amount: float
    category: str  # cartao, emprestimo, financiamento, cheque_especial, conta_consumo, outros
    status: str = "ativa"
    origin_date: date
    is_paying: bool = False
    monthly_payment: Optional[float] = None
    payment_day: Optional[int] = None
    total_installments: Optional[int] = None
    paid_installments: int = 0
    notes: Optional[str] = None

    @field_validator('original_amount', 'current_amount')
    @classmethod
    def amounts_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('creditor')
    @classmethod
    def creditor_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Credor nao pode ser vazio')
        return v.strip()


class DebtUpdate(BaseModel):
    creditor: Optional[str] = None
    original_amount: Optional[float] = None
    current_amount: Optional[float] = None
    category: Optional[str] = None
    status: Optional[str] = None
    origin_date: Optional[date] = None
    is_paying: Optional[bool] = None
    monthly_payment: Optional[float] = None
    payment_day: Optional[int] = None
    total_installments: Optional[int] = None
    paid_installments: Optional[int] = None
    notes: Optional[str] = None

    @field_validator('original_amount', 'current_amount')
    @classmethod
    def amounts_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('creditor')
    @classmethod
    def creditor_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Credor nao pode ser vazio')
        return v.strip() if v else v


class DebtResponse(BaseModel):
    id: str
    creditor: str
    original_amount: float
    current_amount: float
    category: str
    status: str
    origin_date: date
    is_paying: bool
    monthly_payment: Optional[float] = None
    payment_day: Optional[int] = None
    total_installments: Optional[int] = None
    paid_installments: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
