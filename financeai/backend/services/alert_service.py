import logging

from database import supabase
from datetime import date, timedelta

logger = logging.getLogger("financeai.alerts")


def check_and_update_overdue() -> None:
    """Mark pending transactions with past due_date as overdue."""
    today = date.today()
    overdue_txns = (
        supabase.table("transactions")
        .select("id")
        .eq("status", "pending")
        .lt("due_date", str(today))
        .execute()
    ).data

    for t in overdue_txns:
        supabase.table("transactions").update({"status": "overdue"}).eq("id", t["id"]).execute()

    if overdue_txns:
        logger.info(f"Marked {len(overdue_txns)} transaction(s) as overdue")


def get_active_alerts() -> list[dict]:
    """Return active alerts. Calls check_and_update_overdue() first."""
    check_and_update_overdue()

    today = date.today()
    alerts = []

    # Overdue transactions
    overdue_txns = (
        supabase.table("transactions")
        .select("*")
        .eq("status", "overdue")
        .execute()
    ).data

    for t in overdue_txns:
        alerts.append({
            "id": t["id"],
            "message": f"Vencida: {t['description']} - R$ {t['amount']:.2f}",
            "level": "danger",
            "due_date": t.get("due_date"),
            "amount": t["amount"],
            "source": "transaction",
        })

    # Transactions pending with due_date in next 3 days
    limit_date = str(today + timedelta(days=3))
    upcoming_txns = (
        supabase.table("transactions")
        .select("*")
        .eq("status", "pending")
        .gte("due_date", str(today))
        .lte("due_date", limit_date)
        .execute()
    ).data

    for t in upcoming_txns:
        days_left = (date.fromisoformat(t["due_date"]) - today).days
        alerts.append({
            "id": t["id"],
            "message": f"Vence em {days_left} dia(s): {t['description']} - R$ {t['amount']:.2f}",
            "level": "warning",
            "due_date": t["due_date"],
            "amount": t["amount"],
            "source": "transaction",
        })

    # Card invoices with due_date in next 5 days
    invoice_limit = str(today + timedelta(days=5))
    upcoming_invoices = (
        supabase.table("card_invoices")
        .select("*, credit_cards(name)")
        .in_("status", ["open", "closed"])
        .gte("due_date", str(today))
        .lte("due_date", invoice_limit)
        .execute()
    ).data

    for inv in upcoming_invoices:
        card_name = inv.get("credit_cards", {}).get("name", "Cartao") if inv.get("credit_cards") else "Cartao"
        days_left = (date.fromisoformat(inv["due_date"]) - today).days
        alerts.append({
            "id": inv["id"],
            "message": f"Fatura {card_name} vence em {days_left} dia(s) - R$ {inv['total_amount']:.2f}",
            "level": "warning",
            "due_date": inv["due_date"],
            "amount": inv["total_amount"],
            "source": "invoice",
        })

    # Active debts reminder
    try:
        active_debts = (
            supabase.table("debts")
            .select("id, creditor, current_amount, category")
            .eq("status", "ativa")
            .execute()
        ).data
        for d in active_debts:
            alerts.append({
                "id": d["id"],
                "message": f"Divida ativa: {d['creditor']} - R$ {d['current_amount']:.2f}",
                "level": "info",
                "due_date": None,
                "amount": d["current_amount"],
                "source": "debt",
            })
    except Exception:
        logger.exception("Failed to fetch active debts for alerts")

    # Goals off-track (target_date approaching and saved_amount < expected progress)
    try:
        active_goals = (
            supabase.table("goals")
            .select("id, name, target_amount, saved_amount, target_date")
            .eq("status", "ativa")
            .execute()
        ).data
        for g in active_goals:
            if not g.get("target_date"):
                continue
            target_date = date.fromisoformat(g["target_date"])
            days_remaining = (target_date - today).days
            if days_remaining <= 0:
                alerts.append({
                    "id": g["id"],
                    "message": f"Meta vencida: {g['name']} - faltam R$ {g['target_amount'] - g['saved_amount']:.2f}",
                    "level": "danger",
                    "due_date": g["target_date"],
                    "amount": g["target_amount"] - g["saved_amount"],
                    "source": "goal",
                })
            elif days_remaining <= 30:
                remaining_amount = g["target_amount"] - g["saved_amount"]
                progress_pct = (g["saved_amount"] / g["target_amount"] * 100) if g["target_amount"] > 0 else 0
                if progress_pct < 80:
                    alerts.append({
                        "id": g["id"],
                        "message": f"Meta em risco: {g['name']} - {progress_pct:.0f}% concluida, vence em {days_remaining} dia(s)",
                        "level": "warning",
                        "due_date": g["target_date"],
                        "amount": remaining_amount,
                        "source": "goal",
                    })
    except Exception:
        logger.exception("Failed to fetch goals for alerts")

    # Budget alerts
    try:
        budgets = (
            supabase.table("budgets")
            .select("*")
            .eq("is_active", True)
            .execute()
        ).data

        if budgets:
            m, y = today.month, today.year
            b_start = f"{y}-{m:02d}-01"
            b_end_month = m + 1 if m < 12 else 1
            b_end_year = y if m < 12 else y + 1
            b_end = f"{b_end_year}-{b_end_month:02d}-01"

            expense_txns = (
                supabase.table("transactions")
                .select("category, amount")
                .eq("type", "expense")
                .gte("due_date", b_start)
                .lt("due_date", b_end)
                .execute()
            ).data

            spent_by_cat: dict[str, float] = {}
            for t in expense_txns:
                cat = t["category"]
                spent_by_cat[cat] = spent_by_cat.get(cat, 0) + t["amount"]

            for b in budgets:
                spent = spent_by_cat.get(b["category"], 0)
                limit_val = b["monthly_limit"]
                if limit_val <= 0:
                    continue
                pct = spent / limit_val * 100
                if pct >= 100:
                    alerts.append({
                        "id": b["id"],
                        "message": f"Orcamento estourado: {b['category']} - R$ {spent:.2f} / R$ {limit_val:.2f} ({pct:.0f}%)",
                        "level": "danger",
                        "due_date": None,
                        "amount": spent,
                        "source": "budget",
                    })
                elif pct >= 80:
                    alerts.append({
                        "id": b["id"],
                        "message": f"Orcamento quase no limite: {b['category']} - R$ {spent:.2f} / R$ {limit_val:.2f} ({pct:.0f}%)",
                        "level": "warning",
                        "due_date": None,
                        "amount": spent,
                        "source": "budget",
                    })
    except Exception:
        logger.exception("Failed to fetch budgets for alerts")

    # Sort: danger first, then warning, then info, then by due_date
    level_order = {"danger": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: (level_order.get(a["level"], 3), a.get("due_date") or ""))
    return alerts
