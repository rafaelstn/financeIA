from fastapi import APIRouter, HTTPException
from database import supabase
from models.plan import PlanCreate, PlanUpdate
from datetime import date

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("/")
async def list_plans():
    result = (
        supabase.table("financial_plans")
        .select("*")
        .order("year", desc=True)
        .order("month", desc=True)
        .execute()
    )
    return result.data


@router.get("/{month}/{year}")
async def get_plan(month: int, year: int):
    result = (
        supabase.table("financial_plans")
        .select("*")
        .eq("month", month)
        .eq("year", year)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return result.data[0]


@router.post("/", status_code=201)
async def create_plan(plan: PlanCreate):
    data = plan.model_dump(exclude_none=True)
    result = supabase.table("financial_plans").insert(data).execute()
    return result.data[0]


@router.put("/{plan_id}")
async def update_plan(plan_id: str, plan: PlanUpdate):
    data = plan.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = (
        supabase.table("financial_plans")
        .update(data)
        .eq("id", plan_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return result.data[0]


@router.delete("/{plan_id}")
async def delete_plan(plan_id: str):
    result = (
        supabase.table("financial_plans")
        .delete()
        .eq("id", plan_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return {"message": "Plano removido"}


@router.get("/{month}/{year}/comparison")
async def get_plan_comparison(month: int, year: int):
    plan_result = (
        supabase.table("financial_plans")
        .select("*")
        .eq("month", month)
        .eq("year", year)
        .execute()
    )
    plan = plan_result.data[0] if plan_result.data else None

    start = f"{year}-{month:02d}-01"
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = f"{end_year}-{end_month:02d}-01"

    txns = (
        supabase.table("transactions")
        .select("*")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expenses = sum(t["amount"] for t in txns if t["type"] == "expense")

    by_category: dict[str, float] = {}
    for t in txns:
        if t["type"] == "expense":
            cat = t["category"]
            by_category[cat] = by_category.get(cat, 0) + t["amount"]

    debts = supabase.table("debts").select("creditor, status, current_amount").execute().data
    debts_paid = [d["creditor"] for d in debts if d.get("status") == "quitada"]

    investments = supabase.table("investments").select("invested_amount, current_amount").execute().data
    total_invested = sum(i["invested_amount"] for i in investments)

    return {
        "month": month,
        "year": year,
        "plan": plan,
        "actual": {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": by_category,
            "debts_paid": debts_paid,
            "total_invested": total_invested,
        },
        "observations": plan.get("observations") if plan else None,
    }
