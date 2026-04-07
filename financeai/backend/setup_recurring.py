"""
Script para criar as tabelas 'recurring_transactions' e 'budgets' no Supabase.

Como usar:
1. Acesse o SQL Editor do Supabase:
   https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new
2. Cole o SQL abaixo e execute.
"""

SQL = """
CREATE TABLE IF NOT EXISTS recurring_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  description TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  type TEXT CHECK (type IN ('income', 'expense')) NOT NULL,
  category TEXT NOT NULL,
  frequency TEXT CHECK (frequency IN ('monthly', 'weekly', 'yearly')) DEFAULT 'monthly',
  day_of_month INTEGER,
  is_active BOOLEAN DEFAULT true,
  next_due_date DATE NOT NULL,
  notes TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS budgets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  category TEXT NOT NULL UNIQUE,
  monthly_limit DECIMAL(10,2) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now()
);
"""

if __name__ == "__main__":
    print("=" * 60)
    print("CRIAR TABELAS 'recurring_transactions' E 'budgets' NO SUPABASE")
    print("=" * 60)
    print()
    print("Acesse o SQL Editor:")
    print("https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new")
    print()
    print("Cole e execute o seguinte SQL:")
    print(SQL)
