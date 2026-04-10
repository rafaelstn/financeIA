from fastapi import APIRouter, HTTPException
from database import supabase
from models.recurring import RecurringCreate, RecurringUpdate
from datetime import date, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta

router = APIRouter(prefix="/api/recurring", tags=["recurring"])


def get_nth_business_day(year: int, month: int, n: int) -> date:
    """Returns the Nth business day (weekday Mon-Fri) of the given month."""
    count = 0
    _, last_day = monthrange(year, month)
    last_bd = None
    for day in range(1, last_day + 1):
        d = date(year, month, day)
        if d.weekday() < 5:  # Monday=0 to Friday=4
            count += 1
            last_bd = d
            if count == n:
                return d
    # If N exceeds business days in month, return last business day
    return last_bd


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

    # Auto-calculate next_due_date when using business day
    if data.get("use_business_day") and data.get("business_day_number"):
        today = date.today()
        bd = get_nth_business_day(today.year, today.month, data["business_day_number"])
        if bd <= today:
            # Already passed this month, use next month
            next_m = today.month + 1 if today.month < 12 else 1
            next_y = today.year if today.month < 12 else today.year + 1
            bd = get_nth_business_day(next_y, next_m, data["business_day_number"])
        data["next_due_date"] = str(bd)
    elif "next_due_date" in data:
        data["next_due_date"] = str(data["next_due_date"])

    result = supabase.table("recurring_transactions").insert(data).execute()
    return result.data[0]


@router.put("/{item_id}")
async def update_recurring(item_id: str, item: RecurringUpdate):
    data = item.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Auto-calculate next_due_date when switching to business day mode
    if data.get("use_business_day") and data.get("business_day_number"):
        today = date.today()
        bd = get_nth_business_day(today.year, today.month, data["business_day_number"])
        if bd <= today:
            next_m = today.month + 1 if today.month < 12 else 1
            next_y = today.year if today.month < 12 else today.year + 1
            bd = get_nth_business_day(next_y, next_m, data["business_day_number"])
        data["next_due_date"] = str(bd)
    elif "next_due_date" in data:
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


def _compute_next_due(current: date, frequency: str, item: dict | None = None) -> date:
    """Compute next due date. Supports business day mode for monthly items."""
    if item and item.get("use_business_day") and item.get("business_day_number"):
        # Business day mode: calculate Nth business day of the next period
        if frequency == "monthly":
            next_m = current.month + 1 if current.month < 12 else 1
            next_y = current.year if current.month < 12 else current.year + 1
            return get_nth_business_day(next_y, next_m, item["business_day_number"])
        elif frequency == "yearly":
            return get_nth_business_day(
                current.year + 1, current.month, item["business_day_number"]
            )
    # Regular fixed-day logic
    if frequency == "weekly":
        return current + timedelta(weeks=1)
    elif frequency == "yearly":
        return current + relativedelta(years=1)
    else:  # monthly
        return current + relativedelta(months=1)


def _transaction_exists_in_month(description: str, year: int, month: int) -> bool:
    """Check if a transaction with same description already exists in the given month."""
    start = f"{year}-{month:02d}-01"
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = f"{end_year}-{end_month:02d}-01"
    result = (
        supabase.table("transactions")
        .select("id")
        .eq("description", description)
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    )
    return len(result.data) > 0


@router.post("/generate")
async def generate_pending(months_ahead: int = 3):
    """Generate pending transactions for active recurring items.

    Safe against duplicates: checks if transaction already exists before creating.
    Catches up on missed months and generates up to N months ahead for planning.
    """
    today = date.today()
    limit_date = today + relativedelta(months=months_ahead)

    active = (
        supabase.table("recurring_transactions")
        .select("*")
        .eq("is_active", True)
        .execute()
    ).data

    created = 0
    skipped = 0

    for item in active:
        current_due = date.fromisoformat(item["next_due_date"])

        # Loop: catch up on all missed periods up to 5 days from now
        while current_due <= limit_date:
            # Calculate actual due date (business day aware)
            if item.get("use_business_day") and item.get("business_day_number"):
                actual_due = get_nth_business_day(
                    current_due.year, current_due.month, item["business_day_number"]
                )
            else:
                actual_due = current_due

            due_str = str(actual_due)

            # Check for duplicate: same description in same month
            if not _transaction_exists_in_month(item["description"], actual_due.year, actual_due.month):
                txn_data = {
                    "description": item["description"],
                    "amount": item["amount"],
                    "type": item["type"],
                    "category": item["category"],
                    "status": "overdue" if actual_due < today else "pending",
                    "due_date": due_str,
                    "notes": f"Gerado automaticamente (recorrente: {item['frequency']})",
                }
                supabase.table("transactions").insert(txn_data).execute()
                created += 1
            else:
                skipped += 1

            # Advance to next period
            current_due = _compute_next_due(current_due, item["frequency"], item)

        # Update next_due_date to the next future period
        supabase.table("recurring_transactions").update(
            {"next_due_date": str(current_due)}
        ).eq("id", item["id"]).execute()

    return {"generated": created, "skipped": skipped}
