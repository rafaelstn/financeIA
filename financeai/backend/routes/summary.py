from fastapi import APIRouter
from database import supabase
from datetime import date, timedelta
from services.alert_service import check_and_update_overdue

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.get("/monthly")
async def monthly_summary(month: int | None = None, year: int | None = None):
    check_and_update_overdue()
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
    card_expenses_total = 0
    for inv in invoices:
        card_name = inv.get("credit_cards", {}).get("name", "Unknown") if inv.get("credit_cards") else "Unknown"
        card_totals.append({
            "card_name": card_name,
            "total": inv["total_amount"],
            "status": inv["status"],
        })
        card_expenses_total += inv["total_amount"]

    # Soma faturas de cartão nas despesas e no saldo
    expenses += card_expenses_total
    balance = income - expenses
    if card_expenses_total > 0:
        by_category["Cartao"] = by_category.get("Cartao", 0) + card_expenses_total

    # Investments totals
    investments = supabase.table("investments").select("invested_amount, current_amount").execute().data
    total_invested = sum(i["invested_amount"] for i in investments)
    total_current = sum(i["current_amount"] for i in investments)

    # Dízimo e Primícia
    tithe_txn = next((t for t in txns if t["type"] == "expense" and t["category"] == "Dizimo"), None)
    firstfruits_txn = next((t for t in txns if t["type"] == "expense" and t["category"] == "Primicia"), None)

    tithe = tithe_txn["amount"] if tithe_txn else 0
    tithe_status = tithe_txn["status"] if tithe_txn else "pending"
    firstfruits = firstfruits_txn["amount"] if firstfruits_txn else 0
    firstfruits_status = firstfruits_txn["status"] if firstfruits_txn else "pending"

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
        "tithe": tithe,
        "tithe_status": tithe_status,
        "firstfruits": firstfruits,
        "firstfruits_status": firstfruits_status,
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

        # Soma faturas de cartão nas despesas
        month_invoices = (
            supabase.table("card_invoices")
            .select("total_amount")
            .eq("month", m)
            .eq("year", y)
            .execute()
        ).data
        expenses += sum(inv["total_amount"] for inv in month_invoices)

        months.append({"month": m, "income": income, "expenses": expenses})

    return {"year": y, "months": months}


@router.get("/upcoming")
async def upcoming_bills():
    today = date.today()
    limit = today + timedelta(days=30)

    # Pending transactions with due_date in next 30 days
    pending_txns = (
        supabase.table("transactions")
        .select("description, amount, due_date, status")
        .eq("status", "pending")
        .gte("due_date", str(today))
        .lte("due_date", str(limit))
        .order("due_date")
        .execute()
    ).data

    # Also get overdue transactions
    overdue_txns = (
        supabase.table("transactions")
        .select("description, amount, due_date, status")
        .eq("status", "overdue")
        .order("due_date")
        .execute()
    ).data

    upcoming = []
    for t in overdue_txns + pending_txns:
        due = date.fromisoformat(t["due_date"]) if t.get("due_date") else today
        days_until = (due - today).days
        upcoming.append({
            "description": t["description"],
            "amount": t["amount"],
            "due_date": t["due_date"],
            "days_until": days_until,
            "status": t["status"],
        })

    upcoming.sort(key=lambda x: x.get("due_date") or "9999-12-31")
    return {"upcoming": upcoming}
