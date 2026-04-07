from fastapi import APIRouter, HTTPException
from database import supabase
from models.credit_card import (
    CreditCardCreate, CreditCardUpdate,
    CardInvoiceCreate, CardInvoiceUpdate,
    CardExpenseCreate, CardExpenseUpdate,
)

router = APIRouter(prefix="/api/credit-cards", tags=["credit-cards"])

# --- Cards ---

@router.get("/")
async def list_cards():
    result = supabase.table("credit_cards").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/{card_id}")
async def get_card(card_id: str):
    result = supabase.table("credit_cards").select("*").eq("id", card_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_card(card: CreditCardCreate):
    result = supabase.table("credit_cards").insert(card.model_dump()).execute()
    return result.data[0]


@router.put("/{card_id}")
async def update_card(card_id: str, card: CreditCardUpdate):
    data = card.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = supabase.table("credit_cards").update(data).eq("id", card_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")
    return result.data[0]


@router.delete("/{card_id}")
async def delete_card(card_id: str):
    result = supabase.table("credit_cards").delete().eq("id", card_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"message": "Card deleted"}

# --- Invoices ---

@router.get("/{card_id}/invoices")
async def list_invoices(card_id: str, status: str | None = None):
    query = supabase.table("card_invoices").select("*").eq("card_id", card_id)
    if status:
        query = query.eq("status", status)
    result = query.order("year", desc=True).order("month", desc=True).execute()
    return result.data


@router.post("/{card_id}/invoices", status_code=201)
async def create_invoice(card_id: str, invoice: CardInvoiceCreate):
    data = invoice.model_dump(exclude_none=True)
    data["card_id"] = card_id
    if "due_date" in data and data["due_date"] is not None:
        data["due_date"] = str(data["due_date"])
    result = supabase.table("card_invoices").insert(data).execute()
    return result.data[0]


@router.put("/{card_id}/invoices/{invoice_id}")
async def update_invoice(card_id: str, invoice_id: str, invoice: CardInvoiceUpdate):
    data = invoice.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "due_date" in data and data["due_date"] is not None:
        data["due_date"] = str(data["due_date"])
    result = (
        supabase.table("card_invoices")
        .update(data)
        .eq("id", invoice_id)
        .eq("card_id", card_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return result.data[0]


@router.delete("/{card_id}/invoices/{invoice_id}")
async def delete_invoice(card_id: str, invoice_id: str):
    result = (
        supabase.table("card_invoices")
        .delete()
        .eq("id", invoice_id)
        .eq("card_id", card_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted"}

# --- Expenses ---

@router.get("/{card_id}/invoices/{invoice_id}/expenses")
async def list_expenses(card_id: str, invoice_id: str):
    result = (
        supabase.table("card_expenses")
        .select("*")
        .eq("invoice_id", invoice_id)
        .order("expense_date", desc=True)
        .execute()
    )
    return result.data


@router.post("/{card_id}/invoices/{invoice_id}/expenses", status_code=201)
async def create_expense(card_id: str, invoice_id: str, expense: CardExpenseCreate):
    data = expense.model_dump()
    data["invoice_id"] = invoice_id
    data["expense_date"] = str(data["expense_date"])
    result = supabase.table("card_expenses").insert(data).execute()
    # Update invoice total
    expenses = supabase.table("card_expenses").select("amount").eq("invoice_id", invoice_id).execute()
    total = sum(e["amount"] for e in expenses.data)
    supabase.table("card_invoices").update({"total_amount": total}).eq("id", invoice_id).execute()
    return result.data[0]


@router.put("/{card_id}/invoices/{invoice_id}/expenses/{expense_id}")
async def update_expense(card_id: str, invoice_id: str, expense_id: str, expense: CardExpenseUpdate):
    data = expense.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "expense_date" in data and data["expense_date"] is not None:
        data["expense_date"] = str(data["expense_date"])
    result = (
        supabase.table("card_expenses")
        .update(data)
        .eq("id", expense_id)
        .eq("invoice_id", invoice_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Expense not found")
    # Recalculate invoice total
    expenses = supabase.table("card_expenses").select("amount").eq("invoice_id", invoice_id).execute()
    total = sum(e["amount"] for e in expenses.data)
    supabase.table("card_invoices").update({"total_amount": total}).eq("id", invoice_id).execute()
    return result.data[0]


@router.delete("/{card_id}/invoices/{invoice_id}/expenses/{expense_id}")
async def delete_expense(card_id: str, invoice_id: str, expense_id: str):
    result = (
        supabase.table("card_expenses")
        .delete()
        .eq("id", expense_id)
        .eq("invoice_id", invoice_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Expense not found")
    # Recalculate invoice total
    expenses = supabase.table("card_expenses").select("amount").eq("invoice_id", invoice_id).execute()
    total = sum(e["amount"] for e in expenses.data)
    supabase.table("card_invoices").update({"total_amount": total}).eq("id", invoice_id).execute()
    return {"message": "Expense deleted"}
