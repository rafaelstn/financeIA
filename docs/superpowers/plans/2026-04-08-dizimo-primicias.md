# Dízimo & Primícias — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Calcular automaticamente dízimo (10%) e primícia (1 dia de trabalho) sobre receitas do mês, criando transações de despesa e exibindo no dashboard.

**Architecture:** Serviço Python `tithe_service.py` centraliza a lógica de cálculo e criação/atualização de transações. Os endpoints de transações chamam esse serviço como side-effect ao criar/editar/deletar receitas. O summary retorna os valores calculados. Frontend adiciona 2 cards novos ao SummaryCards.

**Tech Stack:** Python/FastAPI, Supabase, Next.js/React, TypeScript, Lucide icons

**Spec:** `docs/superpowers/specs/2026-04-08-dizimo-primicias-design.md`

---

## Estrutura de Arquivos

| Ação | Arquivo | Responsabilidade |
|------|---------|------------------|
| Criar | `backend/services/tithe_service.py` | Lógica de cálculo e sync de dízimo/primícia |
| Modificar | `backend/routes/transactions.py` | Chamar tithe_service após CRUD de income |
| Modificar | `backend/routes/summary.py:61-71` | Adicionar tithe/firstfruits ao response |
| Modificar | `frontend/components/SummaryCards.tsx` | 2 cards novos, grid 6 colunas |

---

### Task 1: Criar `tithe_service.py`

**Files:**
- Create: `backend/services/tithe_service.py`

- [ ] **Step 1: Criar o serviço com a função de sync**

Criar `backend/services/tithe_service.py`:

```python
import math
from database import supabase

TITHE_CATEGORIES = ("Dizimo", "Primicia")
MONTH_NAMES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def sync_tithe_and_firstfruits(month: int, year: int) -> None:
    """Recalcula e sincroniza as transações de dízimo e primícia do mês."""
    start = f"{year}-{month:02d}-01"
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = f"{end_year}-{end_month:02d}-01"

    # Soma todas as receitas do mês
    income_txns = (
        supabase.table("transactions")
        .select("amount")
        .eq("type", "income")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data
    total_income = sum(t["amount"] for t in income_txns)

    month_name = MONTH_NAMES[month]
    label = f"{month_name}/{year}"
    # Último dia do mês como due_date
    last_day = f"{end_year}-{end_month:02d}-01"

    tithe_amount = round(total_income * 0.10, 2)
    firstfruits_amount = math.ceil(total_income / 30) if total_income > 0 else 0

    items = [
        {"category": "Dizimo", "description": f"Dízimo - {label}", "amount": tithe_amount},
        {"category": "Primicia", "description": f"Primícia - {label}", "amount": firstfruits_amount},
    ]

    for item in items:
        _upsert_tithe_transaction(item, month, year, start, end, last_day, total_income)


def _upsert_tithe_transaction(
    item: dict, month: int, year: int, start: str, end: str, last_day: str, total_income: float
) -> None:
    """Cria, atualiza ou remove uma transação de dízimo/primícia."""
    existing = (
        supabase.table("transactions")
        .select("id, status")
        .eq("type", "expense")
        .eq("category", item["category"])
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    if total_income <= 0:
        # Remove se não há receita
        for txn in existing:
            supabase.table("transactions").delete().eq("id", txn["id"]).execute()
        return

    if existing:
        # Atualiza amount, preserva status (pode já estar "paid")
        supabase.table("transactions").update({
            "amount": item["amount"],
            "description": item["description"],
        }).eq("id", existing[0]["id"]).execute()
    else:
        # Cria nova
        from datetime import date as date_type
        import calendar
        last_day_num = calendar.monthrange(year, month)[1]
        due = f"{year}-{month:02d}-{last_day_num}"
        supabase.table("transactions").insert({
            "description": item["description"],
            "amount": item["amount"],
            "type": "expense",
            "category": item["category"],
            "status": "pending",
            "due_date": due,
        }).execute()
```

- [ ] **Step 2: Verificar que o arquivo foi criado corretamente**

Run: `python -c "from services.tithe_service import sync_tithe_and_firstfruits; print('OK')"`
(executar de dentro do diretório `backend/`)

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/services/tithe_service.py
git commit -m "feat: add tithe_service for dizimo and primicia calculation"
```

---

### Task 2: Integrar tithe_service nos endpoints de transações

**Files:**
- Modify: `backend/routes/transactions.py`

- [ ] **Step 1: Adicionar import e helper para extrair mês/ano**

No topo de `backend/routes/transactions.py`, adicionar:

```python
from services.tithe_service import sync_tithe_and_firstfruits, TITHE_CATEGORIES
from datetime import date as date_type
```

- [ ] **Step 2: Adicionar sync no `create_transaction`**

Após a linha `result = supabase.table("transactions").insert(data).execute()` e antes do `return`, adicionar:

```python
    created = result.data[0]
    if created.get("type") == "income" and created.get("due_date"):
        d = date_type.fromisoformat(created["due_date"])
        sync_tithe_and_firstfruits(d.month, d.year)
    return created
```

E remover o `return result.data[0]` original.

- [ ] **Step 3: Adicionar sync no `update_transaction`**

Após a linha `result = supabase.table("transactions").update(data).eq("id", transaction_id).execute()` e antes do `return`, adicionar:

```python
    updated = result.data[0]
    if updated.get("type") == "income" and updated.get("due_date"):
        d = date_type.fromisoformat(updated["due_date"])
        sync_tithe_and_firstfruits(d.month, d.year)
    return updated
```

E remover o `return result.data[0]` original.

- [ ] **Step 4: Adicionar sync no `delete_transaction`**

No `delete_transaction`, antes de deletar, buscar a transação para saber se é income:

Substituir o corpo inteiro da função por:

```python
async def delete_transaction(transaction_id: str):
    # Busca antes de deletar para saber se precisa recalcular
    existing = supabase.table("transactions").select("type, due_date, category").eq("id", transaction_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Transaction not found")

    txn = existing.data[0]

    # Impede deletar transações automáticas de dízimo/primícia
    if txn.get("category") in TITHE_CATEGORIES:
        raise HTTPException(status_code=400, detail="Transações de dízimo/primícia são gerenciadas automaticamente")

    supabase.table("transactions").delete().eq("id", transaction_id).execute()

    if txn.get("type") == "income" and txn.get("due_date"):
        d = date_type.fromisoformat(txn["due_date"])
        sync_tithe_and_firstfruits(d.month, d.year)

    return {"message": "Transaction deleted"}
```

- [ ] **Step 5: Proteger edição de amount em transações de dízimo/primícia**

No `update_transaction`, adicionar validação no início da função (após o check de `not data`):

```python
    # Verifica se é transação automática — só permite mudar status
    existing_check = supabase.table("transactions").select("category").eq("id", transaction_id).execute()
    if existing_check.data and existing_check.data[0].get("category") in TITHE_CATEGORIES:
        allowed_fields = {"status", "paid_date"}
        if not set(data.keys()).issubset(allowed_fields):
            raise HTTPException(status_code=400, detail="Só é possível alterar o status de transações de dízimo/primícia")
```

- [ ] **Step 6: Commit**

```bash
git add backend/routes/transactions.py
git commit -m "feat: integrate tithe sync on income transaction CRUD"
```

---

### Task 3: Adicionar campos de dízimo/primícia no summary

**Files:**
- Modify: `backend/routes/summary.py:61-71`

- [ ] **Step 1: Extrair valores de dízimo e primícia das transações do mês**

Em `backend/routes/summary.py`, no `monthly_summary`, antes do `return`, adicionar:

```python
    # Dízimo e Primícia
    tithe_txn = next((t for t in txns if t["type"] == "expense" and t["category"] == "Dizimo"), None)
    firstfruits_txn = next((t for t in txns if t["type"] == "expense" and t["category"] == "Primicia"), None)

    tithe = tithe_txn["amount"] if tithe_txn else 0
    tithe_status = tithe_txn["status"] if tithe_txn else "pending"
    firstfruits = firstfruits_txn["amount"] if firstfruits_txn else 0
    firstfruits_status = firstfruits_txn["status"] if firstfruits_txn else "pending"
```

- [ ] **Step 2: Adicionar ao response dict**

Modificar o `return` do `monthly_summary` para incluir os novos campos:

```python
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
        "tithe": tithe,
        "tithe_status": tithe_status,
        "firstfruits": firstfruits,
        "firstfruits_status": firstfruits_status,
    }
```

- [ ] **Step 3: Commit**

```bash
git add backend/routes/summary.py
git commit -m "feat: add tithe and firstfruits to monthly summary response"
```

---

### Task 4: Atualizar SummaryCards no frontend

**Files:**
- Modify: `frontend/components/SummaryCards.tsx`

- [ ] **Step 1: Atualizar interface Summary**

Em `frontend/components/SummaryCards.tsx`, substituir a interface `Summary` por:

```typescript
interface Summary {
  income: number;
  expenses: number;
  balance: number;
  total_invested: number;
  total_current: number;
  tithe: number;
  tithe_status: string;
  firstfruits: number;
  firstfruits_status: string;
}
```

- [ ] **Step 2: Adicionar imports de ícones**

Atualizar o import de lucide-react:

```typescript
import { DollarSign, TrendingUp, TrendingDown, PiggyBank, Heart, Star } from "lucide-react";
```

- [ ] **Step 3: Atualizar o skeleton loading para 6 cards**

Substituir `[...Array(4)]` por `[...Array(6)]` e atualizar as classes do grid:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
  {[...Array(6)].map((_, i) => (
```

- [ ] **Step 4: Adicionar os cards de Dízimo e Primícia ao array**

Substituir o array `cards` por:

```typescript
  const cards = [
    { title: "Saldo do Mês", value: data.balance, icon: DollarSign, color: data.balance >= 0 ? "text-emerald-500" : "text-red-500" },
    { title: "Receitas", value: data.income, icon: TrendingUp, color: "text-emerald-500" },
    { title: "Despesas", value: data.expenses, icon: TrendingDown, color: "text-red-500" },
    { title: "Investido", value: data.total_current, icon: PiggyBank, color: "text-blue-500" },
    { title: "Dízimo", value: data.tithe, icon: Heart, color: "text-purple-500", status: data.tithe_status },
    { title: "Primícia", value: data.firstfruits, icon: Star, color: "text-amber-500", status: data.firstfruits_status },
  ];
```

- [ ] **Step 5: Atualizar o grid e adicionar badge de status**

Substituir o bloco de render por:

```tsx
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
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
            {"status" in card && card.status && (
              <span className={`text-xs mt-1 inline-block px-2 py-0.5 rounded-full ${
                card.status === "paid"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-amber-500/20 text-amber-400"
              }`}>
                {card.status === "paid" ? "Pago" : "Pendente"}
              </span>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
```

- [ ] **Step 6: Commit**

```bash
git add frontend/components/SummaryCards.tsx
git commit -m "feat: add tithe and firstfruits cards to dashboard"
```

---

### Task 5: Teste manual end-to-end

- [ ] **Step 1: Iniciar o backend**

Run: `cd backend && python -m uvicorn main:app --reload`

- [ ] **Step 2: Iniciar o frontend**

Run: `cd frontend && npm run dev`

- [ ] **Step 3: Testar criação de receita**

Via API ou interface, criar uma transação:
```json
{
  "description": "Salário Abril",
  "amount": 3000,
  "type": "income",
  "category": "Salario",
  "due_date": "2026-04-05"
}
```

Expected: Duas transações criadas automaticamente:
- "Dízimo - Abril/2026" = R$300,00 (pending)
- "Primícia - Abril/2026" = R$100,00 (pending)

- [ ] **Step 4: Verificar dashboard**

Acessar `http://localhost:3000`

Expected: 6 cards visíveis, com Dízimo (R$300,00 - Pendente) e Primícia (R$100,00 - Pendente)

- [ ] **Step 5: Testar acumulação**

Criar segunda receita:
```json
{
  "description": "Freelance",
  "amount": 2000,
  "type": "income",
  "category": "Freelance",
  "due_date": "2026-04-15"
}
```

Expected: Dízimo atualiza para R$500,00, Primícia para R$167,00

- [ ] **Step 6: Testar exclusão de receita**

Deletar a receita de Freelance.

Expected: Dízimo volta para R$300,00, Primícia volta para R$100,00

- [ ] **Step 7: Testar marcar como pago**

Na página de transações, editar o Dízimo e mudar status para "paid".

Expected: Card no dashboard muda badge para "Pago"
