from fastapi import APIRouter, HTTPException
from database import supabase
from models.chat import ChatRequest, ChatResponse
from services.ai import get_ai_provider
from datetime import date

router = APIRouter(prefix="/api/chat", tags=["chat"])


def build_financial_context() -> str:
    today = date.today()
    m, y = today.month, today.year
    start = f"{y}-{m:02d}-01"
    end_month = m + 1 if m < 12 else 1
    end_year = y if m < 12 else y + 1
    end = f"{end_year}-{end_month:02d}-01"

    # Monthly transactions
    txns = (
        supabase.table("transactions")
        .select("amount, type, status")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expenses = sum(t["amount"] for t in txns if t["type"] == "expense")
    balance = income - expenses

    # Overdue
    overdue = (
        supabase.table("transactions")
        .select("amount")
        .eq("status", "overdue")
        .execute()
    ).data
    overdue_count = len(overdue)
    overdue_total = sum(t["amount"] for t in overdue)

    # Investments
    investments = (
        supabase.table("investments")
        .select("invested_amount, current_amount")
        .execute()
    ).data
    invested = sum(i["invested_amount"] for i in investments)
    current = sum(i["current_amount"] for i in investments)

    # Open invoices
    open_invoices = (
        supabase.table("card_invoices")
        .select("total_amount, credit_cards(name)")
        .in_("status", ["open", "closed"])
        .execute()
    ).data
    invoice_lines = []
    for inv in open_invoices:
        card_name = inv.get("credit_cards", {}).get("name", "Cartao") if inv.get("credit_cards") else "Cartao"
        invoice_lines.append(f"  - {card_name}: R$ {inv['total_amount']:.2f}")
    invoices_text = "\n".join(invoice_lines) if invoice_lines else "  Nenhuma"

    return f"""Voce e um assistente financeiro pessoal inteligente e direto.
Contexto financeiro atual do usuario:
- Receitas do mes: R$ {income:.2f}
- Despesas do mes: R$ {expenses:.2f}
- Saldo atual: R$ {balance:.2f}
- Contas em atraso: {overdue_count} (total: R$ {overdue_total:.2f})
- Total investido: R$ {invested:.2f} | Valor atual: R$ {current:.2f}
- Faturas abertas:
{invoices_text}

Responda em portugues, seja objetivo e ofereca dicas praticas baseadas nos dados acima."""


@router.post("/")
async def chat(request: ChatRequest):
    try:
        system_prompt = build_financial_context()
        provider = get_ai_provider()
        history = [{"role": m.role, "content": m.content} for m in request.history]
        response_text = await provider.generate_response(
            message=request.message,
            history=history,
            system_prompt=system_prompt,
        )

        # Save to chat_history
        supabase.table("chat_history").insert({"role": "user", "content": request.message}).execute()
        supabase.table("chat_history").insert({"role": "assistant", "content": response_text}).execute()

        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(limit: int = 50):
    result = (
        supabase.table("chat_history")
        .select("*")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data
