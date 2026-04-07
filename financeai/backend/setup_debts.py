"""
Script para criar a tabela 'debts' no Supabase.

Como usar:
1. Acesse o SQL Editor do Supabase:
   https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new
2. Cole o SQL abaixo e execute.
"""

SQL = """
CREATE TABLE IF NOT EXISTS debts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  creditor TEXT NOT NULL,
  original_amount DECIMAL(10,2) NOT NULL,
  current_amount DECIMAL(10,2) NOT NULL,
  category TEXT CHECK (category IN ('cartao', 'emprestimo', 'financiamento', 'cheque_especial', 'conta_consumo', 'outros')) NOT NULL,
  status TEXT CHECK (status IN ('ativa', 'negociando', 'acordo', 'quitada', 'prescrita')) DEFAULT 'ativa',
  origin_date DATE NOT NULL,
  is_paying BOOLEAN DEFAULT false,
  monthly_payment DECIMAL(10,2),
  payment_day INTEGER,
  total_installments INTEGER,
  paid_installments INTEGER DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
"""

if __name__ == "__main__":
    print("=" * 60)
    print("CRIAR TABELA 'debts' NO SUPABASE")
    print("=" * 60)
    print()
    print("Acesse o SQL Editor:")
    print("https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new")
    print()
    print("Cole e execute o seguinte SQL:")
    print(SQL)
