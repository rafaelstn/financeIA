from fastapi import APIRouter, HTTPException
from database import supabase
from models.debt import DebtCreate, DebtUpdate, DebtResponse

router = APIRouter(prefix="/api/debts", tags=["debts"])


@router.get("/")
async def list_debts(
    status: str | None = None,
    category: str | None = None,
):
    query = supabase.table("debts").select("*")
    if status:
        query = query.eq("status", status)
    if category:
        query = query.eq("category", category)
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{debt_id}")
async def get_debt(debt_id: str):
    result = supabase.table("debts").select("*").eq("id", debt_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Debt not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_debt(debt: DebtCreate):
    data = debt.model_dump(exclude_none=True)
    if "origin_date" in data and data["origin_date"] is not None:
        data["origin_date"] = str(data["origin_date"])
    result = supabase.table("debts").insert(data).execute()
    return result.data[0]


@router.put("/{debt_id}")
async def update_debt(debt_id: str, debt: DebtUpdate):
    data = debt.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "origin_date" in data and data["origin_date"] is not None:
        data["origin_date"] = str(data["origin_date"])
    result = supabase.table("debts").update(data).eq("id", debt_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Debt not found")
    return result.data[0]


@router.delete("/{debt_id}")
async def delete_debt(debt_id: str):
    result = supabase.table("debts").delete().eq("id", debt_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Debt not found")
    return {"message": "Debt deleted"}
