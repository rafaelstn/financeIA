from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class CreditCardCreate(BaseModel):
    name: str
    bank: str
    limit_amount: float
    closing_day: int
    due_day: int


class CreditCardUpdate(BaseModel):
    name: Optional[str] = None
    bank: Optional[str] = None
    limit_amount: Optional[float] = None
    closing_day: Optional[int] = None
    due_day: Optional[int] = None


class CreditCardResponse(BaseModel):
    id: str
    name: str
    bank: str
    limit_amount: float
    closing_day: int
    due_day: int
    created_at: Optional[datetime] = None


class CardInvoiceCreate(BaseModel):
    card_id: str
    month: int
    year: int
    total_amount: float = 0
    status: str = "open"
    due_date: Optional[date] = None


class CardInvoiceUpdate(BaseModel):
    total_amount: Optional[float] = None
    status: Optional[str] = None
    due_date: Optional[date] = None


class CardInvoiceResponse(BaseModel):
    id: str
    card_id: str
    month: int
    year: int
    total_amount: float
    status: str
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None


class CardExpenseCreate(BaseModel):
    invoice_id: str
    description: str
    amount: float
    category: str
    expense_date: date
    installments: int = 1
    installment_number: int = 1


class CardExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    expense_date: Optional[date] = None
    installments: Optional[int] = None
    installment_number: Optional[int] = None


class CardExpenseResponse(BaseModel):
    id: str
    invoice_id: str
    description: str
    amount: float
    category: str
    expense_date: date
    installments: int
    installment_number: int
    created_at: Optional[datetime] = None
