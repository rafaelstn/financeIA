from fastapi import APIRouter, HTTPException
from database import supabase
from models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/")
async def list_transactions(
    type: str | None = None,
    category: str | None = None,
    status: str | None = None,
    month: int | None = None,
    year: int | None = None,
    page: int = 1,
    per_page: int = 20,
):
    query = supabase.table("transactions").select("*", count="exact")
    if type:
        query = query.eq("type", type)
    if category:
        query = query.eq("category", category)
    if status:
        query = query.eq("status", status)
    if month and year:
        start = f"{year}-{month:02d}-01"
        end_month = month + 1 if month < 12 else 1
        end_year = year if month < 12 else year + 1
        end = f"{end_year}-{end_month:02d}-01"
        query = query.gte("due_date", start).lt("due_date", end)
    offset = (page - 1) * per_page
    result = query.order("due_date", desc=True).range(offset, offset + per_page - 1).execute()
    return {"data": result.data, "total": result.count, "page": page, "per_page": per_page}


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    result = supabase.table("transactions").select("*").eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_transaction(transaction: TransactionCreate):
    data = transaction.model_dump(exclude_none=True)
    for key in ("due_date", "paid_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("transactions").insert(data).execute()
    return result.data[0]


@router.put("/{transaction_id}")
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    data = transaction.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for key in ("due_date", "paid_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("transactions").update(data).eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result.data[0]


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = supabase.table("transactions").delete().eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}
