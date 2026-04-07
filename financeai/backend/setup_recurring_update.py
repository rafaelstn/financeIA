"""
Migration: Add business day support to recurring_transactions.

Run the SQL below in Supabase Dashboard (SQL Editor):
------------------------------------------------------

ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS use_business_day BOOLEAN DEFAULT false;
ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS business_day_number INTEGER;

------------------------------------------------------

use_business_day: When true, the recurring transaction uses the Nth business day
                  of the month instead of a fixed calendar day.
business_day_number: Which business day (e.g., 5 = 5th business day of the month).
"""

SQL = """
ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS use_business_day BOOLEAN DEFAULT false;
ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS business_day_number INTEGER;
"""

if __name__ == "__main__":
    print("Execute o SQL abaixo no Supabase Dashboard (SQL Editor):\n")
    print(SQL)
    print("Depois de executar, as colunas use_business_day e business_day_number")
    print("estarao disponiveis na tabela recurring_transactions.")
