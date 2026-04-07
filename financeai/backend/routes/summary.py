from fastapi import APIRouter
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.get("/monthly")
async def monthly_summary(month: int | None = None, year: int | None = None):
    today = date.today()
    m = month or today.month
    y = year or today.year
    start = f"{y}-{m:02d}-01"
    end_month = m + 1 if m < 12 else 1
    end_year = y if m < 12 else y + 1
    end = f"{end_year}-{end_month:02d}-01"

    # Transactions in the month
    txns = (
        supabase.table("transactions")
        .select("*")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expenses = sum(t["amount"] for t in txns if t["type"] == "expense")
    balance = income - expenses

    # Expenses by category
    by_category: dict[str, float] = {}
    for t in txns:
        if t["type"] == "expense":
            cat = t["category"]
            by_category[cat] = by_category.get(cat, 0) + t["amount"]

    # Card invoices for this month
    invoices = (
        supabase.table("card_invoices")
        .select("*, credit_cards(name)")
        .eq("month", m)
        .eq("year", y)
        .execute()
    ).data

    card_totals = []
    for inv in invoices:
        card_name = inv.get("credit_cards", {}).get("name", "Unknown") if inv.get("credit_cards") else "Unknown"
        card_totals.append({
            "card_name": card_name,
            "total": inv["total_amount"],
            "status": inv["status"],
        })

    # Investments totals
    investments = supabase.table("investments").select("invested_amount, current_amount").execute().data
    total_invested = sum(i["invested_amount"] for i in investments)
    total_current = sum(i["current_amount"] for i in investments)

    return {
        "month": m,
        "year": y,
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "by_category": by_category,
        "card_totals": card_totals,
        "total_invested": total_invested,
        "total_current": total_current,
    }


@router.get("/yearly")
async def yearly_summary(year: int | None = None):
    y = year or date.today().year
    months = []
    for m in range(1, 13):
        start = f"{y}-{m:02d}-01"
        end_month = m + 1 if m < 12 else 1
        end_year = y if m < 12 else y + 1
        end = f"{end_year}-{end_month:02d}-01"

        txns = (
            supabase.table("transactions")
            .select("amount, type")
            .gte("due_date", start)
            .lt("due_date", end)
            .execute()
        ).data

        income = sum(t["amount"] for t in txns if t["type"] == "income")
        expenses = sum(t["amount"] for t in txns if t["type"] == "expense")

        months.append({"month": m, "income": income, "expenses": expenses})

    return {"year": y, "months": months}
