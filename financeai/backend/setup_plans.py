"""Create financial_plans table in Supabase."""
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SQL = """
CREATE TABLE IF NOT EXISTS financial_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  month INTEGER NOT NULL,
  year INTEGER NOT NULL,
  title TEXT NOT NULL,
  content JSONB,
  observations TEXT,
  status TEXT CHECK (status IN ('planejado', 'em_andamento', 'concluido')) DEFAULT 'planejado',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
"""

# Try via PostgREST (won't work, but try)
# Actually use the Supabase client to check if table exists
from database import supabase

try:
    result = supabase.table("financial_plans").select("id").limit(1).execute()
    print("Tabela financial_plans ja existe!")
except Exception as e:
    if "PGRST205" in str(e):
        print("Tabela nao existe. Crie manualmente no Supabase Dashboard:")
        print(f"  https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new")
        print()
        print("Cole este SQL:")
        print(SQL)
    else:
        print(f"Erro: {e}")
