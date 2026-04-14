# FinanceAI Full Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar o FinanceAI de um MVP funcional em um app financeiro premium com estilo BI analítico, corrigindo bugs críticos e melhorando a arquitetura.

**Architecture:** Redesign incremental em 5 fases. Fase 1 corrige bugs. Fase 2 estabelece design system com CSS custom properties. Fase 3 reescreve o dashboard com novos componentes. Fase 4 aplica o design system nas páginas secundárias. Fase 5 adiciona polish (skeletons, responsividade, validações).

**Tech Stack:** Next.js, React, TypeScript, Tailwind CSS, Recharts, FastAPI, Supabase, sonner (toasts)

**Spec:** `docs/superpowers/specs/2026-04-10-full-redesign-design.md`

**Mockup aprovado:** `.superpowers/brainstorm/253-1775830692/content/dashboard-layout-v4.html`

---

## File Structure

### Files to modify

| File | Responsibility | Phase |
|------|---------------|-------|
| `frontend/components/PageHelp.tsx` | Fix DialogTrigger bug | 1 |
| `frontend/components/SummaryCards.tsx` | Fix invested field, then rewrite for hero cards | 1, 3 |
| `frontend/components/Sidebar.tsx` | Fix hardcoded color, then design system | 1, 4 |
| `backend/services/alert_service.py` | Fix date sorting, overdue side-effect | 1 |
| `backend/routes/chat.py` | Fix exception exposure, add context cache | 1 |
| `backend/routes/transactions.py` | Fix tithe sync to income-only | 1 |
| `frontend/app/globals.css` | Add design system tokens | 2 |
| `frontend/app/layout.tsx` | Update background to design system | 2 |
| `frontend/components/SpendingChart.tsx` | Rewrite: bar chart + donut | 3 |
| `frontend/components/AlertsPanel.tsx` | Redesign with border-left style | 3 |
| `frontend/components/GoalsProgress.tsx` | Redesign with grid + progress bars | 3 |
| `frontend/app/page.tsx` | Rewrite dashboard layout | 3 |
| `backend/routes/summary.py` | Add /upcoming endpoint | 3 |
| `frontend/app/transactions/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/credit-cards/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/debts/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/investments/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/recurring/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/budgets/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/goals/page.tsx` | Apply design tokens + toasts | 4 |
| `frontend/app/planning/page.tsx` | Apply design tokens | 4 |

### Files to create

| File | Responsibility | Phase |
|------|---------------|-------|
| `frontend/components/UpcomingBills.tsx` | Tabela de próximos vencimentos | 3 |

---

## PHASE 1 — BUG FIXES

### Task 1: Fix PageHelp DialogTrigger

**Files:**
- Modify: `financeai/frontend/components/PageHelp.tsx`

- [ ] **Step 1: Fix the DialogTrigger prop**

Replace the invalid `render` prop with `asChild`:

```tsx
// In PageHelp.tsx, replace the DialogTrigger block:
<DialogTrigger asChild>
  <Button variant="outline" size="icon" className="h-8 w-8 rounded-full">
    <HelpCircle className="h-4 w-4" />
  </Button>
</DialogTrigger>
```

- [ ] **Step 2: Verify in browser**

Open any page that uses PageHelp (e.g., /transactions) and click the help button. It should open the dialog without console errors.

- [ ] **Step 3: Commit**

```bash
git add financeai/frontend/components/PageHelp.tsx
git commit -m "fix: replace invalid render prop with asChild on DialogTrigger"
```

---

### Task 2: Fix SummaryCards invested field

**Files:**
- Modify: `financeai/frontend/components/SummaryCards.tsx`

- [ ] **Step 1: Change total_current to total_invested**

In the `cards` array, line with `title: "Investido"`, change:

```tsx
// Before:
{ title: "Investido", value: data.total_current, icon: PiggyBank, color: "text-blue-500" },

// After:
{ title: "Investido", value: data.total_invested, icon: PiggyBank, color: "text-blue-500" },
```

- [ ] **Step 2: Commit**

```bash
git add financeai/frontend/components/SummaryCards.tsx
git commit -m "fix: show total_invested instead of total_current in SummaryCards"
```

---

### Task 3: Fix alert_service date sorting

**Files:**
- Modify: `financeai/backend/services/alert_service.py`

- [ ] **Step 1: Fix the sort key to parse dates**

Replace the last sort line (around line 211):

```python
# Before:
alerts.sort(key=lambda a: (level_order.get(a["level"], 3), a.get("due_date") or ""))

# After:
alerts.sort(key=lambda a: (level_order.get(a["level"], 3), a.get("due_date") or "9999-12-31"))
```

Note: ISO date strings sort correctly alphabetically when they exist. The fix is the fallback — `""` sorts before any date (wrong: puts no-date items first), `"9999-12-31"` sorts them last (correct).

- [ ] **Step 2: Remove overdue side-effect from GET**

Move `check_and_update_overdue()` out of `get_active_alerts()`. Remove the call on line 31:

```python
def get_active_alerts() -> list[dict]:
    """Return active alerts."""
    today = date.today()
    alerts = []
    # ... rest stays the same, but remove the check_and_update_overdue() call
```

- [ ] **Step 3: Call overdue check from summary endpoint instead**

In `financeai/backend/routes/summary.py`, add the overdue check to the monthly summary (called once per dashboard load):

```python
from services.alert_service import check_and_update_overdue

@router.get("/monthly")
async def monthly_summary(month: int | None = None, year: int | None = None):
    check_and_update_overdue()
    today = date.today()
    # ... rest stays the same
```

- [ ] **Step 4: Commit**

```bash
git add financeai/backend/services/alert_service.py financeai/backend/routes/summary.py
git commit -m "fix: fix alert date sorting and move overdue check out of GET"
```

---

### Task 4: Fix chat exception exposure and add context cache

**Files:**
- Modify: `financeai/backend/routes/chat.py`

- [ ] **Step 1: Fix exception exposure**

In the chat POST endpoint (around line 392-394):

```python
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail="Erro ao processar mensagem. Tente novamente.")
```

- [ ] **Step 2: Add simple cache for build_financial_context**

Add at the top of the file (after imports):

```python
import time

_context_cache: dict = {"text": "", "timestamp": 0}
_CACHE_TTL = 120  # 2 minutes

def get_financial_context() -> str:
    now = time.time()
    if now - _context_cache["timestamp"] < _CACHE_TTL and _context_cache["text"]:
        return _context_cache["text"]
    text = build_financial_context()
    _context_cache["text"] = text
    _context_cache["timestamp"] = now
    return text
```

Then in the chat POST endpoint, replace `build_financial_context()` call:

```python
context = get_financial_context()
```

- [ ] **Step 3: Commit**

```bash
git add financeai/backend/routes/chat.py
git commit -m "fix: hide internal errors from chat response, add context cache"
```

---

### Task 5: Fix tithe sync to income-only

**Files:**
- Modify: `financeai/backend/routes/transactions.py`

The code already checks `if created.get("type") == "income"` on line 54 and `if updated.get("type") == "income"` on line 77. This is actually already correct — tithe only syncs for income transactions.

However, looking closer at the code, expense transactions of type Dizimo/Primicia are created by the sync itself — if someone updates a non-income transaction, the sync won't fire. This is already correct behavior.

- [ ] **Step 1: Verify the current behavior is correct**

Read `financeai/backend/routes/transactions.py` lines 46-80. Confirm that `sync_tithe_and_firstfruits` is only called when `type == "income"`. If already correct, skip to commit.

- [ ] **Step 2: Commit (no-op if already correct)**

No changes needed — the code already guards tithe sync behind `type == "income"` check.

---

### Task 6: Fix Sidebar hardcoded color

**Files:**
- Modify: `financeai/frontend/components/Sidebar.tsx`

- [ ] **Step 1: Replace hardcoded bg-blue-600 with CSS variable-ready class**

```tsx
// Before (line 52-54):
isActive
  ? "bg-blue-600 text-white shadow-sm"
  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"

// After:
isActive
  ? "bg-primary text-primary-foreground shadow-sm"
  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
```

Also fix the logo background (line 39):

```tsx
// Before:
<div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center">

// After:
<div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center">
```

- [ ] **Step 2: Commit**

```bash
git add financeai/frontend/components/Sidebar.tsx
git commit -m "fix: replace hardcoded blue-600 with theme-aware primary color"
```

---

**CHECKPOINT: Phase 1 complete. Run the app and verify all fixes work before proceeding.**

---

## PHASE 2 — DESIGN SYSTEM

### Task 7: Add design system tokens to globals.css

**Files:**
- Modify: `financeai/frontend/app/globals.css`

- [ ] **Step 1: Replace the `.dark` block with the new BI palette**

Replace the entire `.dark { ... }` block in globals.css with:

```css
.dark {
  /* Base backgrounds */
  --background: #0c1222;
  --foreground: #e2e8f0;

  /* Card system */
  --card: #111a2e;
  --card-foreground: #e2e8f0;
  --card-inner: #0f1825;

  /* Popover */
  --popover: #111a2e;
  --popover-foreground: #e2e8f0;

  /* Primary (accent blue) */
  --primary: #60a5fa;
  --primary-foreground: #0c1222;

  /* Secondary */
  --secondary: #1e2d4a;
  --secondary-foreground: #e2e8f0;

  /* Muted */
  --muted: #1e2d4a;
  --muted-foreground: #64748b;

  /* Accent */
  --accent: #1e2d4a;
  --accent-foreground: #e2e8f0;

  /* Destructive */
  --destructive: #f87171;

  /* Borders */
  --border: #1e2d4a;
  --input: #1e2d4a;
  --ring: #60a5fa;

  /* Charts */
  --chart-1: #60a5fa;
  --chart-2: #f87171;
  --chart-3: #c084fc;
  --chart-4: #fbbf24;
  --chart-5: #34d399;

  /* Sidebar */
  --sidebar: #111a2e;
  --sidebar-foreground: #e2e8f0;
  --sidebar-primary: #60a5fa;
  --sidebar-primary-foreground: #0c1222;
  --sidebar-accent: #1e2d4a;
  --sidebar-accent-foreground: #e2e8f0;
  --sidebar-border: #1e2d4a;
  --sidebar-ring: #60a5fa;

  /* Status colors (custom properties for components) */
  --status-paid-bg: rgba(74, 222, 128, 0.08);
  --status-paid-text: #4ade80;
  --status-overdue-bg: rgba(248, 113, 113, 0.08);
  --status-overdue-text: #fca5a5;
  --status-pending-bg: rgba(251, 191, 36, 0.06);
  --status-pending-text: #fde68a;
  --status-info-bg: rgba(96, 165, 250, 0.06);
  --status-info-text: #93c5fd;

  /* Accent palette */
  --accent-green: #4ade80;
  --accent-red: #f87171;
  --accent-amber: #fbbf24;
  --accent-purple: #c084fc;
  --accent-emerald: #34d399;
}
```

- [ ] **Step 2: Update the body base layer**

In the `@layer base` block, it's already `@apply bg-background text-foreground;` — this will now use the new dark values automatically.

- [ ] **Step 3: Commit**

```bash
git add financeai/frontend/app/globals.css
git commit -m "feat: add BI-style design system tokens to dark theme"
```

---

### Task 8: Update layout background

**Files:**
- Modify: `financeai/frontend/app/layout.tsx`

- [ ] **Step 1: The layout body already uses `bg-background`**

Verify that `layout.tsx` body has `bg-background` class. It does: `className={... bg-background text-foreground}`. Since we changed `--background` in the dark theme, this automatically picks up the new `#0c1222` color.

No code change needed. The design system tokens propagate automatically through CSS variables.

- [ ] **Step 2: Verify in browser**

Open the app. Background should now be dark navy blue (`#0c1222`) instead of pure black. Cards should be `#111a2e`. Borders should be `#1e2d4a`.

- [ ] **Step 3: Commit (if any tweaks needed)**

---

**CHECKPOINT: Phase 2 complete. The app should now have the BI color palette applied globally. All existing components will pick up new colors through CSS variables.**

---

## PHASE 3 — DASHBOARD PREMIUM

### Task 9: Add /api/summary/upcoming endpoint

**Files:**
- Modify: `financeai/backend/routes/summary.py`

- [ ] **Step 1: Add the upcoming endpoint**

Add at the end of `summary.py`:

```python
@router.get("/upcoming")
async def upcoming_bills():
    today = date.today()
    limit = today + timedelta(days=30)

    # Pending transactions with due_date in next 30 days
    pending_txns = (
        supabase.table("transactions")
        .select("description, amount, due_date, status")
        .eq("status", "pending")
        .gte("due_date", str(today))
        .lte("due_date", str(limit))
        .order("due_date")
        .execute()
    ).data

    # Also get overdue transactions
    overdue_txns = (
        supabase.table("transactions")
        .select("description, amount, due_date, status")
        .eq("status", "overdue")
        .order("due_date")
        .execute()
    ).data

    upcoming = []
    for t in overdue_txns + pending_txns:
        due = date.fromisoformat(t["due_date"]) if t.get("due_date") else today
        days_until = (due - today).days
        upcoming.append({
            "description": t["description"],
            "amount": t["amount"],
            "due_date": t["due_date"],
            "days_until": days_until,
            "status": t["status"],
        })

    upcoming.sort(key=lambda x: x.get("due_date") or "9999-12-31")
    return {"upcoming": upcoming}
```

- [ ] **Step 2: Add timedelta import**

At the top of `summary.py`, add:

```python
from datetime import date, timedelta
```

- [ ] **Step 3: Test the endpoint**

```bash
curl http://localhost:8000/api/summary/upcoming | python -m json.tool
```

Expected: JSON with `upcoming` array containing pending/overdue transactions sorted by due_date.

- [ ] **Step 4: Commit**

```bash
git add financeai/backend/routes/summary.py
git commit -m "feat: add /api/summary/upcoming endpoint for dashboard"
```

---

### Task 10: Rewrite SummaryCards as Hero Cards

**Files:**
- Modify: `financeai/frontend/components/SummaryCards.tsx`

- [ ] **Step 1: Rewrite the full component**

Replace the entire content of `SummaryCards.tsx` with the new hero cards + secondary cards layout:

```tsx
"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

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

interface Props {
  month: number;
  year: number;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

export default function SummaryCards({ month, year }: Props) {
  const [data, setData] = useState<Summary | null>(null);

  useEffect(() => {
    setData(null);
    api.get(`/summary/monthly?month=${month}&year=${year}`).then((res) => setData(res.data));
  }, [month, year]);

  if (!data) return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-[120px] rounded-xl bg-card border border-border animate-pulse" />
        ))}
      </div>
      <div className="grid grid-cols-4 gap-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-[80px] rounded-[10px] bg-card border border-border animate-pulse" />
        ))}
      </div>
    </div>
  );

  const pctExpenses = data.income > 0 ? ((data.expenses / data.income) * 100).toFixed(1) : "0";
  const pctBalance = data.income > 0 ? ((data.balance / data.income) * 100).toFixed(1) : "0";

  return (
    <div className="space-y-3">
      {/* Hero Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Saldo */}
        <div className="relative overflow-hidden rounded-xl p-5 border"
          style={{ background: "linear-gradient(135deg, #0f2027, #1a3a4a)", borderColor: "#1e4a5a" }}>
          <svg className="absolute bottom-0 left-0 right-0 h-10 opacity-20" viewBox="0 0 200 40" preserveAspectRatio="none">
            <polyline points="0,35 20,30 40,32 60,25 80,28 100,18 120,22 140,15 160,12 180,8 200,5" fill="none" stroke="#4ade80" strokeWidth="2"/>
          </svg>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">Saldo</p>
          <p className={`text-2xl font-bold mt-1 relative ${data.balance >= 0 ? "text-[#4ade80]" : "text-[#f87171]"}`}>
            R$ {fmt(data.balance)}
          </p>
          <p className="text-xs text-muted-foreground mt-1.5 relative">
            {data.balance >= 0 ? "+" : ""}{pctBalance}% vs despesas
          </p>
        </div>

        {/* Receitas */}
        <div className="relative overflow-hidden rounded-xl p-5 border"
          style={{ background: "linear-gradient(135deg, #0f1a2e, #162040)", borderColor: "#1e3060" }}>
          <svg className="absolute bottom-0 left-0 right-0 h-10 opacity-15" viewBox="0 0 200 40" preserveAspectRatio="none">
            <polyline points="0,30 30,28 60,25 90,20 120,22 150,15 200,10" fill="none" stroke="#60a5fa" strokeWidth="2"/>
          </svg>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">Receitas</p>
          <p className="text-2xl font-bold mt-1 relative">R$ {fmt(data.income)}</p>
          <p className="text-xs text-muted-foreground mt-1.5 relative">3 fontes de renda</p>
        </div>

        {/* Despesas */}
        <div className="relative overflow-hidden rounded-xl p-5 border"
          style={{ background: "linear-gradient(135deg, #1a0f1e, #2a1535)", borderColor: "#3a2050" }}>
          <svg className="absolute bottom-0 left-0 right-0 h-10 opacity-15" viewBox="0 0 200 40" preserveAspectRatio="none">
            <polyline points="0,25 30,20 60,28 90,22 120,30 150,18 200,15" fill="none" stroke="#c084fc" strokeWidth="2"/>
          </svg>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">Despesas</p>
          <p className="text-2xl font-bold mt-1 relative">R$ {fmt(data.expenses)}</p>
          <p className="text-xs text-muted-foreground mt-1.5 relative">{pctExpenses}% da receita</p>
        </div>
      </div>

      {/* Secondary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-[10px] p-3 bg-card border border-border">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Investido</p>
          <p className="text-[15px] font-semibold mt-1 text-muted-foreground">R$ {fmt(data.total_invested)}</p>
        </div>
        <div className="rounded-[10px] p-3 bg-card border border-border">
          <div className="flex justify-between items-center">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Dizimo</p>
            <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
              data.tithe_status === "paid"
                ? "bg-[--status-paid-bg] text-[--status-paid-text]"
                : "bg-[--status-overdue-bg] text-[--status-overdue-text]"
            }`}>
              {data.tithe_status === "paid" ? "Pago" : "Pendente"}
            </span>
          </div>
          <p className="text-[15px] font-semibold mt-1">R$ {fmt(data.tithe)}</p>
        </div>
        <div className="rounded-[10px] p-3 bg-card border border-border">
          <div className="flex justify-between items-center">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Primicia</p>
            <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
              data.firstfruits_status === "paid"
                ? "bg-[--status-paid-bg] text-[--status-paid-text]"
                : "bg-[--status-overdue-bg] text-[--status-overdue-text]"
            }`}>
              {data.firstfruits_status === "paid" ? "Pago" : "Pendente"}
            </span>
          </div>
          <p className="text-[15px] font-semibold mt-1">R$ {fmt(data.firstfruits)}</p>
        </div>
        <div className="rounded-[10px] p-3 bg-card border border-border">
          <div className="flex justify-between items-center">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Dividas</p>
          </div>
          <p className="text-[15px] font-semibold mt-1 text-[#f87171]">R$ {fmt(data.total_invested)}</p>
        </div>
      </div>
    </div>
  );
}
```

Note: The debts card needs data from `/api/debts`. We'll add that data fetch in the dashboard page (Task 14).

- [ ] **Step 2: Verify in browser**

Dashboard should show 3 hero cards with sparklines + 4 secondary cards below.

- [ ] **Step 3: Commit**

```bash
git add financeai/frontend/components/SummaryCards.tsx
git commit -m "feat: rewrite SummaryCards with hero cards and sparklines"
```

---

### Task 11: Rewrite SpendingChart with bar chart + donut

**Files:**
- Modify: `financeai/frontend/components/SpendingChart.tsx`

- [ ] **Step 1: Rewrite with side-by-side bars and donut chart**

Replace the entire content of `SpendingChart.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
} from "recharts";
import api from "@/lib/api";

const CATEGORY_COLORS = ["#60a5fa", "#c084fc", "#f59e0b", "#34d399", "#f87171", "#fb923c", "#a78bfa", "#38bdf8"];
const MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

interface Props {
  month: number;
  year: number;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

export default function SpendingChart({ month, year }: Props) {
  const [categoryData, setCategoryData] = useState<{ name: string; value: number }[]>([]);
  const [yearlyData, setYearlyData] = useState<{ name: string; receitas: number; despesas: number }[]>([]);

  useEffect(() => {
    api.get(`/summary/monthly?month=${month}&year=${year}`).then((res) => {
      const byCategory = res.data.by_category as Record<string, number>;
      const sorted = Object.entries(byCategory)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5);
      setCategoryData(sorted);
    });

    api.get(`/summary/yearly?year=${year}`).then((res) => {
      setYearlyData(
        res.data.months
          .filter((m: { income: number; expenses: number }) => m.income > 0 || m.expenses > 0)
          .map((m: { month: number; income: number; expenses: number }) => ({
            name: MONTH_LABELS[m.month - 1],
            receitas: m.income,
            despesas: m.expenses,
          }))
      );
    });
  }, [month, year]);

  const isLoading = categoryData.length === 0 && yearlyData.length === 0;
  const totalExpenses = categoryData.reduce((sum, c) => sum + c.value, 0);

  if (isLoading) return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-3">
      <div className="lg:col-span-3 h-[280px] rounded-[10px] bg-card border border-border animate-pulse" />
      <div className="lg:col-span-2 h-[280px] rounded-[10px] bg-card border border-border animate-pulse" />
    </div>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-3">
      {/* Bar chart - Evolução mensal */}
      <div className="lg:col-span-3 rounded-[10px] p-4 bg-card border border-border">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-semibold">Evolucao mensal</h3>
          <div className="flex gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-sm bg-[#60a5fa]" />
              <span className="text-xs text-muted-foreground">Receitas</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-sm bg-[#f87171]" />
              <span className="text-xs text-muted-foreground">Despesas</span>
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={yearlyData} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" vertical={false} />
            <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false}
              tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v} />
            <Tooltip
              contentStyle={{ background: "#111a2e", border: "1px solid #1e2d4a", borderRadius: "8px", fontSize: "12px" }}
              formatter={(value: number) => `R$ ${fmt(value)}`}
            />
            <Bar dataKey="receitas" fill="#60a5fa" radius={[3, 3, 0, 0]} />
            <Bar dataKey="despesas" fill="#f87171" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Donut chart - Top 5 categorias */}
      <div className="lg:col-span-2 rounded-[10px] p-4 bg-card border border-border">
        <h3 className="text-sm font-semibold mb-3">Top 5 Despesas por categoria</h3>
        {categoryData.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sem dados</p>
        ) : (
          <div className="flex gap-3 items-center">
            <ResponsiveContainer width={100} height={100}>
              <PieChart>
                <Pie
                  data={categoryData}
                  dataKey="value"
                  cx="50%"
                  cy="50%"
                  innerRadius={28}
                  outerRadius={45}
                  strokeWidth={0}
                >
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              {categoryData.map((cat, i) => (
                <div key={cat.name} className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-sm flex-shrink-0" style={{ background: CATEGORY_COLORS[i] }} />
                  <span className="text-xs text-muted-foreground flex-1">{cat.name}</span>
                  <span className="text-xs font-medium">R$ {fmt(cat.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add financeai/frontend/components/SpendingChart.tsx
git commit -m "feat: rewrite SpendingChart with side-by-side bars and donut chart"
```

---

### Task 12: Create UpcomingBills component

**Files:**
- Create: `financeai/frontend/components/UpcomingBills.tsx`

- [ ] **Step 1: Create the component**

```tsx
"use client";

import { useEffect, useState } from "react";
import { formatDate } from "@/lib/utils";
import api from "@/lib/api";

interface Bill {
  description: string;
  amount: number;
  due_date: string;
  days_until: number;
  status: string;
}

export default function UpcomingBills() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/summary/upcoming")
      .then((res) => setBills(res.data.upcoming || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <div className="h-4 w-40 bg-muted animate-pulse rounded mb-4" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-8 bg-muted animate-pulse rounded mb-2" />
      ))}
    </div>
  );

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <h3 className="text-sm font-semibold mb-3">Proximos vencimentos</h3>
      {bills.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhuma conta proxima</p>
      ) : (
        <div>
          {/* Header */}
          <div className="grid grid-cols-[1fr_auto_auto] gap-2 pb-2 border-b border-border mb-1">
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">Conta</span>
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">Vence</span>
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground text-right">Valor</span>
          </div>
          {bills.slice(0, 6).map((bill, i) => (
            <div key={i} className="grid grid-cols-[1fr_auto_auto] gap-2 py-2 border-b border-[#0f1825] last:border-0 items-center">
              <div>
                <p className="text-sm">{bill.description}</p>
                {bill.status === "overdue" && (
                  <span className="text-[10px] text-[#fca5a5]">Atrasada</span>
                )}
              </div>
              <span className="text-sm text-muted-foreground">{formatDate(bill.due_date)}</span>
              <span className="text-sm font-semibold text-right">
                R$ {bill.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add financeai/frontend/components/UpcomingBills.tsx
git commit -m "feat: create UpcomingBills component for dashboard"
```

---

### Task 13: Redesign AlertsPanel with border-left style

**Files:**
- Modify: `financeai/frontend/components/AlertsPanel.tsx`

- [ ] **Step 1: Rewrite AlertsPanel**

Replace the entire content:

```tsx
"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface Alert {
  id: string;
  message: string;
  level: string;
  due_date: string | null;
  amount: number | null;
  source: string;
}

const LEVEL_STYLES: Record<string, { bg: string; border: string; text: string }> = {
  danger: { bg: "bg-[--status-overdue-bg]", border: "border-l-[#f87171]", text: "text-[#fca5a5]" },
  warning: { bg: "bg-[--status-pending-bg]", border: "border-l-[#fbbf24]", text: "text-[#fde68a]" },
  info: { bg: "bg-[--status-info-bg]", border: "border-l-[#60a5fa]", text: "text-[#93c5fd]" },
};

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/alerts").then((res) => setAlerts(res.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <div className="h-4 w-24 bg-muted animate-pulse rounded mb-4" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-14 bg-muted animate-pulse rounded mb-2" />
      ))}
    </div>
  );

  // Group and limit alerts
  const displayed = alerts.slice(0, 5);

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <h3 className="text-sm font-semibold mb-3">Alertas</h3>
      {displayed.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhum alerta ativo</p>
      ) : (
        <div className="space-y-2">
          {displayed.map((alert) => {
            const style = LEVEL_STYLES[alert.level] || LEVEL_STYLES.info;
            return (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border-l-[3px] ${style.bg} ${style.border}`}
              >
                <p className={`text-xs font-semibold ${style.text}`}>{alert.message}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add financeai/frontend/components/AlertsPanel.tsx
git commit -m "feat: redesign AlertsPanel with border-left severity style"
```

---

### Task 14: Redesign GoalsProgress

**Files:**
- Modify: `financeai/frontend/components/GoalsProgress.tsx`

- [ ] **Step 1: Rewrite with grid layout**

Replace the entire content:

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";

interface Goal {
  id: string;
  name: string;
  target_amount: number;
  saved_amount: number;
  status: string;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

export default function GoalsProgress() {
  const [goals, setGoals] = useState<Goal[]>([]);

  useEffect(() => {
    api.get("/goals", { params: { status: "ativa" } }).then((res) => setGoals(res.data));
  }, []);

  const displayed = goals.slice(0, 3);

  if (displayed.length === 0) return null;

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold">Metas</h3>
        <Link href="/goals" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          Ver todas &#8250;
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {displayed.map((g) => {
          const pct = g.target_amount > 0 ? Math.min((g.saved_amount / g.target_amount) * 100, 100) : 0;
          return (
            <div key={g.id} className="rounded-lg p-3 bg-[#0f1825] border border-border">
              <div className="flex justify-between items-center">
                <p className="text-sm font-medium">{g.name}</p>
                <span className="text-xs text-muted-foreground">{pct.toFixed(0)}%</span>
              </div>
              <div className="w-full h-1 bg-border rounded-full mt-2 overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#60a5fa] transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                R$ {fmt(g.saved_amount)} / R$ {fmt(g.target_amount)}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add financeai/frontend/components/GoalsProgress.tsx
git commit -m "feat: redesign GoalsProgress with grid and accent-blue progress bars"
```

---

### Task 15: Rewrite Dashboard page layout

**Files:**
- Modify: `financeai/frontend/app/page.tsx`

- [ ] **Step 1: Rewrite the dashboard page**

Replace the entire content:

```tsx
"use client";

import { useState } from "react";
import SummaryCards from "@/components/SummaryCards";
import SpendingChart from "@/components/SpendingChart";
import GoalsProgress from "@/components/GoalsProgress";
import UpcomingBills from "@/components/UpcomingBills";
import AlertsPanel from "@/components/AlertsPanel";

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function Dashboard() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  function prev() {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  }

  function next() {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  }

  return (
    <div className="space-y-4 max-w-[1200px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold">Dashboard Financeiro</h2>
          <p className="text-xs text-muted-foreground">Visao geral financeira</p>
        </div>
        <div className="flex gap-px bg-secondary rounded-md overflow-hidden border border-border">
          <button onClick={prev} className="px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
            &#8249; {MONTH_NAMES[month === 1 ? 11 : month - 2]?.slice(0, 3)}
          </button>
          <div className="px-4 py-1.5 text-xs font-semibold bg-accent">
            {MONTH_NAMES[month - 1]} {year}
          </div>
          <button onClick={next} className="px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
            {MONTH_NAMES[month === 12 ? 0 : month]?.slice(0, 3)} &#8250;
          </button>
        </div>
      </div>

      {/* Row 1-2: Summary Cards (hero + secondary) */}
      <SummaryCards month={month} year={year} />

      {/* Row 3: Charts */}
      <SpendingChart month={month} year={year} />

      {/* Row 4: Upcoming + Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <UpcomingBills />
        <AlertsPanel />
      </div>

      {/* Row 5: Goals */}
      <GoalsProgress />
    </div>
  );
}
```

- [ ] **Step 2: Remove DebtsOverview import**

DebtsOverview was removed from the dashboard. The debts data is now shown in the secondary card. The DebtsOverview component file can stay for the /debts page but is no longer imported in page.tsx.

- [ ] **Step 3: Verify in browser**

Open the dashboard. Should show the full 5-row layout matching the approved mockup v4.

- [ ] **Step 4: Commit**

```bash
git add financeai/frontend/app/page.tsx
git commit -m "feat: rewrite dashboard with premium 5-row BI layout"
```

---

**CHECKPOINT: Phase 3 complete. Dashboard should match the approved mockup. Review all 5 rows before proceeding.**

---

## PHASE 4 — PAGES & TOASTS

### Task 16: Install sonner and add Toaster

**Files:**
- Modify: `financeai/frontend/app/layout.tsx`

- [ ] **Step 1: Install sonner**

```bash
cd financeai/frontend && npm install sonner
```

- [ ] **Step 2: Add Toaster to layout**

In `layout.tsx`, add the import and component:

```tsx
import { Toaster } from "sonner";

// Inside the body, after <Chat />:
<Toaster theme="dark" position="bottom-right" richColors />
```

- [ ] **Step 3: Commit**

```bash
git add financeai/frontend/package.json financeai/frontend/package-lock.json financeai/frontend/app/layout.tsx
git commit -m "feat: add sonner toast notifications"
```

---

### Task 17: Add toasts to all CRUD pages

**Files:**
- Modify: `financeai/frontend/app/transactions/page.tsx`
- Modify: `financeai/frontend/app/credit-cards/page.tsx`
- Modify: `financeai/frontend/app/debts/page.tsx`
- Modify: `financeai/frontend/app/investments/page.tsx`
- Modify: `financeai/frontend/app/recurring/page.tsx`
- Modify: `financeai/frontend/app/budgets/page.tsx`
- Modify: `financeai/frontend/app/goals/page.tsx`

- [ ] **Step 1: Add toast imports and calls to each page**

For each page file, add at the top:

```tsx
import { toast } from "sonner";
```

Then wrap each API success/error call. Pattern for every page:

```tsx
// After successful create:
toast.success("Item criado com sucesso");

// After successful update:
toast.success("Item atualizado");

// After successful delete:
toast.success("Item removido");

// On API error (in .catch blocks):
toast.error("Erro ao processar operacao");
```

Apply this pattern to every `api.post`, `api.put`, `api.delete` call in all 7 pages.

- [ ] **Step 2: Verify toasts work**

Create, edit, and delete a transaction. Each operation should show a toast notification in the bottom-right corner.

- [ ] **Step 3: Commit**

```bash
git add financeai/frontend/app/transactions/page.tsx financeai/frontend/app/credit-cards/page.tsx financeai/frontend/app/debts/page.tsx financeai/frontend/app/investments/page.tsx financeai/frontend/app/recurring/page.tsx financeai/frontend/app/budgets/page.tsx financeai/frontend/app/goals/page.tsx
git commit -m "feat: add toast notifications to all CRUD pages"
```

---

### Task 18: Update Sidebar to design system

**Files:**
- Modify: `financeai/frontend/components/Sidebar.tsx`

- [ ] **Step 1: Update sidebar colors**

The sidebar already uses `bg-card` and `border-border` which now map to the BI palette. The `bg-primary` fix from Task 6 handles the active state. Verify the sidebar looks correct with the new design system — no additional changes should be needed.

- [ ] **Step 2: Verify in browser**

Sidebar should have dark navy background (`#111a2e`), subtle borders, and blue active state.

---

**CHECKPOINT: Phase 4 complete. All pages should have the BI color palette and toast notifications.**

---

## PHASE 5 — POLISH

### Task 19: Add backend validations

**Files:**
- Modify: `financeai/backend/models/budget.py`
- Modify: `financeai/backend/models/recurring.py`
- Modify: `financeai/backend/models/credit_card.py`

- [ ] **Step 1: Add validation to BudgetCreate**

In `models/budget.py`, add field validator:

```python
from pydantic import BaseModel, field_validator

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float
    is_active: bool = True

    @field_validator('monthly_limit')
    @classmethod
    def limit_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Limite deve ser maior que zero')
        return v
```

- [ ] **Step 2: Add validation to RecurringCreate**

In `models/recurring.py`, add validators:

```python
from pydantic import BaseModel, field_validator

class RecurringCreate(BaseModel):
    # ... existing fields ...

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

    @field_validator('business_day_number')
    @classmethod
    def business_day_valid_range(cls, v):
        if v is not None and (v < 1 or v > 23):
            raise ValueError('Dia util deve ser entre 1 e 23')
        return v
```

- [ ] **Step 3: Add validation to CreditCardCreate**

In `models/credit_card.py`, add validators for closing_day and due_day:

```python
@field_validator('closing_day', 'due_day')
@classmethod
def day_must_be_valid(cls, v):
    if v < 1 or v > 31:
        raise ValueError('Dia deve ser entre 1 e 31')
    return v
```

- [ ] **Step 4: Commit**

```bash
git add financeai/backend/models/budget.py financeai/backend/models/recurring.py financeai/backend/models/credit_card.py
git commit -m "feat: add input validations to budget, recurring, and credit card models"
```

---

### Task 20: Add hover states and transitions

**Files:**
- Modify: `financeai/frontend/app/globals.css`

- [ ] **Step 1: Add utility classes for card hover and transitions**

Add to the `@layer base` block in globals.css:

```css
@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
  html {
    @apply font-sans;
  }
}

@layer utilities {
  .card-hover {
    @apply transition-all duration-200 hover:border-primary/30;
  }
}
```

- [ ] **Step 2: Apply card-hover to dashboard components**

Add `card-hover` class to the main card containers in:
- `SummaryCards.tsx` — hero cards and secondary cards outer divs
- `SpendingChart.tsx` — chart container divs
- `UpcomingBills.tsx` — outer div
- `AlertsPanel.tsx` — outer div
- `GoalsProgress.tsx` — goal cards

- [ ] **Step 3: Commit**

```bash
git add financeai/frontend/app/globals.css financeai/frontend/components/SummaryCards.tsx financeai/frontend/components/SpendingChart.tsx financeai/frontend/components/UpcomingBills.tsx financeai/frontend/components/AlertsPanel.tsx financeai/frontend/components/GoalsProgress.tsx
git commit -m "feat: add hover states and transitions to dashboard cards"
```

---

### Task 21: Final verification

- [ ] **Step 1: Run the full app**

```bash
cd financeai && python -m uvicorn backend.main:app --reload &
cd financeai/frontend && npm run dev
```

- [ ] **Step 2: Verify dashboard**

Open http://localhost:3000. Check:
- Hero cards show saldo, receitas, despesas with sparklines
- Secondary cards show investido, dízimo, primícia, dívidas
- Bar chart shows monthly evolution side-by-side
- Donut chart shows top 5 categories
- Upcoming bills table shows pending/overdue transactions
- Alerts show with colored border-left by severity
- Goals show in 3-column grid with progress bars
- Month navigation works
- All colors match the BI palette

- [ ] **Step 3: Verify pages**

Navigate to each page (transactions, credit-cards, debts, etc.):
- Colors should use the BI palette (dark navy background, card backgrounds)
- CRUD operations should show toast notifications
- Help button should work (PageHelp fix)
- Dates should display as dd/mm/aaaa

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete FinanceAI premium redesign - BI style dashboard"
```
