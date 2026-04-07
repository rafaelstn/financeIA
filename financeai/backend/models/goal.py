from pydantic import BaseModel
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


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    saved_amount: Optional[float] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    target_date: Optional[date] = None
    notes: Optional[str] = None


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
