import math
from database import supabase

TITHE_CATEGORIES = ("Dizimo", "Primicia")
MONTH_NAMES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def sync_tithe_and_firstfruits(month: int, year: int) -> None:
    """Recalcula e sincroniza as transações de dízimo e primícia do mês."""
    start = f"{year}-{month:02d}-01"
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = f"{end_year}-{end_month:02d}-01"

    # Soma todas as receitas do mês
    income_txns = (
        supabase.table("transactions")
        .select("amount")
        .eq("type", "income")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data
    total_income = sum(t["amount"] for t in income_txns)

    month_name = MONTH_NAMES[month]
    label = f"{month_name}/{year}"

    tithe_amount = round(total_income * 0.10, 2)
    firstfruits_amount = math.ceil(total_income / 30) if total_income > 0 else 0

    items = [
        {"category": "Dizimo", "description": f"Dízimo - {label}", "amount": tithe_amount},
        {"category": "Primicia", "description": f"Primícia - {label}", "amount": firstfruits_amount},
    ]

    for item in items:
        _upsert_tithe_transaction(item, month, year, start, end, total_income)


def _upsert_tithe_transaction(
    item: dict, month: int, year: int, start: str, end: str, total_income: float
) -> None:
    """Cria, atualiza ou remove uma transação de dízimo/primícia."""
    existing = (
        supabase.table("transactions")
        .select("id, status")
        .eq("type", "expense")
        .eq("category", item["category"])
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    if total_income <= 0:
        # Remove se não há receita
        for txn in existing:
            supabase.table("transactions").delete().eq("id", txn["id"]).execute()
        return

    if existing:
        # Atualiza amount, preserva status (pode já estar "paid")
        supabase.table("transactions").update({
            "amount": item["amount"],
            "description": item["description"],
        }).eq("id", existing[0]["id"]).execute()
    else:
        # Cria nova
        import calendar
        last_day_num = calendar.monthrange(year, month)[1]
        due = f"{year}-{month:02d}-{last_day_num}"
        supabase.table("transactions").insert({
            "description": item["description"],
            "amount": item["amount"],
            "type": "expense",
            "category": item["category"],
            "status": "pending",
            "due_date": due,
        }).execute()
