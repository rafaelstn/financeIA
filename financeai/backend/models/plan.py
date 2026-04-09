from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlanCreate(BaseModel):
    month: int
    year: int
    title: str
    content: dict  # JSON com sections e items
    observations: Optional[str] = None
    status: str = "planejado"  # planejado, em_andamento, concluido


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    observations: Optional[str] = None
    status: Optional[str] = None


class PlanResponse(BaseModel):
    id: str
    month: int
    year: int
    title: str
    content: dict
    observations: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
