"""
Script to create database tables in Supabase.
Run this once to initialize the schema.
"""
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SQL = """
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
"""

def run_sql_via_management_api():
    """Try Supabase Management API to run SQL."""
    # Extract project ref from URL
    project_ref = SUPABASE_URL.replace("https://", "").split(".")[0]
    management_url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"query": SQL}

    try:
        response = httpx.post(management_url, headers=headers, json=payload, timeout=30)
        print(f"Management API response: {response.status_code}")
        print(response.text[:500])
        return response.status_code < 300
    except Exception as e:
        print(f"Management API error: {e}")
        return False


def verify_tables():
    """Verify which tables exist using supabase-py."""
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    tables = [
        "transactions",
        "credit_cards",
        "card_invoices",
        "card_expenses",
        "investments",
        "chat_history",
        "settings",
    ]

    print("\n--- Table Verification ---")
    all_exist = True
    for table in tables:
        try:
            client.table(table).select("*").limit(1).execute()
            print(f"  [OK] {table}")
        except Exception as e:
            print(f"  [MISSING] {table}: {e}")
            all_exist = False

    return all_exist


if __name__ == "__main__":
    print("=== FinanceAI Database Setup ===\n")
    print("Attempting to create tables via Supabase Management API...")
    success = run_sql_via_management_api()

    if success:
        print("\nSQL executed successfully via Management API.")
    else:
        print("\nManagement API failed. Verifying existing tables...")

    all_ok = verify_tables()

    if not all_ok:
        print("\n[ACTION REQUIRED] Some tables are missing.")
        print("Run the following SQL in your Supabase Dashboard SQL Editor:")
        print("  https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new")
        print("\n" + "="*60)
        print(SQL)
        print("="*60)
    else:
        print("\nAll tables verified. Database is ready.")
