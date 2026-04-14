# FinanceAI

Sistema de gestao financeira pessoal com mentor de inteligencia artificial integrado. Nao e so um dashboard — e um agente financeiro que entende suas metas, rastreia seus gastos e executa acoes no seu sistema.

## O que faz

- **Transacoes** — controle de receitas e despesas por categoria, com filtros e busca
- **Dividas** — acompanhamento com metodo bola de neve e status de pagamento
- **Metas** — objetivos financeiros com prioridade, prazo e progresso visual
- **Orcamentos** — limites mensais por categoria com tracking em tempo real
- **Cartoes de credito** — gestao de faturas e totais mensais
- **Investimentos** — portfolio com valor investido vs. valor atual
- **Recorrencias** — transacoes automaticas com suporte a dias uteis
- **Planejamento mensal** — planos gerados com framework de psicologia comportamental
- **Mentor IA** — chat com inteligencia artificial que acessa seus dados reais e executa acoes (criar transacoes, atualizar dividas, ajustar metas)

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI, Python, Pydantic |
| Banco | Supabase (PostgreSQL) |
| IA | Multi-provider (OpenAI, Claude, Gemini) com tool-calling |

## Arquitetura

```
financeai/
├── backend/
│   ├── main.py              # App FastAPI, middleware, rotas
│   ├── config.py            # Variaveis de ambiente
│   ├── database.py          # Cliente Supabase
│   ├── routes/              # Endpoints da API
│   ├── models/              # Schemas Pydantic
│   └── services/
│       ├── ai/              # Providers (OpenAI, Claude, Gemini)
│       ├── chat_tools.py    # ~20 tools que a IA executa
│       ├── alert_service.py # Sistema de alertas
│       └── tithe_service.py # Dizimo e primicias
├── frontend/
│   ├── app/                 # Next.js App Router (paginas)
│   ├── components/          # Componentes React
│   └── lib/                 # API client, utils, helpers
```

## Como rodar

### Pre-requisitos

- Node.js 18+
- Python 3.10+
- Conta no [Supabase](https://supabase.com)
- Chave de API de pelo menos um provider: OpenAI, Anthropic ou Google

### Setup

1. Clone o repositorio:
```bash
git clone https://github.com/rafaelstn/financeIA.git
cd financeIA
```

2. Configure as variaveis de ambiente:
```bash
cp financeai/.env.example financeai/.env
```

Preencha com suas credenciais:
```env
SUPABASE_URL=sua_url
SUPABASE_KEY=sua_key
AI_PROVIDER=openai
OPENAI_API_KEY=sua_key
```

3. Backend:
```bash
cd financeai/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

4. Frontend:
```bash
cd financeai/frontend
npm install
npm run dev
```

5. Acesse `http://localhost:3000`

## Como funciona o Mentor IA

O chat nao e um chatbot generico. Ele recebe o contexto financeiro real do usuario (saldo, dividas, metas, transacoes recentes, alertas) e tem acesso a ~20 ferramentas que executam acoes diretamente no banco:

- Criar, editar e deletar transacoes
- Atualizar status de dividas
- Criar e ajustar metas
- Consultar orcamentos
- Gerar planos financeiros

O sistema usa um loop de tool-calling: a IA decide qual acao tomar, o backend executa, e o resultado volta pra IA refinar a resposta.

## Licenca

MIT
