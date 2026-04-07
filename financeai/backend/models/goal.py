from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    saved_amount: float = 0
    priority: str = "media"  # alta, media, baixa
    category: str  # eletronico, veiculo, imovel, viagem, educacao, saude, lazer, outros
    status: str = "ativa"  # ativa, pausada, concluida, cancelada
    target_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator('target_amount')
    @classmethod
    def target_amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor alvo deve ser maior que zero')
        return v

    @field_validator('saved_amount')
    @classmethod
    def saved_amount_must_not_be_negative(cls, v):
        if v < 0:
            raise ValueError('Valor guardado nao pode ser negativo')
        return v

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome nao pode ser vazio')
        return v.strip()


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    saved_amount: Optional[float] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    target_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator('target_amount')
    @classmethod
    def target_amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor alvo deve ser maior que zero')
        return v

    @field_validator('saved_amount')
    @classmethod
    def saved_amount_must_not_be_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Valor guardado nao pode ser negativo')
        return v

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Nome nao pode ser vazio')
        return v.strip() if v else v


class GoalResponse(BaseModel):
    id: str
    name: str
    target_amount: float
    saved_amount: float
    priority: str
    category: str
    status: str
    target_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
