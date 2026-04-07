from fastapi import APIRouter, HTTPException
from database import supabase
from models.investment import InvestmentCreate, InvestmentUpdate

router = APIRouter(prefix="/api/investments", tags=["investments"])


@router.get("/")
async def list_investments():
    result = supabase.table("investments").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/{investment_id}")
async def get_investment(investment_id: str):
    result = supabase.table("investments").select("*").eq("id", investment_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_investment(investment: InvestmentCreate):
    data = investment.model_dump(exclude_none=True)
    for key in ("start_date", "maturity_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("investments").insert(data).execute()
    return result.data[0]


@router.put("/{investment_id}")
async def update_investment(investment_id: str, investment: InvestmentUpdate):
    data = investment.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for key in ("start_date", "maturity_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("investments").update(data).eq("id", investment_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    return result.data[0]


@router.delete("/{investment_id}")
async def delete_investment(investment_id: str):
    result = supabase.table("investments").delete().eq("id", investment_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "Investment deleted"}
