# Dízimo & Primícias — Cálculo Automático no Dashboard

**Data:** 2026-04-08
**Status:** Aprovado

## Contexto

O usuário precisa que o sistema calcule automaticamente o dízimo (10% de toda receita do mês) e a primícia (1 dia de trabalho = receita / 30, arredondado pra cima). Esses valores são gerados como transações de despesa com status "pending" e exibidos no dashboard.

## Regras de Negócio

### Dízimo
- **Fórmula:** `soma_receitas_mes * 0.10`
- Calculado sobre todas as transações de type="income" do mês
- Acumula conforme novas receitas entram
- Zera na virada do mês (cada mês tem suas próprias transações)

### Primícia
- **Fórmula:** `math.ceil(soma_receitas_mes / 30)`
- Divisão por 30 dias fixos (independente do mês)
- Arredondamento sempre pra cima
- Mesmas regras de acumulação e reset do dízimo

## Arquitetura — Abordagem A (Cálculo no summary + side-effect em transações)

### Backend

#### 1. Hook na criação/edição/exclusão de transações de income

**Arquivo:** `backend/routes/transactions.py`

Ao criar, editar ou deletar uma transação de type="income":

1. Soma todas as receitas do mês da transação
2. Calcula dízimo: `total_income * 0.10`
3. Calcula primícia: `math.ceil(total_income / 30)`
4. Busca transações existentes de categoria "Dizimo" e "Primicia" no mês
   - Se existem: **atualiza o amount**
   - Se não existem: **cria novas** com:
     - description: `"Dízimo - {Mês}/{Ano}"` ou `"Primícia - {Mês}/{Ano}"`
     - type: `"expense"`
     - category: `"Dizimo"` ou `"Primicia"`
     - status: `"pending"`
     - due_date: último dia do mês
   - Se total_income == 0: **remove** as transações de dízimo/primícia do mês

**Importante:** Se a transação de dízimo/primícia já foi marcada como "paid", o update muda apenas o amount, sem alterar o status.

#### 2. Endpoint `/api/summary/monthly` — campos novos

**Arquivo:** `backend/routes/summary.py`

Adicionar ao response:
```json
{
  "tithe": 150.00,
  "tithe_status": "pending",
  "firstfruits": 50.00,
  "firstfruits_status": "pending"
}
```

Valores lidos diretamente das transações de categoria "Dizimo" e "Primicia" do mês.

#### 3. Categorias novas

Adicionar `"Dizimo"` e `"Primicia"` às categorias válidas no modelo de transação.

### Frontend

#### 1. SummaryCards — 6 cards

**Arquivo:** `frontend/components/SummaryCards.tsx`

Grid passa de 4 para 6 colunas:

| Card | Campo | Ícone | Cor |
|------|-------|-------|-----|
| Saldo do Mês | `balance` | existente | existente |
| Receitas | `income` | existente | existente |
| Despesas | `expenses` | existente | existente |
| Investido | `total_current` | existente | existente |
| Dízimo | `tithe` | igreja/coração | roxo |
| Primícia | `firstfruits` | estrela | dourado |

- Cards de Dízimo e Primícia mostram badge de status ("Pendente" / "Pago")
- Grid responsivo: 6 cols desktop, 3x2 tablet, 2x3 ou 1 col mobile

#### 2. Transações automáticas visíveis

As transações de Dízimo e Primícia aparecem normalmente na lista de transações, onde o usuário pode:
- Visualizar o valor acumulado
- Marcar como "pago" quando efetuar o pagamento
- **Não pode editar o amount manualmente** (é calculado automaticamente)

## Fluxo Completo

```
1. Usuário cadastra receita de R$3.000 (Salário)
   → Backend cria: "Dízimo - Abril/2026" = R$300 (pending)
   → Backend cria: "Primícia - Abril/2026" = R$100 (pending)
   → Dashboard mostra 6 cards com dízimo e primícia

2. Usuário cadastra receita de R$2.000 (Freelance)
   → Backend atualiza: "Dízimo - Abril/2026" = R$500
   → Backend atualiza: "Primícia - Abril/2026" = R$167

3. Usuário marca dízimo como "pago"
   → Card no dashboard muda status para "Pago"

4. Maio começa
   → Novas receitas geram novas transações de dízimo/primícia de maio
   → Valores de abril permanecem no histórico
```

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `backend/routes/transactions.py` | Hook para criar/atualizar dízimo e primícia |
| `backend/routes/summary.py` | Campos tithe, firstfruits no response |
| `backend/models/transaction.py` | Categorias "Dizimo" e "Primicia" |
| `frontend/components/SummaryCards.tsx` | 2 cards novos, grid 6 colunas |

## Fora de Escopo

- Configuração de percentual customizável (fixo em 10%)
- Configuração de dias de trabalho customizável (fixo em 30)
- Relatório separado de dízimos/primícias
- Integração com investimentos (só receitas type="income")
