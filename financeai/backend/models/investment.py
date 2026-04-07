from pydantic import BaseModel, field_validator
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

    @field_validator('invested_amount', 'current_amount')
    @classmethod
    def amounts_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome nao pode ser vazio')
        return v.strip()


class InvestmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    institution: Optional[str] = None
    invested_amount: Optional[float] = None
    current_amount: Optional[float] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator('invested_amount', 'current_amount')
    @classmethod
    def amounts_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Nome nao pode ser vazio')
        return v.strip() if v else v


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
