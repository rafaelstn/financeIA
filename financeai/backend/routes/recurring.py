from fastapi import APIRouter, HTTPException
from database import supabase
from models.recurring import RecurringCreate, RecurringUpdate
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

router = APIRouter(prefix="/api/recurring", tags=["recurring"])


@router.get("/")
async def list_recurring(
    is_active: bool | None = None,
    type: str | None = None,
):
    query = supabase.table("recurring_transactions").select("*")
    if is_active is not None:
        query = query.eq("is_active", is_active)
    if type:
        query = query.eq("type", type)
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.post("/", status_code=201)
async def create_recurring(item: RecurringCreate):
    data = item.model_dump(exclude_none=True)
    if "next_due_date" in data:
        data["next_due_date"] = str(data["next_due_date"])
    result = supabase.table("recurring_transactions").insert(data).execute()
    return result.data[0]


@router.put("/{item_id}")
async def update_recurring(item_id: str, item: RecurringUpdate):
    data = item.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "next_due_date" in data:
        data["next_due_date"] = str(data["next_due_date"])
    result = (
        supabase.table("recurring_transactions")
        .update(data)
        .eq("id", item_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    return result.data[0]


@router.delete("/{item_id}")
async def delete_recurring(item_id: str):
    result = (
        supabase.table("recurring_transactions")
        .delete()
        .eq("id", item_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    return {"message": "Recurring transaction deleted"}


def _compute_next_due(current: date, frequency: str) -> date:
    if frequency == "weekly":
        return current + timedelta(weeks=1)
    elif frequency == "yearly":
        return current + relativedelta(years=1)
    else:  # monthly
        return current + relativedelta(months=1)


@router.post("/generate")
async def generate_pending():
    """Generate pending transactions for all active recurring items where next_due_date <= today."""
    today = date.today()
    active = (
        supabase.table("recurring_transactions")
        .select("*")
        .eq("is_active", True)
        .lte("next_due_date", str(today))
        .execute()
    ).data

    count = 0
    for item in active:
        # Create a transaction with status 'pending'
        txn_data = {
            "description": item["description"],
            "amount": item["amount"],
            "type": item["type"],
            "category": item["category"],
            "status": "pending",
            "due_date": item["next_due_date"],
            "notes": f"Gerado automaticamente (recorrente: {item['frequency']})",
        }
        supabase.table("transactions").insert(txn_data).execute()

        # Update next_due_date
        current_due = date.fromisoformat(item["next_due_date"])
        next_due = _compute_next_due(current_due, item["frequency"])
        supabase.table("recurring_transactions").update(
            {"next_due_date": str(next_due)}
        ).eq("id", item["id"]).execute()

        count += 1

    return {"generated": count}
