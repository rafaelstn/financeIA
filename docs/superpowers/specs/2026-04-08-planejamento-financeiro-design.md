# Planejamento Financeiro — Spec

**Data:** 2026-04-08
**Status:** Aprovado

## Contexto

O usuário precisa de uma página dedicada de Planejamento Financeiro onde a IA lê todos os dados do banco (receitas, despesas, dívidas, investimentos, metas) e gera um plano estruturado mês a mês. Todo mês o sistema compara planejado vs realizado automaticamente, o usuário adiciona observações, e pede pra IA ajustar o plano seguinte.

## Funcionalidades

### 1. Página "Planejamento" no sidebar

Nova aba no menu lateral, entre "Objetivos" e "Recorrentes". Layout dividido em:

- **Área principal (esquerda/centro):** plano ativo + histórico
- **Chat lateral (direita):** chat dedicado ao planejamento, mesmo sistema do chat flutuante mas em painel fixo na página

### 2. Plano estruturado

Gerado pela IA e salvo como JSON no banco. Estrutura por mês:

```json
{
  "month": 5,
  "year": 2026,
  "title": "Reestruturação - Maio/2026",
  "summary": "Texto resumo do mês",
  "sections": [
    {
      "category": "dividas",
      "title": "Dívidas a Pagar",
      "items": [
        {"description": "Recovery", "amount": 253.21, "notes": "Quitar à vista - menor valor"},
        {"description": "Mercado Pago", "amount": 334.39, "notes": "Quitar à vista"}
      ],
      "total": 587.60
    },
    {
      "category": "reserva",
      "title": "Reserva / Investimento",
      "items": [
        {"description": "Reserva de emergência", "amount": 500.00, "notes": "Meta: 6 meses de despesas fixas"}
      ],
      "total": 500.00
    },
    {
      "category": "custo_vida",
      "title": "Custo de Vida",
      "items": [
        {"description": "Despesas fixas", "amount": 4737.00, "notes": "Contas recorrentes"},
        {"description": "Dízimo", "amount": 1806.90, "notes": "10% da receita"},
        {"description": "Primícia", "amount": 603.00, "notes": "1 dia de trabalho"}
      ],
      "total": 7146.90
    },
    {
      "category": "sobra",
      "title": "Sobra Livre",
      "items": [
        {"description": "Disponível para uso pessoal", "amount": 9834.50}
      ],
      "total": 9834.50
    }
  ],
  "status": "planejado"
}
```

Status do mês: `"planejado"` | `"em_andamento"` | `"concluido"`

### 3. Planejado vs Realizado (híbrido)

Quando o mês termina (ou a qualquer momento), o sistema:

1. **Puxa automaticamente** as transações reais do mês do banco
2. **Compara** com o que foi planejado por categoria
3. **Mostra** um resumo visual: valor planejado, valor real, diferença (verde se gastou menos, vermelho se gastou mais)
4. **Observações do usuário** — campo de texto livre onde o usuário anota o que aconteceu de diferente
5. A IA usa esse comparativo + observações para ajustar o plano do mês seguinte

### 4. Chat de planejamento

Mesmo motor de chat existente (mesmos providers, mesmo sistema de tools), mas:

- Renderizado como painel lateral fixo na página de Planejamento (não flutuante)
- Contexto adicional: inclui o plano ativo no prompt da IA
- 2 tools novos:
  - `save_financial_plan`: salva/atualiza o plano de um mês no banco
  - `get_plan_vs_actual`: retorna comparativo planejado vs realizado de um mês

### 5. Histórico

Lista de meses anteriores com seus planos, acessíveis abaixo do plano ativo ou via navegação. Cada mês mostra:

- O plano que foi definido
- O comparativo planejado vs realizado
- As observações do usuário
- Status (concluído, em andamento)

## Arquitetura

### Backend

#### Tabela `financial_plans` (Supabase)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | uuid | PK |
| month | int | Mês (1-12) |
| year | int | Ano |
| title | text | Título do plano do mês |
| content | jsonb | Plano estruturado (sections com items) |
| observations | text | Observações do usuário (nullable) |
| status | text | planejado, em_andamento, concluido |
| created_at | timestamptz | Auto |
| updated_at | timestamptz | Auto |

Constraint: unique(month, year) — só um plano por mês.

#### Rota `/api/plans`

- `GET /api/plans` — lista todos os planos (ordenado por year desc, month desc)
- `GET /api/plans/{month}/{year}` — plano de um mês específico
- `POST /api/plans` — cria plano de um mês
- `PUT /api/plans/{plan_id}` — atualiza plano (content, observations, status)
- `DELETE /api/plans/{plan_id}` — remove plano

#### Rota `/api/plans/{month}/{year}/comparison`

Retorna comparativo planejado vs realizado:

```json
{
  "month": 5,
  "year": 2026,
  "plan": { "...plano salvo..." },
  "actual": {
    "income": 18069.00,
    "expenses": 7200.00,
    "by_category": {"Moradia": 1730.00, "Alimentacao": 500.00},
    "debts_paid": ["Recovery", "Mercado Pago"],
    "investments_added": 500.00
  },
  "observations": "Texto do usuário"
}
```

#### Tools novos no chat

1. **`save_financial_plan`**: parâmetros `month`, `year`, `title`, `content` (JSON), `status`. A IA chama esse tool depois de gerar o plano.

2. **`get_plan_vs_actual`**: parâmetros `month`, `year`. Retorna o plano salvo + dados reais do mês para a IA analisar e sugerir ajustes.

### Frontend

#### Página `app/planning/page.tsx`

Layout com 2 colunas:

- **Coluna principal (70%):** plano ativo do mês atual/selecionado + histórico
- **Coluna lateral (30%):** chat de planejamento

#### Componentes

- `PlanningChat.tsx` — chat em painel fixo (reutiliza lógica do Chat.tsx existente)
- `PlanView.tsx` — renderiza o plano estruturado com sections e items
- `PlanComparison.tsx` — mostra planejado vs realizado com barras de comparação
- `PlanHistory.tsx` — lista de meses anteriores com seus planos

### Sidebar

Adicionar link "Planejamento" no Sidebar.tsx, entre "Objetivos" e "Recorrentes", com ícone `ClipboardList` do Lucide.

## Fluxo Completo

```
1. Usuário abre "Planejamento" → página vazia com chat lateral
2. No chat: "Cria meu planejamento a partir de maio"
3. IA lê:
   - Receitas: R$18.069 (3 salários)
   - Despesas fixas: R$4.737 (11 contas recorrentes)
   - Dízimo: R$1.806,90 + Primícia: R$603
   - Dívidas Serasa: R$11.552,33 (8 dívidas)
   - Investimentos: R$0
   - Metas: nenhuma
4. IA gera plano de maio com prioridades:
   - Pagar dívidas menores primeiro (snowball)
   - Separar reserva de emergência
   - Manter custo de vida
   - Sobra livre
5. IA chama save_financial_plan → plano aparece na tela
6. Junho chega → usuário abre planejamento
7. Sistema mostra comparativo maio: planejado vs realizado
8. Usuário adiciona: "Não consegui pagar a Vivo, mas quitei Recovery"
9. Pede: "Ajusta o plano de junho"
10. IA chama get_plan_vs_actual(5, 2026) → analisa → gera plano de junho → salva
```

## Arquivos Impactados

| Ação | Arquivo | Responsabilidade |
|------|---------|------------------|
| Criar | `backend/models/plan.py` | Modelo Pydantic do plano |
| Criar | `backend/routes/plans.py` | CRUD + comparison endpoint |
| Modificar | `backend/main.py` | Registrar rota /api/plans |
| Modificar | `backend/services/chat_tools.py` | 2 tools novos |
| Modificar | `backend/routes/chat.py` | Contexto do plano no prompt |
| Criar | `frontend/app/planning/page.tsx` | Página de planejamento |
| Criar | `frontend/components/PlanningChat.tsx` | Chat lateral fixo |
| Criar | `frontend/components/PlanView.tsx` | Visualização do plano |
| Criar | `frontend/components/PlanComparison.tsx` | Planejado vs Realizado |
| Criar | `frontend/components/PlanHistory.tsx` | Histórico de planos |
| Modificar | `frontend/components/Sidebar.tsx` | Link novo |

## Fora de Escopo

- Exportar plano em PDF
- Compartilhar plano com terceiros
- Plano multi-ano (cada mês é independente, conectado pelo histórico)
- Notificações push sobre o plano
- Edição manual dos valores do plano (só via IA)
