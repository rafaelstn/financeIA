from database import supabase
from datetime import date, timedelta


def get_active_alerts() -> list[dict]:
    today = date.today()
    alerts = []

    # Transactions pending with due_date in the past -> mark overdue
    overdue_txns = (
        supabase.table("transactions")
        .select("*")
        .eq("status", "pending")
        .lt("due_date", str(today))
        .execute()
    ).data

    for t in overdue_txns:
        # Mark as overdue in DB
        supabase.table("transactions").update({"status": "overdue"}).eq("id", t["id"]).execute()
        alerts.append({
            "id": t["id"],
            "message": f"Vencida: {t['description']} - R$ {t['amount']:.2f}",
            "level": "danger",
            "due_date": t["due_date"],
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

    # Sort: danger first, then by due_date
    alerts.sort(key=lambda a: (0 if a["level"] == "danger" else 1, a["due_date"] or ""))
    return alerts
