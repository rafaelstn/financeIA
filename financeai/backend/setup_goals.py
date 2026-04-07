"""
Script para criar a tabela 'goals' no Supabase.

Como usar:
1. Acesse o SQL Editor do Supabase:
   https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new
2. Cole o SQL abaixo e execute.
"""

SQL = """
CREATE TABLE IF NOT EXISTS goals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  target_amount DECIMAL(10,2) NOT NULL,
  saved_amount DECIMAL(10,2) DEFAULT 0,
  priority TEXT CHECK (priority IN ('alta', 'media', 'baixa')) DEFAULT 'media',
  category TEXT CHECK (category IN ('eletronico', 'veiculo', 'imovel', 'viagem', 'educacao', 'saude', 'lazer', 'outros')) NOT NULL,
  status TEXT CHECK (status IN ('ativa', 'pausada', 'concluida', 'cancelada')) DEFAULT 'ativa',
  target_date DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
"""

if __name__ == "__main__":
    print("=" * 60)
    print("CRIAR TABELA 'goals' NO SUPABASE")
    print("=" * 60)
    print()
    print("Acesse o SQL Editor:")
    print("https://supabase.com/dashboard/project/fvpijszqtevhtjbagzba/sql/new")
    print()
    print("Cole e execute o seguinte SQL:")
    print(SQL)
