from fastapi import APIRouter, HTTPException
from database import supabase
from models.budget import BudgetCreate, BudgetUpdate
from datetime import date

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("/")
async def list_budgets():
    result = supabase.table("budgets").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/status")
async def get_budgets_status():
    """For each active budget, return spent this month, remaining, and percentage."""
    today = date.today()
    m, y = today.month, today.year
    start = f"{y}-{m:02d}-01"
    end_month = m + 1 if m < 12 else 1
    end_year = y if m < 12 else y + 1
    end = f"{end_year}-{end_month:02d}-01"

    budgets = (
        supabase.table("budgets")
        .select("*")
        .eq("is_active", True)
        .execute()
    ).data

    # Get all expense transactions for the current month
    txns = (
        supabase.table("transactions")
        .select("category, amount")
        .eq("type", "expense")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    # Sum by category
    spent_by_cat: dict[str, float] = {}
    for t in txns:
        cat = t["category"]
        spent_by_cat[cat] = spent_by_cat.get(cat, 0) + t["amount"]

    result = []
    for b in budgets:
        spent = spent_by_cat.get(b["category"], 0)
        limit_val = b["monthly_limit"]
        remaining = limit_val - spent
        pct = (spent / limit_val * 100) if limit_val > 0 else 0
        result.append({
            "id": b["id"],
            "category": b["category"],
            "monthly_limit": limit_val,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": round(pct, 1),
        })

    return result


@router.post("/", status_code=201)
async def create_budget(budget: BudgetCreate):
    data = budget.model_dump(exclude_none=True)
    result = supabase.table("budgets").insert(data).execute()
    return result.data[0]


@router.put("/{budget_id}")
async def update_budget(budget_id: str, budget: BudgetUpdate):
    data = budget.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = supabase.table("budgets").update(data).eq("id", budget_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Budget not found")
    return result.data[0]


@router.delete("/{budget_id}")
async def delete_budget(budget_id: str):
    result = supabase.table("budgets").delete().eq("id", budget_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted"}
