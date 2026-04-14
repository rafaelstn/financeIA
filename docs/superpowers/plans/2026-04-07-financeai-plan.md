# FinanceAI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal finance system with dashboard, CRUD operations, alerts, and AI chat with financial context.

**Architecture:** Next.js 14 frontend communicates via REST with a FastAPI backend. Backend is the sole gateway to Supabase (PostgreSQL) and AI providers. Multi-provider AI via Strategy Pattern, configurable in `.env`.

**Tech Stack:** Python/FastAPI, Next.js 14/TypeScript, Tailwind/shadcn/ui, Recharts, Supabase, Gemini/Claude/OpenAI APIs.

---

## Task 1: Project Scaffolding and Database Setup

**Files:**
- Create: `financeai/.env`
- Create: `financeai/backend/requirements.txt`
- Create: `financeai/backend/config.py`
- Create: `financeai/backend/database.py`

- [ ] **Step 1: Create project directories**

```bash
mkdir -p "f:/Financeiro Pessoal/financeai/backend/models"
mkdir -p "f:/Financeiro Pessoal/financeai/backend/routes"
mkdir -p "f:/Financeiro Pessoal/financeai/backend/services/ai"
```

- [ ] **Step 2: Create `.env` file**

Create `financeai/.env`:
```env
SUPABASE_URL=https://fvpijszqtevhtjbagzba.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2cGlqc3pxdGV2aHRqYmFnemJhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTU3NzUyMywiZXhwIjoyMDkxMTUzNTIzfQ.oCdTUMWBRRAIt1LMs00sRTKNSlF8hjqJe09CARq39JA
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyB5GVxfm3F_KaoSxRAm0KZYX7kkKRA4X5c
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

- [ ] **Step 3: Create `requirements.txt`**

Create `financeai/backend/requirements.txt`:
```
fastapi
uvicorn[standard]
supabase
python-dotenv
anthropic
openai
google-genai
pydantic
httpx
```

- [ ] **Step 4: Install Python dependencies**

```bash
cd "f:/Financeiro Pessoal/financeai/backend"
pip install -r requirements.txt
```

- [ ] **Step 5: Create `config.py`**

Create `financeai/backend/config.py`:
```python
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")


settings = Settings()
```

- [ ] **Step 6: Create `database.py`**

Create `financeai/backend/database.py`:
```python
from supabase import create_client, Client
from config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
```

- [ ] **Step 7: Create database tables in Supabase**

Run the following SQL via the Supabase API (using `httpx` or the MCP tool):

```sql
CREATE TABLE IF NOT EXISTS transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  description TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  type TEXT CHECK (type IN ('income', 'expense')) NOT NULL,
  category TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'paid', 'overdue')) DEFAULT 'pending',
  due_date DATE,
  paid_date DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credit_cards (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  bank TEXT NOT NULL,
  limit_amount DECIMAL(10,2) NOT NULL,
  closing_day INTEGER NOT NULL,
  due_day INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS card_invoices (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  card_id UUID REFERENCES credit_cards(id) ON DELETE CASCADE,
  month INTEGER NOT NULL,
  year INTEGER NOT NULL,
  total_amount DECIMAL(10,2) DEFAULT 0,
  status TEXT CHECK (status IN ('open', 'closed', 'paid')) DEFAULT 'open',
  due_date DATE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS card_expenses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  invoice_id UUID REFERENCES card_invoices(id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  category TEXT NOT NULL,
  expense_date DATE NOT NULL,
  installments INTEGER DEFAULT 1,
  installment_number INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS investments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  institution TEXT NOT NULL,
  invested_amount DECIMAL(10,2) NOT NULL,
  current_amount DECIMAL(10,2) NOT NULL,
  start_date DATE NOT NULL,
  maturity_date DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chat_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT now()
);
```

- [ ] **Step 8: Verify tables were created**

Query the Supabase API or run `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';` to confirm all 7 tables exist.

- [ ] **Step 9: Commit**

```bash
git init
git add .
git commit -m "feat: project scaffolding, database setup, config"
```

---

## Task 2: Pydantic Models

**Files:**
- Create: `financeai/backend/models/__init__.py`
- Create: `financeai/backend/models/transaction.py`
- Create: `financeai/backend/models/credit_card.py`
- Create: `financeai/backend/models/investment.py`
- Create: `financeai/backend/models/alert.py`
- Create: `financeai/backend/models/chat.py`

- [ ] **Step 1: Create `models/__init__.py`**

Create empty `financeai/backend/models/__init__.py`.

- [ ] **Step 2: Create `models/transaction.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TransactionCreate(BaseModel):
    description: str
    amount: float
    type: str  # 'income' | 'expense'
    category: str
    status: str = "pending"
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    description: str
    amount: float
    type: str
    category: str
    status: str
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
```

- [ ] **Step 3: Create `models/credit_card.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class CreditCardCreate(BaseModel):
    name: str
    bank: str
    limit_amount: float
    closing_day: int
    due_day: int


class CreditCardUpdate(BaseModel):
    name: Optional[str] = None
    bank: Optional[str] = None
    limit_amount: Optional[float] = None
    closing_day: Optional[int] = None
    due_day: Optional[int] = None


class CreditCardResponse(BaseModel):
    id: str
    name: str
    bank: str
    limit_amount: float
    closing_day: int
    due_day: int
    created_at: Optional[datetime] = None


class CardInvoiceCreate(BaseModel):
    card_id: str
    month: int
    year: int
    total_amount: float = 0
    status: str = "open"
    due_date: Optional[date] = None


class CardInvoiceUpdate(BaseModel):
    total_amount: Optional[float] = None
    status: Optional[str] = None
    due_date: Optional[date] = None


class CardInvoiceResponse(BaseModel):
    id: str
    card_id: str
    month: int
    year: int
    total_amount: float
    status: str
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None


class CardExpenseCreate(BaseModel):
    invoice_id: str
    description: str
    amount: float
    category: str
    expense_date: date
    installments: int = 1
    installment_number: int = 1


class CardExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    expense_date: Optional[date] = None
    installments: Optional[int] = None
    installment_number: Optional[int] = None


class CardExpenseResponse(BaseModel):
    id: str
    invoice_id: str
    description: str
    amount: float
    category: str
    expense_date: date
    installments: int
    installment_number: int
    created_at: Optional[datetime] = None
```

- [ ] **Step 4: Create `models/investment.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class InvestmentCreate(BaseModel):
    name: str
    type: str
    institution: str
    invested_amount: float
    current_amount: float
    start_date: date
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class InvestmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    institution: Optional[str] = None
    invested_amount: Optional[float] = None
    current_amount: Optional[float] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class InvestmentResponse(BaseModel):
    id: str
    name: str
    type: str
    institution: str
    invested_amount: float
    current_amount: float
    start_date: date
    maturity_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

- [ ] **Step 5: Create `models/alert.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date


class AlertResponse(BaseModel):
    id: str
    message: str
    level: str  # 'warning' | 'danger'
    due_date: Optional[date] = None
    amount: Optional[float] = None
    source: str  # 'transaction' | 'invoice'
```

- [ ] **Step 6: Create `models/chat.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant'
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str


class ChatHistoryResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: Optional[datetime] = None
```

- [ ] **Step 7: Commit**

```bash
git add backend/models/
git commit -m "feat: add Pydantic models for all entities"
```

---

## Task 3: Backend Main + Health Check

**Files:**
- Create: `financeai/backend/main.py`
- Create: `financeai/backend/routes/__init__.py`

- [ ] **Step 1: Create `routes/__init__.py`**

Create empty `financeai/backend/routes/__init__.py`.

- [ ] **Step 2: Create `main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinanceAI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "FinanceAI API"}
```

- [ ] **Step 3: Start the server and verify health check**

```bash
cd "f:/Financeiro Pessoal/financeai/backend"
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/` — should return `{"status": "ok", "service": "FinanceAI API"}`.

- [ ] **Step 4: Commit**

```bash
git add backend/main.py backend/routes/__init__.py
git commit -m "feat: FastAPI app with CORS and health check"
```

---

## Task 4: Transactions CRUD Route

**Files:**
- Create: `financeai/backend/routes/transactions.py`
- Modify: `financeai/backend/main.py` (add router include)

- [ ] **Step 1: Create `routes/transactions.py`**

```python
from fastapi import APIRouter, HTTPException
from database import supabase
from models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/")
async def list_transactions(
    type: str | None = None,
    category: str | None = None,
    status: str | None = None,
    month: int | None = None,
    year: int | None = None,
):
    query = supabase.table("transactions").select("*")
    if type:
        query = query.eq("type", type)
    if category:
        query = query.eq("category", category)
    if status:
        query = query.eq("status", status)
    if month and year:
        start = f"{year}-{month:02d}-01"
        end_month = month + 1 if month < 12 else 1
        end_year = year if month < 12 else year + 1
        end = f"{end_year}-{end_month:02d}-01"
        query = query.gte("due_date", start).lt("due_date", end)
    result = query.order("due_date", desc=True).execute()
    return result.data


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    result = supabase.table("transactions").select("*").eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_transaction(transaction: TransactionCreate):
    data = transaction.model_dump(exclude_none=True)
    # Convert date objects to ISO strings for JSON serialization
    for key in ("due_date", "paid_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("transactions").insert(data).execute()
    return result.data[0]


@router.put("/{transaction_id}")
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    data = transaction.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for key in ("due_date", "paid_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("transactions").update(data).eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result.data[0]


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = supabase.table("transactions").delete().eq("id", transaction_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}
```

- [ ] **Step 2: Register router in `main.py`**

Add to `main.py` after CORS middleware:
```python
from routes.transactions import router as transactions_router

app.include_router(transactions_router)
```

- [ ] **Step 3: Test with curl**

```bash
# Create
curl -X POST http://localhost:8000/api/transactions/ -H "Content-Type: application/json" -d '{"description":"Salario","amount":5000,"type":"income","category":"Salario","due_date":"2026-04-10"}'

# List
curl http://localhost:8000/api/transactions/
```

- [ ] **Step 4: Commit**

```bash
git add backend/routes/transactions.py backend/main.py
git commit -m "feat: transactions CRUD endpoints"
```

---

## Task 5: Credit Cards CRUD Route (cards + invoices + expenses)

**Files:**
- Create: `financeai/backend/routes/credit_cards.py`
- Modify: `financeai/backend/main.py` (add router include)

- [ ] **Step 1: Create `routes/credit_cards.py`**

```python
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
```

- [ ] **Step 2: Register router in `main.py`**

Add to `main.py`:
```python
from routes.credit_cards import router as credit_cards_router

app.include_router(credit_cards_router)
```

- [ ] **Step 3: Test with curl**

```bash
# Create card
curl -X POST http://localhost:8000/api/credit-cards/ -H "Content-Type: application/json" -d '{"name":"Nubank","bank":"Nubank","limit_amount":5000,"closing_day":3,"due_day":10}'

# List cards
curl http://localhost:8000/api/credit-cards/
```

- [ ] **Step 4: Commit**

```bash
git add backend/routes/credit_cards.py backend/main.py
git commit -m "feat: credit cards, invoices, and expenses CRUD endpoints"
```

---

## Task 6: Investments CRUD Route

**Files:**
- Create: `financeai/backend/routes/investments.py`
- Modify: `financeai/backend/main.py` (add router include)

- [ ] **Step 1: Create `routes/investments.py`**

```python
from fastapi import APIRouter, HTTPException
from database import supabase
from models.investment import InvestmentCreate, InvestmentUpdate

router = APIRouter(prefix="/api/investments", tags=["investments"])


@router.get("/")
async def list_investments():
    result = supabase.table("investments").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/{investment_id}")
async def get_investment(investment_id: str):
    result = supabase.table("investments").select("*").eq("id", investment_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    return result.data[0]


@router.post("/", status_code=201)
async def create_investment(investment: InvestmentCreate):
    data = investment.model_dump(exclude_none=True)
    for key in ("start_date", "maturity_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("investments").insert(data).execute()
    return result.data[0]


@router.put("/{investment_id}")
async def update_investment(investment_id: str, investment: InvestmentUpdate):
    data = investment.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for key in ("start_date", "maturity_date"):
        if key in data and data[key] is not None:
            data[key] = str(data[key])
    result = supabase.table("investments").update(data).eq("id", investment_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    return result.data[0]


@router.delete("/{investment_id}")
async def delete_investment(investment_id: str):
    result = supabase.table("investments").delete().eq("id", investment_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "Investment deleted"}
```

- [ ] **Step 2: Register router in `main.py`**

Add to `main.py`:
```python
from routes.investments import router as investments_router

app.include_router(investments_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/routes/investments.py backend/main.py
git commit -m "feat: investments CRUD endpoints"
```

---

## Task 7: Summary Routes

**Files:**
- Create: `financeai/backend/routes/summary.py`
- Modify: `financeai/backend/main.py` (add router include)

- [ ] **Step 1: Create `routes/summary.py`**

```python
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
```

- [ ] **Step 2: Register router in `main.py`**

Add to `main.py`:
```python
from routes.summary import router as summary_router

app.include_router(summary_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/routes/summary.py backend/main.py
git commit -m "feat: monthly and yearly summary endpoints"
```

---

## Task 8: Alert Service and Route

**Files:**
- Create: `financeai/backend/services/alert_service.py`
- Create: `financeai/backend/routes/alerts.py`
- Modify: `financeai/backend/main.py` (add router include)

- [ ] **Step 1: Create `services/__init__.py` and `services/ai/__init__.py`**

Create empty files:
- `financeai/backend/services/__init__.py`
- `financeai/backend/services/ai/__init__.py`

- [ ] **Step 2: Create `services/alert_service.py`**

```python
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
```

- [ ] **Step 3: Create `routes/alerts.py`**

```python
from fastapi import APIRouter
from services.alert_service import get_active_alerts

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/")
async def list_alerts():
    return get_active_alerts()
```

- [ ] **Step 4: Register router in `main.py`**

Add to `main.py`:
```python
from routes.alerts import router as alerts_router

app.include_router(alerts_router)
```

- [ ] **Step 5: Commit**

```bash
git add backend/services/ backend/routes/alerts.py backend/main.py
git commit -m "feat: alert service with overdue detection and upcoming warnings"
```

---

## Task 9: AI Service (Strategy Pattern)

**Files:**
- Create: `financeai/backend/services/ai/base.py`
- Create: `financeai/backend/services/ai/gemini_provider.py`
- Create: `financeai/backend/services/ai/claude_provider.py`
- Create: `financeai/backend/services/ai/openai_provider.py`
- Modify: `financeai/backend/services/ai/__init__.py` (add factory)

- [ ] **Step 1: Create `services/ai/base.py`**

```python
from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str:
        ...
```

- [ ] **Step 2: Create `services/ai/gemini_provider.py`**

```python
from google import genai
from services.ai.base import AIProvider
from config import settings


class GeminiProvider(AIProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.0-flash"

    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str:
        contents = []
        # Add history
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        # Add current message
        contents.append({"role": "user", "parts": [{"text": message}]})

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config={"system_instruction": system_prompt},
        )
        return response.text
```

- [ ] **Step 3: Create `services/ai/claude_provider.py`**

```python
import anthropic
from services.ai.base import AIProvider
from config import settings


class ClaudeProvider(AIProvider):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str:
        messages = []
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
```

- [ ] **Step 4: Create `services/ai/openai_provider.py`**

```python
from openai import OpenAI
from services.ai.base import AIProvider
from config import settings


class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"

    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content
```

- [ ] **Step 5: Create factory in `services/ai/__init__.py`**

```python
from services.ai.base import AIProvider
from config import settings


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        from services.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif provider == "claude":
        from services.ai.claude_provider import ClaudeProvider
        return ClaudeProvider()
    elif provider == "openai":
        from services.ai.openai_provider import OpenAIProvider
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider}. Use 'gemini', 'claude', or 'openai'.")
```

- [ ] **Step 6: Commit**

```bash
git add backend/services/ai/
git commit -m "feat: multi-provider AI service with Gemini, Claude, and OpenAI"
```

---

## Task 10: Chat Route

**Files:**
- Create: `financeai/backend/routes/chat.py`
- Modify: `financeai/backend/main.py` (add router include)

- [ ] **Step 1: Create `routes/chat.py`**

```python
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
```

- [ ] **Step 2: Register router in `main.py`**

Add to `main.py`:
```python
from routes.chat import router as chat_router

app.include_router(chat_router)
```

- [ ] **Step 3: Test chat endpoint**

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"Como estao minhas financas?","history":[]}'
```

- [ ] **Step 4: Commit**

```bash
git add backend/routes/chat.py backend/main.py
git commit -m "feat: chat endpoint with financial context injection"
```

---

## Task 11: Frontend Setup (Next.js + shadcn/ui + Dark Mode)

**Files:**
- Create: Next.js project in `financeai/frontend/`
- Modify: `financeai/frontend/app/layout.tsx`
- Modify: `financeai/frontend/tailwind.config.ts`

- [ ] **Step 1: Create Next.js project**

```bash
cd "f:/Financeiro Pessoal/financeai"
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm
```

- [ ] **Step 2: Install dependencies**

```bash
cd "f:/Financeiro Pessoal/financeai/frontend"
npm install axios recharts lucide-react
npx shadcn@latest init -d
npx shadcn@latest add button input card dialog table badge select label textarea tabs separator sheet
```

- [ ] **Step 3: Configure dark mode in `app/globals.css`**

Replace contents of `financeai/frontend/app/globals.css`:
```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
  --color-sidebar-ring: var(--sidebar-ring);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar: var(--sidebar);
  --color-chart-5: var(--chart-5);
  --color-chart-4: var(--chart-4);
  --color-chart-3: var(--chart-3);
  --color-chart-2: var(--chart-2);
  --color-chart-1: var(--chart-1);
  --color-ring: var(--ring);
  --color-input: var(--input);
  --color-border: var(--border);
  --color-destructive: var(--destructive);
  --color-accent-foreground: var(--accent-foreground);
  --color-accent: var(--accent);
  --color-muted-foreground: var(--muted-foreground);
  --color-muted: var(--muted);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-secondary: var(--secondary);
  --color-primary-foreground: var(--primary-foreground);
  --color-primary: var(--primary);
  --color-popover-foreground: var(--popover-foreground);
  --color-popover: var(--popover);
  --color-card-foreground: var(--card-foreground);
  --color-card: var(--card);
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
  --radius-sm: calc(var(--radius) - 4px);
}
```

Note: The actual dark theme colors are defined via shadcn/ui's CSS variables. The `dark` class on `<html>` activates them.

- [ ] **Step 4: Update `app/layout.tsx` to force dark mode**

Replace `financeai/frontend/app/layout.tsx`:
```tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FinanceAI",
  description: "Sistema financeiro pessoal com IA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}>
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 5: Create API client `lib/api.ts`**

Create `financeai/frontend/lib/api.ts`:
```typescript
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
});

export default api;
```

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: Next.js setup with shadcn/ui, dark mode, and API client"
```

---

## Task 12: Sidebar Component

**Files:**
- Create: `financeai/frontend/components/Sidebar.tsx`

- [ ] **Step 1: Create `components/Sidebar.tsx`**

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, ArrowLeftRight, CreditCard, TrendingUp } from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transacoes", icon: ArrowLeftRight },
  { href: "/credit-cards", label: "Cartoes", icon: CreditCard },
  { href: "/investments", label: "Investimentos", icon: TrendingUp },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-card border-r border-border flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-bold text-primary">FinanceAI</h1>
      </div>
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 2: Update `app/layout.tsx` to include Sidebar**

Wrap children with Sidebar in the layout:
```tsx
import Sidebar from "@/components/Sidebar";

// Inside the <body> tag:
<body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}>
  <div className="flex min-h-screen">
    <Sidebar />
    <main className="flex-1 p-6">{children}</main>
  </div>
</body>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/Sidebar.tsx frontend/app/layout.tsx
git commit -m "feat: sidebar navigation component"
```

---

## Task 13: Dashboard — Summary Cards + Alerts Panel

**Files:**
- Create: `financeai/frontend/components/SummaryCards.tsx`
- Create: `financeai/frontend/components/AlertsPanel.tsx`
- Modify: `financeai/frontend/app/page.tsx`

- [ ] **Step 1: Create `components/SummaryCards.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, TrendingUp, TrendingDown, PiggyBank } from "lucide-react";
import api from "@/lib/api";

interface Summary {
  income: number;
  expenses: number;
  balance: number;
  total_invested: number;
  total_current: number;
}

export default function SummaryCards() {
  const [data, setData] = useState<Summary | null>(null);

  useEffect(() => {
    api.get("/summary/monthly").then((res) => setData(res.data));
  }, []);

  if (!data) return null;

  const cards = [
    { title: "Saldo do Mes", value: data.balance, icon: DollarSign, color: data.balance >= 0 ? "text-emerald-500" : "text-red-500" },
    { title: "Receitas", value: data.income, icon: TrendingUp, color: "text-emerald-500" },
    { title: "Despesas", value: data.expenses, icon: TrendingDown, color: "text-red-500" },
    { title: "Investido", value: data.total_current, icon: PiggyBank, color: "text-blue-500" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${card.color}`}>
              R$ {card.value.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create `components/AlertsPanel.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";
import api from "@/lib/api";

interface Alert {
  id: string;
  message: string;
  level: string;
  due_date: string | null;
  amount: number | null;
  source: string;
}

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    api.get("/alerts").then((res) => setAlerts(res.data));
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <AlertTriangle className="h-4 w-4" />
          Alertas
        </CardTitle>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nenhum alerta ativo</p>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start gap-3">
                <Badge variant={alert.level === "danger" ? "destructive" : "secondary"}>
                  {alert.level === "danger" ? "Vencida" : "Aviso"}
                </Badge>
                <p className="text-sm">{alert.message}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 3: Update `app/page.tsx`**

Replace `financeai/frontend/app/page.tsx`:
```tsx
import SummaryCards from "@/components/SummaryCards";
import AlertsPanel from "@/components/AlertsPanel";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <SummaryCards />
      <AlertsPanel />
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/components/SummaryCards.tsx frontend/components/AlertsPanel.tsx frontend/app/page.tsx
git commit -m "feat: dashboard with summary cards and alerts panel"
```

---

## Task 14: Dashboard — Charts

**Files:**
- Create: `financeai/frontend/components/SpendingChart.tsx`
- Modify: `financeai/frontend/app/page.tsx`

- [ ] **Step 1: Create `components/SpendingChart.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
} from "recharts";
import api from "@/lib/api";

const COLORS = [
  "#10b981", "#f59e0b", "#ef4444", "#3b82f6",
  "#8b5cf6", "#ec4899", "#14b8a6", "#f97316",
  "#6366f1", "#84cc16",
];

const MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

export default function SpendingChart() {
  const [categoryData, setCategoryData] = useState<{ name: string; value: number }[]>([]);
  const [yearlyData, setYearlyData] = useState<{ name: string; receitas: number; despesas: number }[]>([]);

  useEffect(() => {
    api.get("/summary/monthly").then((res) => {
      const byCategory = res.data.by_category as Record<string, number>;
      setCategoryData(
        Object.entries(byCategory).map(([name, value]) => ({ name, value }))
      );
    });

    api.get("/summary/yearly").then((res) => {
      setYearlyData(
        res.data.months.map((m: { month: number; income: number; expenses: number }) => ({
          name: MONTH_LABELS[m.month - 1],
          receitas: m.income,
          despesas: m.expenses,
        }))
      );
    });
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Gastos por Categoria</CardTitle>
        </CardHeader>
        <CardContent>
          {categoryData.length === 0 ? (
            <p className="text-sm text-muted-foreground">Sem dados</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `R$ ${value.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Receitas x Despesas (Anual)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={yearlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip formatter={(value: number) => `R$ ${value.toFixed(2)}`} />
              <Legend />
              <Bar dataKey="receitas" fill="#10b981" />
              <Bar dataKey="despesas" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Update `app/page.tsx` to include charts**

```tsx
import SummaryCards from "@/components/SummaryCards";
import SpendingChart from "@/components/SpendingChart";
import AlertsPanel from "@/components/AlertsPanel";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <SummaryCards />
      <SpendingChart />
      <AlertsPanel />
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/SpendingChart.tsx frontend/app/page.tsx
git commit -m "feat: pie and bar charts for spending visualization"
```

---

## Task 15: Transactions Page

**Files:**
- Create: `financeai/frontend/app/transactions/page.tsx`

- [ ] **Step 1: Create `app/transactions/page.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Pencil } from "lucide-react";
import api from "@/lib/api";

const CATEGORIES = [
  "Alimentacao", "Moradia", "Transporte", "Saude", "Lazer",
  "Educacao", "Salario", "Freelance", "Investimento", "Outros",
];

interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: string;
  category: string;
  status: string;
  due_date: string | null;
  paid_date: string | null;
  notes: string | null;
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    description: "", amount: "", type: "expense", category: "Outros",
    status: "pending", due_date: "", paid_date: "", notes: "",
  });
  const [filterType, setFilterType] = useState<string>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const load = () => {
    const params: Record<string, string> = {};
    if (filterType !== "all") params.type = filterType;
    if (filterCategory !== "all") params.category = filterCategory;
    api.get("/transactions", { params }).then((res) => setTransactions(res.data));
  };

  useEffect(() => { load(); }, [filterType, filterCategory]);

  const resetForm = () => {
    setForm({ description: "", amount: "", type: "expense", category: "Outros", status: "pending", due_date: "", paid_date: "", notes: "" });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      description: form.description,
      amount: parseFloat(form.amount),
      type: form.type,
      category: form.category,
      status: form.status,
    };
    if (form.due_date) data.due_date = form.due_date;
    if (form.paid_date) data.paid_date = form.paid_date;
    if (form.notes) data.notes = form.notes;

    if (editingId) {
      await api.put(`/transactions/${editingId}`, data);
    } else {
      await api.post("/transactions", data);
    }
    setOpen(false);
    resetForm();
    load();
  };

  const handleEdit = (t: Transaction) => {
    setForm({
      description: t.description, amount: String(t.amount), type: t.type,
      category: t.category, status: t.status, due_date: t.due_date || "",
      paid_date: t.paid_date || "", notes: t.notes || "",
    });
    setEditingId(t.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    await api.delete(`/transactions/${id}`);
    load();
  };

  const statusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive"> = {
      paid: "default", pending: "secondary", overdue: "destructive",
    };
    const labels: Record<string, string> = { paid: "Pago", pending: "Pendente", overdue: "Vencido" };
    return <Badge variant={variants[status] || "secondary"}>{labels[status] || status}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Transacoes</h2>
        <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) resetForm(); }}>
          <DialogTrigger asChild>
            <Button><Plus className="h-4 w-4 mr-2" />Adicionar</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingId ? "Editar" : "Nova"} Transacao</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div><Label>Descricao</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <div><Label>Valor</Label><Input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Tipo</Label>
                  <Select value={form.type} onValueChange={(v) => setForm({ ...form, type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent><SelectItem value="income">Receita</SelectItem><SelectItem value="expense">Despesa</SelectItem></SelectContent>
                  </Select>
                </div>
                <div><Label>Categoria</Label>
                  <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Status</Label>
                  <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent><SelectItem value="pending">Pendente</SelectItem><SelectItem value="paid">Pago</SelectItem><SelectItem value="overdue">Vencido</SelectItem></SelectContent>
                  </Select>
                </div>
                <div><Label>Vencimento</Label><Input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></div>
              </div>
              <div><Label>Data Pagamento</Label><Input type="date" value={form.paid_date} onChange={(e) => setForm({ ...form, paid_date: e.target.value })} /></div>
              <div><Label>Observacoes</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
              <Button className="w-full" onClick={handleSubmit}>{editingId ? "Salvar" : "Criar"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex gap-4">
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Tipo" /></SelectTrigger>
          <SelectContent><SelectItem value="all">Todos</SelectItem><SelectItem value="income">Receitas</SelectItem><SelectItem value="expense">Despesas</SelectItem></SelectContent>
        </Select>
        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Categoria" /></SelectTrigger>
          <SelectContent><SelectItem value="all">Todas</SelectItem>{CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Descricao</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Vencimento</TableHead>
                <TableHead className="w-20">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.description}</TableCell>
                  <TableCell className={t.type === "income" ? "text-emerald-500" : "text-red-500"}>
                    R$ {t.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell>{t.type === "income" ? "Receita" : "Despesa"}</TableCell>
                  <TableCell>{t.category}</TableCell>
                  <TableCell>{statusBadge(t.status)}</TableCell>
                  <TableCell>{t.due_date || "-"}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEdit(t)}><Pencil className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(t.id)}><Trash2 className="h-4 w-4" /></Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/app/transactions/
git commit -m "feat: transactions page with CRUD, filters, and status badges"
```

---

## Task 16: Credit Cards Page

**Files:**
- Create: `financeai/frontend/app/credit-cards/page.tsx`

- [ ] **Step 1: Create `app/credit-cards/page.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, ChevronDown, ChevronRight } from "lucide-react";
import api from "@/lib/api";

interface CreditCard {
  id: string;
  name: string;
  bank: string;
  limit_amount: number;
  closing_day: number;
  due_day: number;
}

interface Invoice {
  id: string;
  card_id: string;
  month: number;
  year: number;
  total_amount: number;
  status: string;
  due_date: string | null;
}

interface Expense {
  id: string;
  invoice_id: string;
  description: string;
  amount: number;
  category: string;
  expense_date: string;
  installments: number;
  installment_number: number;
}

export default function CreditCardsPage() {
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [openCard, setOpenCard] = useState(false);
  const [cardForm, setCardForm] = useState({ name: "", bank: "", limit_amount: "", closing_day: "", due_day: "" });
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [invoices, setInvoices] = useState<Record<string, Invoice[]>>({});
  const [expandedInvoice, setExpandedInvoice] = useState<string | null>(null);
  const [expenses, setExpenses] = useState<Record<string, Expense[]>>({});
  const [openInvoice, setOpenInvoice] = useState(false);
  const [invoiceForm, setInvoiceForm] = useState({ month: "", year: "", due_date: "" });
  const [invoiceCardId, setInvoiceCardId] = useState("");
  const [openExpense, setOpenExpense] = useState(false);
  const [expenseForm, setExpenseForm] = useState({ description: "", amount: "", category: "Outros", expense_date: "", installments: "1", installment_number: "1" });
  const [expenseInvoice, setExpenseInvoice] = useState({ cardId: "", invoiceId: "" });

  const loadCards = () => api.get("/credit-cards").then((res) => setCards(res.data));
  useEffect(() => { loadCards(); }, []);

  const loadInvoices = async (cardId: string) => {
    const res = await api.get(`/credit-cards/${cardId}/invoices`);
    setInvoices((prev) => ({ ...prev, [cardId]: res.data }));
  };

  const loadExpenses = async (cardId: string, invoiceId: string) => {
    const res = await api.get(`/credit-cards/${cardId}/invoices/${invoiceId}/expenses`);
    setExpenses((prev) => ({ ...prev, [invoiceId]: res.data }));
  };

  const toggleCard = (cardId: string) => {
    if (expandedCard === cardId) {
      setExpandedCard(null);
    } else {
      setExpandedCard(cardId);
      loadInvoices(cardId);
    }
  };

  const toggleInvoice = (cardId: string, invoiceId: string) => {
    if (expandedInvoice === invoiceId) {
      setExpandedInvoice(null);
    } else {
      setExpandedInvoice(invoiceId);
      loadExpenses(cardId, invoiceId);
    }
  };

  const createCard = async () => {
    await api.post("/credit-cards", {
      name: cardForm.name, bank: cardForm.bank,
      limit_amount: parseFloat(cardForm.limit_amount),
      closing_day: parseInt(cardForm.closing_day),
      due_day: parseInt(cardForm.due_day),
    });
    setOpenCard(false);
    setCardForm({ name: "", bank: "", limit_amount: "", closing_day: "", due_day: "" });
    loadCards();
  };

  const deleteCard = async (id: string) => {
    await api.delete(`/credit-cards/${id}`);
    loadCards();
  };

  const createInvoice = async () => {
    await api.post(`/credit-cards/${invoiceCardId}/invoices`, {
      card_id: invoiceCardId,
      month: parseInt(invoiceForm.month),
      year: parseInt(invoiceForm.year),
      due_date: invoiceForm.due_date || null,
    });
    setOpenInvoice(false);
    setInvoiceForm({ month: "", year: "", due_date: "" });
    loadInvoices(invoiceCardId);
  };

  const createExpense = async () => {
    const { cardId, invoiceId } = expenseInvoice;
    await api.post(`/credit-cards/${cardId}/invoices/${invoiceId}/expenses`, {
      invoice_id: invoiceId,
      description: expenseForm.description,
      amount: parseFloat(expenseForm.amount),
      category: expenseForm.category,
      expense_date: expenseForm.expense_date,
      installments: parseInt(expenseForm.installments),
      installment_number: parseInt(expenseForm.installment_number),
    });
    setOpenExpense(false);
    setExpenseForm({ description: "", amount: "", category: "Outros", expense_date: "", installments: "1", installment_number: "1" });
    loadExpenses(cardId, invoiceId);
    loadInvoices(cardId);
  };

  const invoiceStatus = (status: string) => {
    const map: Record<string, "default" | "secondary" | "destructive"> = { paid: "default", open: "secondary", closed: "destructive" };
    const labels: Record<string, string> = { paid: "Paga", open: "Aberta", closed: "Fechada" };
    return <Badge variant={map[status] || "secondary"}>{labels[status] || status}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Cartoes de Credito</h2>
        <Dialog open={openCard} onOpenChange={setOpenCard}>
          <DialogTrigger asChild><Button><Plus className="h-4 w-4 mr-2" />Novo Cartao</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Novo Cartao</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div><Label>Nome</Label><Input value={cardForm.name} onChange={(e) => setCardForm({ ...cardForm, name: e.target.value })} /></div>
              <div><Label>Banco</Label><Input value={cardForm.bank} onChange={(e) => setCardForm({ ...cardForm, bank: e.target.value })} /></div>
              <div><Label>Limite</Label><Input type="number" value={cardForm.limit_amount} onChange={(e) => setCardForm({ ...cardForm, limit_amount: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Dia Fechamento</Label><Input type="number" value={cardForm.closing_day} onChange={(e) => setCardForm({ ...cardForm, closing_day: e.target.value })} /></div>
                <div><Label>Dia Vencimento</Label><Input type="number" value={cardForm.due_day} onChange={(e) => setCardForm({ ...cardForm, due_day: e.target.value })} /></div>
              </div>
              <Button className="w-full" onClick={createCard}>Criar</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Invoice dialog */}
      <Dialog open={openInvoice} onOpenChange={setOpenInvoice}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nova Fatura</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Mes</Label><Input type="number" min="1" max="12" value={invoiceForm.month} onChange={(e) => setInvoiceForm({ ...invoiceForm, month: e.target.value })} /></div>
              <div><Label>Ano</Label><Input type="number" value={invoiceForm.year} onChange={(e) => setInvoiceForm({ ...invoiceForm, year: e.target.value })} /></div>
            </div>
            <div><Label>Vencimento</Label><Input type="date" value={invoiceForm.due_date} onChange={(e) => setInvoiceForm({ ...invoiceForm, due_date: e.target.value })} /></div>
            <Button className="w-full" onClick={createInvoice}>Criar</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Expense dialog */}
      <Dialog open={openExpense} onOpenChange={setOpenExpense}>
        <DialogContent>
          <DialogHeader><DialogTitle>Novo Lancamento</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><Label>Descricao</Label><Input value={expenseForm.description} onChange={(e) => setExpenseForm({ ...expenseForm, description: e.target.value })} /></div>
            <div><Label>Valor</Label><Input type="number" step="0.01" value={expenseForm.amount} onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })} /></div>
            <div><Label>Categoria</Label><Input value={expenseForm.category} onChange={(e) => setExpenseForm({ ...expenseForm, category: e.target.value })} /></div>
            <div><Label>Data</Label><Input type="date" value={expenseForm.expense_date} onChange={(e) => setExpenseForm({ ...expenseForm, expense_date: e.target.value })} /></div>
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Parcelas</Label><Input type="number" value={expenseForm.installments} onChange={(e) => setExpenseForm({ ...expenseForm, installments: e.target.value })} /></div>
              <div><Label>Parcela N</Label><Input type="number" value={expenseForm.installment_number} onChange={(e) => setExpenseForm({ ...expenseForm, installment_number: e.target.value })} /></div>
            </div>
            <Button className="w-full" onClick={createExpense}>Criar</Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="space-y-4">
        {cards.map((card) => (
          <Card key={card.id}>
            <CardHeader className="cursor-pointer" onClick={() => toggleCard(card.id)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {expandedCard === card.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  <CardTitle className="text-base">{card.name} — {card.bank}</CardTitle>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-muted-foreground">Limite: R$ {card.limit_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</span>
                  <span className="text-sm text-muted-foreground">Fecha dia {card.closing_day} | Vence dia {card.due_day}</span>
                  <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); deleteCard(card.id); }}><Trash2 className="h-4 w-4" /></Button>
                </div>
              </div>
            </CardHeader>
            {expandedCard === card.id && (
              <CardContent>
                <div className="flex justify-end mb-4">
                  <Button size="sm" variant="outline" onClick={() => { setInvoiceCardId(card.id); setOpenInvoice(true); }}>
                    <Plus className="h-4 w-4 mr-1" />Fatura
                  </Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Periodo</TableHead>
                      <TableHead>Total</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Vencimento</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(invoices[card.id] || []).map((inv) => (
                      <>
                        <TableRow key={inv.id} className="cursor-pointer" onClick={() => toggleInvoice(card.id, inv.id)}>
                          <TableCell className="flex items-center gap-2">
                            {expandedInvoice === inv.id ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                            {inv.month}/{inv.year}
                          </TableCell>
                          <TableCell>R$ {inv.total_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                          <TableCell>{invoiceStatus(inv.status)}</TableCell>
                          <TableCell>{inv.due_date || "-"}</TableCell>
                        </TableRow>
                        {expandedInvoice === inv.id && (
                          <TableRow>
                            <TableCell colSpan={4} className="bg-muted/50 p-4">
                              <div className="flex justify-end mb-2">
                                <Button size="sm" variant="outline" onClick={() => { setExpenseInvoice({ cardId: card.id, invoiceId: inv.id }); setOpenExpense(true); }}>
                                  <Plus className="h-3 w-3 mr-1" />Lancamento
                                </Button>
                              </div>
                              <Table>
                                <TableHeader>
                                  <TableRow>
                                    <TableHead>Descricao</TableHead>
                                    <TableHead>Valor</TableHead>
                                    <TableHead>Categoria</TableHead>
                                    <TableHead>Data</TableHead>
                                    <TableHead>Parcela</TableHead>
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {(expenses[inv.id] || []).map((exp) => (
                                    <TableRow key={exp.id}>
                                      <TableCell>{exp.description}</TableCell>
                                      <TableCell>R$ {exp.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                                      <TableCell>{exp.category}</TableCell>
                                      <TableCell>{exp.expense_date}</TableCell>
                                      <TableCell>{exp.installment_number}/{exp.installments}</TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </TableCell>
                          </TableRow>
                        )}
                      </>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/app/credit-cards/
git commit -m "feat: credit cards page with expandable invoices and expenses"
```

---

## Task 17: Investments Page

**Files:**
- Create: `financeai/frontend/app/investments/page.tsx`

- [ ] **Step 1: Create `app/investments/page.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Pencil } from "lucide-react";
import api from "@/lib/api";

interface Investment {
  id: string;
  name: string;
  type: string;
  institution: string;
  invested_amount: number;
  current_amount: number;
  start_date: string;
  maturity_date: string | null;
  notes: string | null;
}

export default function InvestmentsPage() {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "", type: "", institution: "", invested_amount: "",
    current_amount: "", start_date: "", maturity_date: "", notes: "",
  });

  const load = () => api.get("/investments").then((res) => setInvestments(res.data));
  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setForm({ name: "", type: "", institution: "", invested_amount: "", current_amount: "", start_date: "", maturity_date: "", notes: "" });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      name: form.name, type: form.type, institution: form.institution,
      invested_amount: parseFloat(form.invested_amount),
      current_amount: parseFloat(form.current_amount),
      start_date: form.start_date,
    };
    if (form.maturity_date) data.maturity_date = form.maturity_date;
    if (form.notes) data.notes = form.notes;

    if (editingId) {
      await api.put(`/investments/${editingId}`, data);
    } else {
      await api.post("/investments", data);
    }
    setOpen(false);
    resetForm();
    load();
  };

  const handleEdit = (inv: Investment) => {
    setForm({
      name: inv.name, type: inv.type, institution: inv.institution,
      invested_amount: String(inv.invested_amount), current_amount: String(inv.current_amount),
      start_date: inv.start_date, maturity_date: inv.maturity_date || "", notes: inv.notes || "",
    });
    setEditingId(inv.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    await api.delete(`/investments/${id}`);
    load();
  };

  const totalInvested = investments.reduce((s, i) => s + i.invested_amount, 0);
  const totalCurrent = investments.reduce((s, i) => s + i.current_amount, 0);
  const totalReturn = totalCurrent - totalInvested;
  const returnPct = totalInvested > 0 ? ((totalReturn / totalInvested) * 100).toFixed(2) : "0.00";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Investimentos</h2>
        <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) resetForm(); }}>
          <DialogTrigger asChild><Button><Plus className="h-4 w-4 mr-2" />Adicionar</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>{editingId ? "Editar" : "Novo"} Investimento</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div><Label>Nome</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Tipo</Label><Input value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} placeholder="CDB, Acoes, FII..." /></div>
                <div><Label>Instituicao</Label><Input value={form.institution} onChange={(e) => setForm({ ...form, institution: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Valor Investido</Label><Input type="number" step="0.01" value={form.invested_amount} onChange={(e) => setForm({ ...form, invested_amount: e.target.value })} /></div>
                <div><Label>Valor Atual</Label><Input type="number" step="0.01" value={form.current_amount} onChange={(e) => setForm({ ...form, current_amount: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Data Inicio</Label><Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></div>
                <div><Label>Vencimento</Label><Input type="date" value={form.maturity_date} onChange={(e) => setForm({ ...form, maturity_date: e.target.value })} /></div>
              </div>
              <div><Label>Observacoes</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
              <Button className="w-full" onClick={handleSubmit}>{editingId ? "Salvar" : "Criar"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Total Investido</p><p className="text-2xl font-bold text-blue-500">R$ {totalInvested.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</p></CardContent></Card>
        <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Valor Atual</p><p className="text-2xl font-bold text-blue-500">R$ {totalCurrent.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</p></CardContent></Card>
        <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Retorno</p><p className={`text-2xl font-bold ${totalReturn >= 0 ? "text-emerald-500" : "text-red-500"}`}>R$ {totalReturn.toLocaleString("pt-BR", { minimumFractionDigits: 2 })} ({returnPct}%)</p></CardContent></Card>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Instituicao</TableHead>
                <TableHead>Investido</TableHead>
                <TableHead>Atual</TableHead>
                <TableHead>Retorno</TableHead>
                <TableHead>Inicio</TableHead>
                <TableHead className="w-20">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {investments.map((inv) => {
                const ret = inv.current_amount - inv.invested_amount;
                return (
                  <TableRow key={inv.id}>
                    <TableCell>{inv.name}</TableCell>
                    <TableCell>{inv.type}</TableCell>
                    <TableCell>{inv.institution}</TableCell>
                    <TableCell>R$ {inv.invested_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell>R$ {inv.current_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell className={ret >= 0 ? "text-emerald-500" : "text-red-500"}>
                      R$ {ret.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell>{inv.start_date}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleEdit(inv)}><Pencil className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(inv.id)}><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/app/investments/
git commit -m "feat: investments page with CRUD and return calculations"
```

---

## Task 18: Chat Component

**Files:**
- Create: `financeai/frontend/components/Chat.tsx`
- Modify: `financeai/frontend/app/layout.tsx` (add Chat)

- [ ] **Step 1: Create `components/Chat.tsx`**

```tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageCircle, X, Send } from "lucide-react";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      api.get("/chat/history").then((res) => {
        if (res.data.length > 0) {
          setMessages(res.data.map((m: { role: string; content: string }) => ({ role: m.role, content: m.content })));
        }
      });
    }
  }, [isOpen]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", content: input.trim() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/chat", { message: userMsg.content, history: messages });
      setMessages([...updated, { role: "assistant", content: res.data.response }]);
    } catch {
      setMessages([...updated, { role: "assistant", content: "Erro ao conectar com a IA. Tente novamente." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-lg hover:opacity-90 transition-opacity z-50"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-0 right-0 w-[400px] h-[600px] bg-card border-l border-t border-border flex flex-col z-50 shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h3 className="font-semibold">Assistente Financeiro</h3>
            <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <p className="text-sm text-muted-foreground text-center mt-8">
                Pergunte sobre suas financas!
              </p>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-3 py-2 text-sm text-muted-foreground">
                  Digitando...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-border flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Digite sua mensagem..."
              disabled={loading}
            />
            <Button size="icon" onClick={send} disabled={loading}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </>
  );
}
```

- [ ] **Step 2: Add Chat to layout**

In `financeai/frontend/app/layout.tsx`, add inside the `<body>` after the flex container:
```tsx
import Chat from "@/components/Chat";

// Inside body, after the flex div:
<div className="flex min-h-screen">
  <Sidebar />
  <main className="flex-1 p-6">{children}</main>
</div>
<Chat />
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/Chat.tsx frontend/app/layout.tsx
git commit -m "feat: floating AI chat component with financial context"
```

---

## Task 19: Final Integration and Verification

- [ ] **Step 1: Verify backend starts without errors**

```bash
cd "f:/Financeiro Pessoal/financeai/backend"
uvicorn main:app --reload --port 8000
```

Check `http://localhost:8000/docs` for Swagger UI with all endpoints.

- [ ] **Step 2: Verify frontend starts without errors**

```bash
cd "f:/Financeiro Pessoal/financeai/frontend"
npm run dev
```

Open `http://localhost:3000` and verify:
- Sidebar navigation works
- Dashboard loads summary cards (all zeros if no data)
- Charts render (empty state)
- Alerts panel shows (empty state)
- Chat button appears in bottom right
- Chat opens and can send/receive messages
- Transactions page: can create, edit, delete transactions
- Credit cards page: can create cards, add invoices, add expenses
- Investments page: can create, edit, delete investments

- [ ] **Step 3: Add test data via API**

```bash
# Add a transaction
curl -X POST http://localhost:8000/api/transactions/ -H "Content-Type: application/json" -d '{"description":"Salario Abril","amount":8000,"type":"income","category":"Salario","due_date":"2026-04-05","status":"paid","paid_date":"2026-04-05"}'

# Add an expense
curl -X POST http://localhost:8000/api/transactions/ -H "Content-Type: application/json" -d '{"description":"Aluguel","amount":2500,"type":"expense","category":"Moradia","due_date":"2026-04-10","status":"pending"}'

# Verify dashboard updates
```

- [ ] **Step 4: Test chat with AI**

Open the chat and ask: "Como estao minhas financas este mes?"
The AI should respond with context about the current financial data.

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: FinanceAI v1.0 - complete personal finance system with AI chat"
```
