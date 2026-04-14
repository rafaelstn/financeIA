# Planejamento Financeiro — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar página de Planejamento Financeiro onde a IA gera planos mês a mês, o sistema compara planejado vs realizado automaticamente, e o usuário acompanha o histórico.

**Architecture:** Nova tabela `financial_plans` no Supabase, rota `/api/plans` com CRUD + comparison, 2 tools novos no chat (`save_financial_plan`, `get_plan_vs_actual`), página frontend com layout de 2 colunas (plano + chat lateral).

**Tech Stack:** Python/FastAPI, Supabase, Next.js/React, TypeScript, Lucide icons

**Spec:** `docs/superpowers/specs/2026-04-08-planejamento-financeiro-design.md`

---

## Estrutura de Arquivos

| Ação | Arquivo | Responsabilidade |
|------|---------|------------------|
| Criar | `backend/models/plan.py` | Modelo Pydantic |
| Criar | `backend/routes/plans.py` | CRUD + comparison |
| Modificar | `backend/main.py:62-68` | Registrar rota |
| Modificar | `backend/services/chat_tools.py` | 2 tools novos |
| Modificar | `backend/routes/chat.py:14-108` | Contexto do plano no prompt |
| Criar | `frontend/app/planning/page.tsx` | Página principal |
| Criar | `frontend/components/PlanView.tsx` | Renderização do plano |
| Criar | `frontend/components/PlanComparison.tsx` | Planejado vs Realizado |
| Modificar | `frontend/components/Sidebar.tsx:11-19` | Link novo |

---

### Task 1: Modelo Pydantic e tabela

**Files:**
- Create: `backend/models/plan.py`

- [ ] **Step 1: Criar o modelo**

Criar `backend/models/plan.py`:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlanCreate(BaseModel):
    month: int
    year: int
    title: str
    content: dict  # JSON com sections e items
    observations: Optional[str] = None
    status: str = "planejado"  # planejado, em_andamento, concluido


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    observations: Optional[str] = None
    status: Optional[str] = None


class PlanResponse(BaseModel):
    id: str
    month: int
    year: int
    title: str
    content: dict
    observations: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

- [ ] **Step 2: Criar tabela no Supabase**

Executar no SQL Editor do Supabase:

```sql
CREATE TABLE financial_plans (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    month integer NOT NULL,
    year integer NOT NULL,
    title text NOT NULL,
    content jsonb NOT NULL,
    observations text,
    status text NOT NULL DEFAULT 'planejado',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(month, year)
);
```

- [ ] **Step 3: Commit**

```bash
git add backend/models/plan.py
git commit -m "feat: add financial plan model"
```

---

### Task 2: Rota `/api/plans` com CRUD + comparison

**Files:**
- Create: `backend/routes/plans.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Criar a rota completa**

Criar `backend/routes/plans.py`:

```python
from fastapi import APIRouter, HTTPException
from database import supabase
from models.plan import PlanCreate, PlanUpdate
from datetime import date

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("/")
async def list_plans():
    result = (
        supabase.table("financial_plans")
        .select("*")
        .order("year", desc=True)
        .order("month", desc=True)
        .execute()
    )
    return result.data


@router.get("/{month}/{year}")
async def get_plan(month: int, year: int):
    result = (
        supabase.table("financial_plans")
        .select("*")
        .eq("month", month)
        .eq("year", year)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return result.data[0]


@router.post("/", status_code=201)
async def create_plan(plan: PlanCreate):
    data = plan.model_dump(exclude_none=True)
    result = supabase.table("financial_plans").insert(data).execute()
    return result.data[0]


@router.put("/{plan_id}")
async def update_plan(plan_id: str, plan: PlanUpdate):
    data = plan.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = (
        supabase.table("financial_plans")
        .update(data)
        .eq("id", plan_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return result.data[0]


@router.delete("/{plan_id}")
async def delete_plan(plan_id: str):
    result = (
        supabase.table("financial_plans")
        .delete()
        .eq("id", plan_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return {"message": "Plano removido"}


@router.get("/{month}/{year}/comparison")
async def get_plan_comparison(month: int, year: int):
    """Retorna comparativo planejado vs realizado de um mes."""
    # Busca plano
    plan_result = (
        supabase.table("financial_plans")
        .select("*")
        .eq("month", month)
        .eq("year", year)
        .execute()
    )
    plan = plan_result.data[0] if plan_result.data else None

    # Busca dados reais do mes
    start = f"{year}-{month:02d}-01"
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = f"{end_year}-{end_month:02d}-01"

    txns = (
        supabase.table("transactions")
        .select("*")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expenses = sum(t["amount"] for t in txns if t["type"] == "expense")

    by_category: dict[str, float] = {}
    for t in txns:
        if t["type"] == "expense":
            cat = t["category"]
            by_category[cat] = by_category.get(cat, 0) + t["amount"]

    # Dividas quitadas no periodo
    debts = supabase.table("debts").select("creditor, status, current_amount").execute().data
    debts_paid = [d["creditor"] for d in debts if d.get("status") == "quitada"]

    # Investimentos
    investments = supabase.table("investments").select("invested_amount, current_amount").execute().data
    total_invested = sum(i["invested_amount"] for i in investments)

    return {
        "month": month,
        "year": year,
        "plan": plan,
        "actual": {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": by_category,
            "debts_paid": debts_paid,
            "total_invested": total_invested,
        },
        "observations": plan.get("observations") if plan else None,
    }
```

- [ ] **Step 2: Registrar rota no main.py**

Em `backend/main.py`, após a linha `app.include_router(chat_router)`, adicionar:

```python
from routes.plans import router as plans_router
app.include_router(plans_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/routes/plans.py backend/main.py
git commit -m "feat: add /api/plans route with CRUD and comparison"
```

---

### Task 3: Tools novos no chat

**Files:**
- Modify: `backend/services/chat_tools.py`

- [ ] **Step 1: Adicionar definições dos 2 tools novos**

Em `backend/services/chat_tools.py`, adicionar ao final da lista `TOOL_DEFINITIONS` (antes do `]` de fechamento):

```python
    {
        "name": "save_financial_plan",
        "description": "Salva ou atualiza um plano financeiro para um mes especifico. Use quando o usuario pedir para criar, gerar ou atualizar um planejamento financeiro.",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {"type": "integer", "description": "Mes do plano (1-12)"},
                "year": {"type": "integer", "description": "Ano do plano"},
                "title": {"type": "string", "description": "Titulo do plano (ex: Reestruturacao - Maio/2026)"},
                "content": {
                    "type": "object",
                    "description": "Plano estruturado com sections. Cada section tem: category (dividas/reserva/custo_vida/sobra), title, items (array de {description, amount, notes}), total",
                },
                "status": {"type": "string", "enum": ["planejado", "em_andamento", "concluido"], "description": "Status do plano"},
            },
            "required": ["month", "year", "title", "content"],
        },
    },
    {
        "name": "get_plan_vs_actual",
        "description": "Retorna o comparativo entre o plano financeiro e o que realmente aconteceu em um mes. Use quando o usuario quiser ver como foi o mes em relacao ao planejado, ou antes de ajustar o plano do proximo mes.",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {"type": "integer", "description": "Mes (1-12)"},
                "year": {"type": "integer", "description": "Ano"},
            },
            "required": ["month", "year"],
        },
    },
```

- [ ] **Step 2: Adicionar funções de execução**

Ao final de `chat_tools.py`, adicionar:

```python
def _save_financial_plan(args: dict) -> str:
    month = args["month"]
    year = args["year"]
    title = args["title"]
    content = args["content"]
    status = args.get("status", "planejado")

    # Verifica se ja existe plano para o mes
    existing = (
        supabase.table("financial_plans")
        .select("id")
        .eq("month", month)
        .eq("year", year)
        .execute()
    ).data

    if existing:
        # Atualiza
        result = (
            supabase.table("financial_plans")
            .update({"title": title, "content": content, "status": status})
            .eq("id", existing[0]["id"])
            .execute()
        )
        return json.dumps({"success": True, "action": "updated", "plan": result.data[0]}, default=str)
    else:
        # Cria
        result = (
            supabase.table("financial_plans")
            .insert({"month": month, "year": year, "title": title, "content": content, "status": status})
            .execute()
        )
        return json.dumps({"success": True, "action": "created", "plan": result.data[0]}, default=str)


def _get_plan_vs_actual(args: dict) -> str:
    import requests as http_requests
    month = args["month"]
    year = args["year"]

    # Busca plano
    plan_data = (
        supabase.table("financial_plans")
        .select("*")
        .eq("month", month)
        .eq("year", year)
        .execute()
    ).data
    plan = plan_data[0] if plan_data else None

    # Dados reais
    start = f"{year}-{month:02d}-01"
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = f"{end_year}-{end_month:02d}-01"

    txns = (
        supabase.table("transactions")
        .select("*")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expenses = sum(t["amount"] for t in txns if t["type"] == "expense")

    by_category: dict[str, float] = {}
    for t in txns:
        if t["type"] == "expense":
            cat = t["category"]
            by_category[cat] = by_category.get(cat, 0) + t["amount"]

    debts = supabase.table("debts").select("creditor, status, current_amount").execute().data
    debts_paid = [d["creditor"] for d in debts if d.get("status") == "quitada"]

    investments = supabase.table("investments").select("invested_amount").execute().data
    total_invested = sum(i["invested_amount"] for i in investments)

    return json.dumps({
        "plan": plan,
        "actual": {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": by_category,
            "debts_paid": debts_paid,
            "total_invested": total_invested,
        },
    }, default=str)
```

- [ ] **Step 3: Registrar no execute_tool**

Na função `execute_tool`, antes do `else` final, adicionar:

```python
        elif name == "save_financial_plan":
            return _save_financial_plan(args)
        elif name == "get_plan_vs_actual":
            return _get_plan_vs_actual(args)
```

- [ ] **Step 4: Commit**

```bash
git add backend/services/chat_tools.py
git commit -m "feat: add save_financial_plan and get_plan_vs_actual chat tools"
```

---

### Task 4: Adicionar contexto do plano no prompt do chat

**Files:**
- Modify: `backend/routes/chat.py`

- [ ] **Step 1: Adicionar seção de planejamento no build_financial_context**

Em `backend/routes/chat.py`, na função `build_financial_context()`, antes do `return`, adicionar:

```python
    # Financial plans
    try:
        plans = (
            supabase.table("financial_plans")
            .select("*")
            .order("year", desc=True)
            .order("month", desc=True)
            .limit(3)
            .execute()
        ).data
    except Exception:
        plans = []

    plan_lines = []
    for p in plans:
        plan_lines.append(f"  - {p['title']} | Status: {p['status']}")
        if p.get("observations"):
            plan_lines.append(f"    Obs: {p['observations']}")
    plans_text = "\n".join(plan_lines) if plan_lines else "  Nenhum plano cadastrado"
```

E no string de retorno, antes do fechamento `"""`, adicionar:

```python

### Planejamento Financeiro
{plans_text}
```

- [ ] **Step 2: Adicionar instrução de planejamento no MENTOR_SYSTEM_PROMPT**

Em `MENTOR_SYSTEM_PROMPT`, antes de `## Regras`, adicionar:

```python
### Planejamento Financeiro
- Quando o usuario pedir um planejamento, ANALISE TUDO: receitas, despesas fixas, dizimo, primicias, dividas, objetivos e investimentos
- Gere um plano estruturado mes a mes com sections: dividas (o que pagar), reserva (quanto guardar), custo_vida (fixas + dizimo + primicia), sobra (livre)
- Use a ferramenta save_financial_plan para salvar o plano no sistema
- Para ajustar planos, use get_plan_vs_actual para ver o que realmente aconteceu antes de sugerir mudancas
- Priorize: 1) Despesas fixas e dizimo/primicia 2) Dividas menores primeiro (bola de neve) 3) Reserva de emergencia 4) Objetivos
- Seja especifico com valores e nomes de dividas/contas
- Cada section deve ter items com description, amount e notes explicando o racional
```

- [ ] **Step 3: Commit**

```bash
git add backend/routes/chat.py
git commit -m "feat: add financial plan context and instructions to chat prompt"
```

---

### Task 5: Página de Planejamento (frontend)

**Files:**
- Create: `frontend/app/planning/page.tsx`
- Create: `frontend/components/PlanView.tsx`
- Create: `frontend/components/PlanComparison.tsx`

- [ ] **Step 1: Criar componente PlanView**

Criar `frontend/components/PlanView.tsx`:

```tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Clock, AlertTriangle, Wallet, PiggyBank, ShoppingCart, Banknote } from "lucide-react";

interface PlanItem {
  description: string;
  amount: number;
  notes?: string;
}

interface PlanSection {
  category: string;
  title: string;
  items: PlanItem[];
  total: number;
}

interface Plan {
  id: string;
  month: number;
  year: number;
  title: string;
  content: { sections: PlanSection[] };
  observations: string | null;
  status: string;
}

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

const CATEGORY_ICONS: Record<string, typeof Wallet> = {
  dividas: AlertTriangle,
  reserva: PiggyBank,
  custo_vida: ShoppingCart,
  sobra: Banknote,
};

const CATEGORY_COLORS: Record<string, string> = {
  dividas: "text-red-500",
  reserva: "text-blue-500",
  custo_vida: "text-amber-500",
  sobra: "text-emerald-500",
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: typeof Clock }> = {
  planejado: { label: "Planejado", color: "bg-blue-500/20 text-blue-400", icon: Clock },
  em_andamento: { label: "Em andamento", color: "bg-amber-500/20 text-amber-400", icon: Clock },
  concluido: { label: "Concluído", color: "bg-emerald-500/20 text-emerald-400", icon: CheckCircle2 },
};

export default function PlanView({ plan }: { plan: Plan }) {
  const statusCfg = STATUS_CONFIG[plan.status] || STATUS_CONFIG.planejado;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">{plan.title}</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${statusCfg.color}`}>
          {statusCfg.label}
        </span>
      </div>

      {plan.content.sections?.map((section) => {
        const Icon = CATEGORY_ICONS[section.category] || Wallet;
        const color = CATEGORY_COLORS[section.category] || "text-gray-500";

        return (
          <Card key={section.category}>
            <CardHeader className="flex flex-row items-center gap-3 pb-2">
              <Icon className={`h-5 w-5 ${color}`} />
              <CardTitle className="text-sm font-medium">{section.title}</CardTitle>
              <span className={`ml-auto text-lg font-bold ${color}`}>
                R$ {section.total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {section.items.map((item, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div>
                      <span>{item.description}</span>
                      {item.notes && (
                        <p className="text-xs text-muted-foreground">{item.notes}</p>
                      )}
                    </div>
                    <span className="font-medium">
                      R$ {item.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        );
      })}

      {plan.observations && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Observações</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">{plan.observations}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Criar componente PlanComparison**

Criar `frontend/components/PlanComparison.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/lib/api";

interface ComparisonData {
  month: number;
  year: number;
  plan: {
    content: {
      sections: {
        category: string;
        title: string;
        total: number;
      }[];
    };
  } | null;
  actual: {
    income: number;
    expenses: number;
    balance: number;
    by_category: Record<string, number>;
    debts_paid: string[];
    total_invested: number;
  };
}

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function PlanComparison({ month, year }: { month: number; year: number }) {
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.get(`/plans/${month}/${year}/comparison`)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [month, year]);

  if (loading) return (
    <Card>
      <CardContent className="p-6">
        <div className="h-32 bg-muted animate-pulse rounded" />
      </CardContent>
    </Card>
  );

  if (!data || !data.plan) return null;

  const sections = data.plan.content.sections || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">
          Planejado vs Realizado — {MONTH_NAMES[month - 1]}/{year}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 text-xs font-medium text-muted-foreground border-b border-border pb-2">
          <span>Categoria</span>
          <span className="text-right">Planejado</span>
          <span className="text-right">Realizado</span>
        </div>

        {sections.map((section) => {
          const actual = section.category === "custo_vida"
            ? data.actual.expenses
            : section.category === "reserva"
            ? data.actual.total_invested
            : 0;

          const diff = section.total - actual;
          const diffColor = diff >= 0 ? "text-emerald-400" : "text-red-400";

          return (
            <div key={section.category} className="grid grid-cols-3 text-sm">
              <span>{section.title}</span>
              <span className="text-right">
                R$ {section.total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
              <span className={`text-right ${diffColor}`}>
                R$ {actual.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>
          );
        })}

        <div className="border-t border-border pt-2 grid grid-cols-3 text-sm font-bold">
          <span>Receita Total</span>
          <span className="text-right">—</span>
          <span className="text-right text-emerald-400">
            R$ {data.actual.income.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
          </span>
        </div>

        {data.actual.debts_paid.length > 0 && (
          <div className="text-xs text-emerald-400 mt-2">
            Dívidas quitadas: {data.actual.debts_paid.join(", ")}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 3: Criar página de Planejamento**

Criar `frontend/app/planning/page.tsx`:

```tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Trash2, ChevronLeft, ChevronRight, ClipboardList } from "lucide-react";
import ReactMarkdown from "react-markdown";
import PlanView from "@/components/PlanView";
import PlanComparison from "@/components/PlanComparison";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface Plan {
  id: string;
  month: number;
  year: number;
  title: string;
  content: { sections: any[] };
  observations: string | null;
  status: string;
}

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function PlanningPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [plan, setPlan] = useState<Plan | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loadingPlan, setLoadingPlan] = useState(true);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const timestamp = () => new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

  // Load plan for selected month
  useEffect(() => {
    setLoadingPlan(true);
    api.get(`/plans/${month}/${year}`)
      .then((res) => setPlan(res.data))
      .catch(() => setPlan(null))
      .finally(() => setLoadingPlan(false));
  }, [month, year]);

  // Load all plans for history
  useEffect(() => {
    api.get("/plans").then((res) => setPlans(res.data)).catch(() => setPlans([]));
  }, [plan]);

  // Chat scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function prev() {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  }

  function next() {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  }

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", content: input.trim(), timestamp: timestamp() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/chat", { message: userMsg.content, history: messages });
      setMessages([...updated, { role: "assistant", content: res.data.response, timestamp: timestamp() }]);
      // Refresh plan after AI response (might have saved a new plan)
      api.get(`/plans/${month}/${year}`)
        .then((r) => setPlan(r.data))
        .catch(() => setPlan(null));
    } catch {
      setMessages([...updated, { role: "assistant", content: "Erro ao conectar com a IA. Tente novamente.", timestamp: timestamp() }]);
    } finally {
      setLoading(false);
    }
  };

  // Save observations
  const saveObservations = async (obs: string) => {
    if (!plan) return;
    await api.put(`/plans/${plan.id}`, { observations: obs });
    setPlan({ ...plan, observations: obs });
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-2rem)]">
      {/* Main area - Plan */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Planejamento Financeiro</h2>
          <div className="flex items-center gap-3">
            <button onClick={prev} className="p-2 rounded-lg hover:bg-muted transition-colors">
              <ChevronLeft className="h-5 w-5" />
            </button>
            <span className="text-lg font-semibold min-w-[180px] text-center">
              {MONTH_NAMES[month - 1]} {year}
            </span>
            <button onClick={next} className="p-2 rounded-lg hover:bg-muted transition-colors">
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>

        {loadingPlan ? (
          <Card>
            <CardContent className="p-6">
              <div className="h-64 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ) : plan ? (
          <>
            <PlanView plan={plan} />
            <PlanComparison month={month} year={year} />

            {/* Observations */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Suas Observações</CardTitle>
              </CardHeader>
              <CardContent>
                <textarea
                  className="w-full bg-transparent border border-border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-ring"
                  rows={3}
                  placeholder="Anote o que aconteceu de diferente neste mês..."
                  defaultValue={plan.observations || ""}
                  onBlur={(e) => saveObservations(e.target.value)}
                />
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <ClipboardList className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                Nenhum plano para {MONTH_NAMES[month - 1]}/{year}.
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Use o chat ao lado para pedir à IA que crie seu planejamento.
              </p>
            </CardContent>
          </Card>
        )}

        {/* History */}
        {plans.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Histórico de Planos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {plans.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => { setMonth(p.month); setYear(p.year); }}
                    className={`w-full text-left flex items-center justify-between p-3 rounded-lg text-sm transition-colors ${
                      p.month === month && p.year === year
                        ? "bg-primary/10 text-primary"
                        : "hover:bg-muted"
                    }`}
                  >
                    <span>{p.title}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      p.status === "concluido"
                        ? "bg-emerald-500/20 text-emerald-400"
                        : p.status === "em_andamento"
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-blue-500/20 text-blue-400"
                    }`}>
                      {p.status === "concluido" ? "Concluído" : p.status === "em_andamento" ? "Em andamento" : "Planejado"}
                    </span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Sidebar - Chat */}
      <div className="w-[380px] flex flex-col border-l border-border bg-card rounded-lg">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h3 className="font-semibold text-sm">Chat de Planejamento</h3>
          <Button variant="ghost" size="icon" onClick={() => setMessages([])}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <p className="text-sm text-muted-foreground text-center mt-8">
              Peça para a IA criar seu planejamento financeiro!
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose prose-sm prose-invert max-w-none [&>p]:m-0 [&>ul]:m-0 [&>ol]:m-0">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>
              <span className="text-xs text-muted-foreground mt-1">{msg.timestamp}</span>
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

        <div className="p-4 border-t border-border flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Peça um planejamento..."
            disabled={loading}
          />
          <Button size="icon" onClick={send} disabled={loading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/app/planning/page.tsx frontend/components/PlanView.tsx frontend/components/PlanComparison.tsx
git commit -m "feat: add planning page with plan view, comparison, and chat"
```

---

### Task 6: Adicionar link no Sidebar

**Files:**
- Modify: `frontend/components/Sidebar.tsx`

- [ ] **Step 1: Adicionar import do ícone**

Em `frontend/components/Sidebar.tsx`, atualizar o import de lucide-react para incluir `ClipboardList`:

```typescript
import {
  LayoutDashboard, ArrowLeftRight, CreditCard, TrendingUp,
  Receipt, Target, Repeat, PieChart, Sun, Moon, Wallet, ClipboardList,
} from "lucide-react";
```

- [ ] **Step 2: Adicionar item de navegação**

No array `navItems`, após o item de "Objetivos" (`{ href: "/goals", ... }`), adicionar:

```typescript
  { href: "/planning", label: "Planejamento", icon: ClipboardList },
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/Sidebar.tsx
git commit -m "feat: add planning link to sidebar navigation"
```

---

### Task 7: Verificação final

- [ ] **Step 1: Verificar build do frontend**

Run: `cd frontend && npx next build`
Expected: Build sem erros

- [ ] **Step 2: Verificar imports do backend**

Run: `cd backend && python -c "from routes.plans import router; print('plans OK')" && python -c "from services.chat_tools import TOOL_DEFINITIONS; print(f'tools: {len(TOOL_DEFINITIONS)}')"` 
Expected: `plans OK` e `tools: 19`

- [ ] **Step 3: Testar fluxo completo**

1. Abrir http://localhost:3000/planning
2. No chat lateral: "Cria meu planejamento financeiro a partir de maio 2026"
3. IA deve analisar dados e gerar plano estruturado
4. Plano deve aparecer na área principal
5. Navegar para outro mês e voltar
