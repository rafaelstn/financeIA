from fastapi import APIRouter, HTTPException
from database import supabase
from models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from services.tithe_service import sync_tithe_and_firstfruits, TITHE_CATEGORIES
from datetime import date as date_type

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
    created = result.data[0]
    if created.get("type") == "income" and created.get("due_date"):
        d = date_type.fromisoformat(created["due_date"])
        sync_tithe_and_firstfruits(d.month, d.year)
    return created


@router.put("/{transaction_id}")
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    data = transaction.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Verifica se é transação automática — só permite mudar status
    existing_check = supabase.table("transactions").select("category").eq("id", transaction_id).execute()
    if existing_check.data and existing_check.data[0].get("category") in TITHE_CATEGORIES:
        allowed_fields = {"status", "paid_date"}
        if not set(data.keys()).issubset(allowed_fields):
            raise HTTPException(status_code=400, detail="Só é possível alterar o status de transações de dízimo/primícia")
    for key in ("due_date", "paid_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("transactions").update(data).eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updated = result.data[0]
    if updated.get("type") == "income" and updated.get("due_date"):
        d = date_type.fromisoformat(updated["due_date"])
        sync_tithe_and_firstfruits(d.month, d.year)
    return updated


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    # Busca antes de deletar para saber se precisa recalcular
    existing = supabase.table("transactions").select("type, due_date, category").eq("id", transaction_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Transaction not found")

    txn = existing.data[0]

    # Impede deletar transações automáticas de dízimo/primícia
    if txn.get("category") in TITHE_CATEGORIES:
        raise HTTPException(status_code=400, detail="Transações de dízimo/primícia são gerenciadas automaticamente")

    supabase.table("transactions").delete().eq("id", transaction_id).execute()

    if txn.get("type") == "income" and txn.get("due_date"):
        d = date_type.fromisoformat(txn["due_date"])
        sync_tithe_and_firstfruits(d.month, d.year)

    return {"message": "Transaction deleted"}
