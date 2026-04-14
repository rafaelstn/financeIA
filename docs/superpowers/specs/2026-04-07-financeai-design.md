# FinanceAI — Design Spec

## Visao Geral

Sistema financeiro pessoal completo com dashboard, CRUD de transacoes/cartoes/investimentos, alertas automaticos e chat com IA que tem contexto financeiro do usuario. Uso pessoal, sem autenticacao.

## Stack

- **Backend:** Python + FastAPI + supabase-py + Pydantic
- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui + Recharts
- **IA:** Multi-provider (Gemini padrao, suporte a Claude e OpenAI via Strategy Pattern)
- **Banco:** Supabase (PostgreSQL gerenciado)

## Arquitetura

```
Frontend (Next.js :3000) --HTTP/REST--> Backend (FastAPI :8000) --> Supabase
                                                |
                                         AI Service (Strategy)
                                         ├── Gemini (ativo)
                                         ├── Claude
                                         └── OpenAI
```

- Frontend faz chamadas REST ao backend (`/api/*`)
- Backend e o unico que se comunica com Supabase e com os providers de IA
- Provider ativo definido por `AI_PROVIDER=gemini` no `.env`
- Trocar provider = editar `.env` + reiniciar backend

## Estrutura de Pastas

```
financeai/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, rotas
│   ├── database.py                # Cliente Supabase
│   ├── config.py                  # Settings do .env
│   ├── models/
│   │   ├── transaction.py         # Pydantic models transacoes
│   │   ├── credit_card.py         # Pydantic models cartoes/faturas/lancamentos
│   │   ├── investment.py          # Pydantic models investimentos
│   │   └── alert.py               # Pydantic models alertas
│   ├── routes/
│   │   ├── transactions.py        # CRUD transacoes
│   │   ├── credit_cards.py        # CRUD cartoes + faturas + lancamentos
│   │   ├── investments.py         # CRUD investimentos
│   │   ├── summary.py             # Resumos mensais/anuais
│   │   ├── chat.py                # Chat com IA
│   │   └── alerts.py              # Alertas ativos
│   ├── services/
│   │   ├── ai/
│   │   │   ├── __init__.py        # Factory get_ai_provider()
│   │   │   ├── base.py            # ABC AIProvider
│   │   │   ├── gemini_provider.py
│   │   │   ├── claude_provider.py
│   │   │   └── openai_provider.py
│   │   └── alert_service.py       # Logica de alertas
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx             # Layout com sidebar + dark mode
│   │   ├── page.tsx               # Dashboard
│   │   ├── transactions/
│   │   │   └── page.tsx           # CRUD transacoes
│   │   ├── credit-cards/
│   │   │   └── page.tsx           # CRUD cartoes
│   │   └── investments/
│   │       └── page.tsx           # CRUD investimentos
│   ├── components/
│   │   ├── Chat.tsx               # Chat flutuante
│   │   ├── AlertsPanel.tsx        # Painel de alertas
│   │   ├── SummaryCards.tsx        # Cards de resumo
│   │   ├── SpendingChart.tsx      # Graficos pizza + barras
│   │   └── Sidebar.tsx            # Navegacao lateral
│   └── lib/
│       └── api.ts                 # Axios client
├── .env
└── README.md
```

## Banco de Dados

### Tabelas

**transactions** — contas a pagar e receber
- `id` UUID PK
- `description` TEXT NOT NULL
- `amount` DECIMAL(10,2) NOT NULL
- `type` TEXT ('income' | 'expense')
- `category` TEXT NOT NULL
- `status` TEXT ('pending' | 'paid' | 'overdue') DEFAULT 'pending'
- `due_date` DATE
- `paid_date` DATE
- `notes` TEXT
- `created_at` TIMESTAMP

**credit_cards** — cartoes cadastrados
- `id` UUID PK
- `name` TEXT NOT NULL
- `bank` TEXT NOT NULL
- `limit_amount` DECIMAL(10,2) NOT NULL
- `closing_day` INTEGER NOT NULL
- `due_day` INTEGER NOT NULL
- `created_at` TIMESTAMP

**card_invoices** — faturas mensais
- `id` UUID PK
- `card_id` UUID FK -> credit_cards
- `month` INTEGER
- `year` INTEGER
- `total_amount` DECIMAL(10,2) DEFAULT 0
- `status` TEXT ('open' | 'closed' | 'paid') DEFAULT 'open'
- `due_date` DATE
- `created_at` TIMESTAMP

**card_expenses** — lancamentos das faturas
- `id` UUID PK
- `invoice_id` UUID FK -> card_invoices
- `description` TEXT NOT NULL
- `amount` DECIMAL(10,2) NOT NULL
- `category` TEXT NOT NULL
- `expense_date` DATE NOT NULL
- `installments` INTEGER DEFAULT 1
- `installment_number` INTEGER DEFAULT 1
- `created_at` TIMESTAMP

**investments** — investimentos
- `id` UUID PK
- `name` TEXT NOT NULL
- `type` TEXT NOT NULL
- `institution` TEXT NOT NULL
- `invested_amount` DECIMAL(10,2) NOT NULL
- `current_amount` DECIMAL(10,2) NOT NULL
- `start_date` DATE NOT NULL
- `maturity_date` DATE
- `notes` TEXT
- `created_at` TIMESTAMP
- `updated_at` TIMESTAMP

**chat_history** — historico de conversa
- `id` UUID PK
- `role` TEXT ('user' | 'assistant')
- `content` TEXT NOT NULL
- `created_at` TIMESTAMP

**settings** — configuracoes do sistema
- `key` TEXT PK
- `value` TEXT NOT NULL
- `updated_at` TIMESTAMP

### Categorias padrao
Alimentacao, Moradia, Transporte, Saude, Lazer, Educacao, Salario, Freelance, Investimento, Outros

## API — Endpoints

| Metodo | Rota | Funcao |
|--------|------|--------|
| GET | `/` | Health check |
| GET/POST/PUT/DELETE | `/api/transactions` | CRUD transacoes |
| GET/POST/PUT/DELETE | `/api/credit-cards` | CRUD cartoes |
| GET/POST/PUT/DELETE | `/api/credit-cards/{id}/invoices` | CRUD faturas |
| GET/POST/PUT/DELETE | `/api/credit-cards/{id}/invoices/{inv_id}/expenses` | CRUD lancamentos |
| GET/POST/PUT/DELETE | `/api/investments` | CRUD investimentos |
| GET | `/api/summary/monthly?month=MM&year=YYYY` | Resumo mensal |
| GET | `/api/summary/yearly?year=YYYY` | Resumo anual |
| GET | `/api/alerts` | Alertas ativos |
| POST | `/api/chat` | Chat com IA |
| GET | `/api/chat/history` | Historico de chat |

## AI Service — Strategy Pattern

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str: ...

def get_ai_provider() -> AIProvider:
    # Retorna provider baseado em AI_PROVIDER do .env
    # "gemini" -> GeminiProvider
    # "claude" -> ClaudeProvider
    # "openai" -> OpenAIProvider
```

### Chat Flow
1. Frontend envia `{ message, history }` para `POST /api/chat`
2. Backend busca contexto financeiro do Supabase:
   - Total receitas/despesas do mes atual
   - Saldo (receitas - despesas)
   - Contas vencidas (count + total)
   - Total investido vs valor atual
   - Faturas abertas dos cartoes
3. Monta system prompt com dados reais
4. Chama provider ativo
5. Salva par user/assistant no `chat_history`
6. Retorna resposta da IA

### System Prompt Template
```
Voce e um assistente financeiro pessoal inteligente e direto.
Contexto financeiro atual do usuario:
- Receitas do mes: R$ {income}
- Despesas do mes: R$ {expenses}
- Saldo atual: R$ {balance}
- Contas em atraso: {overdue_count} (total: R$ {overdue_total})
- Total investido: R$ {invested} | Valor atual: R$ {current}
- Faturas abertas: {open_invoices}

Responda em portugues, seja objetivo e ofereca dicas praticas baseadas nos dados acima.
```

## Alert Service

Funcao `get_active_alerts()`:
- Transacoes pendentes com `due_date` em <= 3 dias -> nivel `warning`
- Transacoes pendentes com `due_date` no passado -> marca como `overdue` + nivel `danger`
- Faturas de cartao com `due_date` em <= 5 dias -> nivel `warning`

## Frontend

### Estilo
- Dark mode (zinc/slate do Tailwind)
- Acentos: verde (receitas), vermelho (despesas), azul (investimentos)
- shadcn/ui para componentes base
- Recharts para graficos

### Dashboard
- Topo: 4 cards de resumo (Saldo, Receitas, Despesas, Investido)
- Meio: grafico pizza (gastos por categoria) + grafico barras (receitas x despesas mensal)
- Abaixo: painel de alertas com badges coloridos (warning=amarelo, danger=vermelho)

### Paginas CRUD
- Tabela com registros + badges de status
- Botao "Adicionar" abre modal com formulario
- Filtros por periodo e categoria
- Cartoes: expansivel para faturas -> lancamentos

### Chat Flutuante
- Botao fixo no canto inferior direito
- Abre painel ~400px a direita
- Bolhas diferenciadas (usuario vs IA)
- Indicador "digitando..." durante chamada
- Scroll automatico
- Envio por Enter ou botao

### Sidebar
- Fixa a esquerda
- Navegacao: Dashboard, Transacoes, Cartoes de Credito, Investimentos
- Icones + labels

## Configuracao (.env)

```
SUPABASE_URL=<url>
SUPABASE_KEY=<service_role_key>
AI_PROVIDER=gemini
GEMINI_API_KEY=<key>
ANTHROPIC_API_KEY=<key>       # opcional, para quando trocar
OPENAI_API_KEY=<key>          # opcional, para quando trocar
```

## Decisoes de Design

1. **Multi-provider via Strategy Pattern** — troca editando `.env`, sem complexidade de runtime
2. **Tabela settings** — preparacao para troca dinamica futura, sem uso ativo agora
3. **Backend como unico gateway** — frontend nunca acessa Supabase ou IA diretamente
4. **Dark mode padrao** — sem toggle light/dark por simplicidade
5. **Chat stateless** — historico enviado pelo frontend a cada mensagem, salvo no banco para persistencia entre sessoes
6. **Sem autenticacao** — uso pessoal local
