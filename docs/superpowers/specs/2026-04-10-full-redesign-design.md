# FinanceAI — Full Redesign Premium

**Data:** 2026-04-10
**Escopo:** Redesign completo incremental — bug fixes + design system + dashboard premium + páginas secundárias + polish
**Abordagem:** Incremental em 5 fases, app funcional durante todo o processo
**Estilo visual:** BI Analítico — fundo azul escuro, sparklines, donut chart, paleta controlada

---

## Fase 1 — Bug Fixes Críticos

Correções que afetam funcionalidade e dados incorretos. Devem ser resolvidas antes de qualquer trabalho visual.

### Frontend

1. **PageHelp DialogTrigger** (`components/PageHelp.tsx:23`)
   - Bug: prop `render` não é válida no DialogTrigger. Deve usar `asChild` com children.
   - Afeta: todas as páginas que usam PageHelp (transactions, credit-cards, debts, goals, recurring, budgets).

2. **SummaryCards campo Investido** (`components/SummaryCards.tsx:52`)
   - Bug: mostra `total_current` (valor atual) em vez de `total_invested` (valor investido original).
   - Solução: exibir `total_invested` como valor principal. Opcionalmente mostrar rendimento (total_current - total_invested) como subtexto.

3. **Sidebar cor hardcoded** (`components/Sidebar.tsx:52-54`)
   - Bug: `bg-blue-600` hardcoded na sidebar, não respeita design tokens.
   - Solução: usar variável CSS ou classe do design system (será criada na Fase 2).

### Backend

4. **Alertas — ordenação de datas** (`services/alert_service.py:211-213`)
   - Bug: ordena `due_date` como string, não como data. "2026-12-01" > "2026-02-01" alfabeticamente (errado).
   - Solução: parsear data antes de ordenar.

5. **Chat — exposição de exceções** (`routes/chat.py:393-395`)
   - Bug: `detail=str(e)` expõe mensagens de erro internas ao cliente.
   - Solução: retornar mensagem genérica ("Erro ao processar mensagem") e logar o erro detalhado.

6. **Overdue check como side-effect** (`services/alert_service.py:9-24`)
   - Bug: `check_and_update_overdue()` roda em toda chamada GET de alertas, modificando dados em operação de leitura.
   - Solução: mover para endpoint POST dedicado ou chamar apenas uma vez na startup + quando transações são criadas/editadas.

7. **Chat build_financial_context — performance** (`routes/chat.py:120-369`)
   - Bug: 15+ queries sequenciais no banco a cada mensagem de chat, sem cache.
   - Solução: implementar cache com TTL de 2-5 minutos usando variável em memória (dict com timestamp).

8. **Tithe sync excessivo** (`routes/transactions.py:54-56, 78-80`)
   - Bug: `sync_tithe_and_firstfruits()` recalcula em toda criação/update de transação.
   - Solução: debounce — só recalcular se a transação for do tipo `income`.

---

## Fase 2 — Design System

Criar a fundação visual que será usada em todas as páginas. Não muda layout, apenas estabelece tokens e componentes base.

### Paleta de cores (CSS custom properties)

```
--bg-base: #0c1222          (fundo principal)
--bg-card: #111a2e          (fundo dos cards)
--bg-card-inner: #0f1825    (fundo interno/nested)
--border-card: #1e2d4a      (borda dos cards)
--border-subtle: #0f1825    (separadores internos)

--text-primary: #e2e8f0     (textos principais)
--text-secondary: #94a3b8   (textos secundários)
--text-muted: #64748b       (labels, hints)
--text-dim: #475569         (textos de menor importância)

--accent-blue: #60a5fa      (cor primária, barras, progresso, links)
--accent-green: #4ade80     (positivo, pago, receitas)
--accent-red: #f87171       (negativo, atrasado, despesas)
--accent-amber: #fbbf24     (atenção, pendente)
--accent-purple: #c084fc    (categorias, destaques secundários)
--accent-emerald: #34d399   (categorias)

--status-paid-bg: rgba(74, 222, 128, 0.08)
--status-paid-text: #4ade80
--status-overdue-bg: rgba(248, 113, 113, 0.08)
--status-overdue-text: #fca5a5
--status-pending-bg: rgba(251, 191, 36, 0.06)
--status-pending-text: #fde68a
--status-info-bg: rgba(96, 165, 250, 0.06)
--status-info-text: #93c5fd
```

### Tipografia

```
--font-size-xs: 8px         (labels uppercase)
--font-size-sm: 9px         (subtextos)
--font-size-base: 10px      (corpo)
--font-size-md: 11px        (tabelas)
--font-size-lg: 15-16px     (valores nos cards)
--font-size-xl: 24px        (valores hero)
--font-size-title: 16px     (títulos de página)

--letter-spacing-label: 1px (labels uppercase)
```

### Espaçamento

```
--space-xs: 4px
--space-sm: 8px
--space-md: 10px
--space-base: 12px
--space-lg: 14px
--space-xl: 16px
--space-2xl: 20px
--space-3xl: 24px
```

### Componentes base (aplicar no globals.css + criar utilitários)

- **Card**: `bg-card`, `border-card`, `rounded-[10px]`, `p-[14px]`
- **Card inner**: `bg-card-inner`, `border-card`, `rounded-[8px]`, `p-[12px]`
- **Label**: `text-muted`, `text-xs`, `uppercase`, `tracking-wide`
- **Value large**: `text-primary`, `text-xl`, `font-bold`
- **Value medium**: `text-primary`, `text-lg`, `font-semibold`
- **Status badge**: padding `2px 7px`, `rounded-full`, `text-[7px]`, `font-medium`, cores por status
- **Alert card**: `border-l-3`, background status com opacidade, `rounded-[8px]`, `p-[10px]`
- **Table row**: grid columns, `py-[5px]`, `border-bottom border-subtle`
- **Progress bar**: `h-[4px]`, `bg-[--border-card]`, inner `bg-accent-blue`, `rounded-[2px]`

### Arquivos a criar/modificar

- `frontend/app/globals.css` — adicionar custom properties acima
- `frontend/lib/utils.ts` — já tem `formatDate`, adicionar helpers se necessário
- **Não criar componentes novos ainda** — os tokens vão ser aplicados inline/tailwind nas fases seguintes

---

## Fase 3 — Dashboard Premium

Redesign completo do dashboard (`app/page.tsx` + componentes).

### Layout do dashboard (aprovado no mockup v4)

**Row 1 — Hero Cards (3 colunas)**
- **Saldo**: valor grande verde, sparkline SVG de fundo, badge "+X% positivo/negativo"
- **Receitas**: valor grande branco, sparkline azul, "N fontes de renda"
- **Despesas**: valor grande branco, sparkline roxo, "X% da receita"

Cada hero card tem gradiente sutil no fundo (não neon, sutil) e SVG polyline como background decorativo com opacidade baixa.

**Row 2 — Cards secundários (4 colunas)**
- **Investido**: valor, sem status
- **Dízimo**: valor + badge status (pago/pendente)
- **Primícia**: valor + badge status
- **Dívidas**: valor total + "N ativas"

Cards com fundo `--bg-card`, borda `--border-card`, sem gradientes.

**Row 3 — Gráficos (grid 1.5fr 1fr)**
- **Evolução mensal** (esquerda): barras lado a lado (azul=receitas, vermelho=despesas), grid lines de fundo, mês atual com opacidade reduzida (projeção). Usar Recharts BarChart.
- **Top 5 categorias** (direita): Donut chart SVG com valor total no centro + legenda lateral com nome, cor e valor. Usar Recharts PieChart.

**Row 4 — Operacional (grid 1fr 1fr)**
- **Próximos vencimentos** (esquerda): tabela com header (Conta | Vence | Valor), linhas separadas por border sutil, dados vindos de `recurring_transactions` + `transactions` com status pending.
- **Alertas** (direita): cards com border-left colorida por severidade (vermelho=atrasado, amarelo=atenção, azul=info). Dados do endpoint `/api/alerts`.

**Row 5 — Metas (grid 3 colunas)**
- Cards com nome, percentual, progress bar (cor única `--accent-blue`), valores "R$ X / R$ Y".
- Link "Ver todas" no header.

### Dados necessários do backend

O dashboard atual já busca `/api/summary/monthly`. Dados adicionais necessários:

1. **Próximos vencimentos**: novo campo no summary OU query separada combinando:
   - `transactions` com `status=pending` e `due_date` nos próximos 30 dias
   - `recurring_transactions` ativas com `next_due_date` nos próximos 30 dias

2. **Dados anuais por mês**: já existe em `/api/summary/yearly` mas precisa retornar breakdown mês a mês (já retorna).

3. **Alertas**: já existe em `/api/alerts`.

4. **Metas**: já existe em `/api/goals?status=ativa`.

### Endpoint novo: GET /api/summary/upcoming

Retorna as próximas contas a vencer (30 dias), combinando transações pending + recorrentes ativas:

```json
{
  "upcoming": [
    {
      "description": "DAS MEI Mensal",
      "amount": 86.00,
      "due_date": "2026-04-14",
      "source": "transaction",
      "days_until": 4
    }
  ]
}
```

### Componentes a criar/modificar

- `components/SummaryCards.tsx` → **reescrever** — hero cards com sparkline + cards secundários
- `components/SpendingChart.tsx` → **reescrever** — barras lado a lado (Recharts) + donut chart
- `components/UpcomingBills.tsx` → **novo** — tabela de próximos vencimentos
- `components/AlertsPanel.tsx` → **modificar** — novo visual com border-left
- `components/GoalsProgress.tsx` → **modificar** — novo layout em grid com progress bars
- `app/page.tsx` → **reescrever layout** — novo grid com as 5 rows

---

## Fase 4 — Páginas Secundárias

Aplicar o design system em todas as páginas. Não redesenhar layouts, mas atualizar cores, tipografia, cards e tabelas para o novo padrão.

### Páginas a atualizar

1. **Transações** (`app/transactions/page.tsx`)
   - Fundo `--bg-base`, cards `--bg-card`, tabela com novo estilo
   - Status badges com cores do design system
   - Toast notifications para operações CRUD (usar sonner ou similar)

2. **Cartões de crédito** (`app/credit-cards/page.tsx`)
   - Mesma aplicação de tokens
   - Cards de cartão com visual melhorado

3. **Dívidas** (`app/debts/page.tsx`)
   - Aplicar tokens
   - Melhorar visualização de parcelas (mostrar "X de Y pagas", progress bar)

4. **Investimentos** (`app/investments/page.tsx`)
   - Aplicar tokens
   - Melhorar card de rendimento (cor verde/vermelha)

5. **Recorrentes** (`app/recurring/page.tsx`)
   - Aplicar tokens

6. **Orçamentos** (`app/budgets/page.tsx`)
   - Aplicar tokens
   - Barras de progresso com cores do design system

7. **Metas** (`app/goals/page.tsx`)
   - Aplicar tokens

8. **Planejamento** (`app/planning/page.tsx`)
   - Aplicar tokens

### Componentes transversais

- **Toast/Notifications**: instalar `sonner` e adicionar feedback para todas operações CRUD em todas as páginas
- **Sidebar**: atualizar cores para o design system (fundo `--bg-card`, hover com `--border-card`, ativa com `--accent-blue`)
- **Layout**: mudar fundo do `body` para `--bg-base`
- **PageHelp**: corrigir bug (Fase 1) e atualizar visual

---

## Fase 5 — Polish

Refinamentos finais para nível premium.

### Melhorias visuais
- **Loading skeletons**: substituir "Carregando..." por skeletons animados nos cards e tabelas
- **Empty states**: substituir "Sem dados" por mensagens contextuais com sugestão de ação
- **Hover states**: cards com `hover:border-[--accent-blue]` sutil em transições suaves
- **Transitions**: `transition-all duration-200` em cards e botões

### Melhorias funcionais
- **Responsividade básica**: sidebar colapsável em telas < 1024px, grid do dashboard ajusta colunas
- **Validações backend pendentes**:
  - `budget.py`: validar `monthly_limit > 0`
  - `recurring.py`: validar `amount > 0`, `business_day_number` entre 1-23
  - `credit_card.py`: validar `closing_day` e `due_day` entre 1-31
  - `goal.py`: validar `target_date` no futuro
  - `investment.py`: validar `maturity_date > start_date`
- **Paginação**: adicionar em `budgets`, `investments`, `goals` (endpoints que não tem)
- **Categorias centralizadas**: criar constante única com todas as categorias no backend para evitar divergência

### Não incluso neste redesign
- Autenticação (decisão do usuário: ignorar por agora)
- Rate limiting
- Testes automatizados
- Internacionalização
- PWA / mobile app

---

## Resumo das fases

| Fase | Escopo | Entrega |
|------|--------|---------|
| 1 | Bug fixes | 8 correções (3 frontend, 5 backend) |
| 2 | Design system | Tokens CSS, paleta, tipografia, espaçamento |
| 3 | Dashboard | 5 rows, sparklines, donut, tabela, alertas, endpoint novo |
| 4 | Páginas | 8 páginas atualizadas, toasts, sidebar, layout |
| 5 | Polish | Skeletons, empty states, hover, responsividade, validações |
