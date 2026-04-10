import logging
import time

from fastapi import APIRouter, HTTPException
from database import supabase
from models.chat import ChatRequest, ChatResponse
from services.ai import get_ai_provider
from services.chat_tools import TOOL_DEFINITIONS, execute_tool
from datetime import date

logger = logging.getLogger("financeai.chat")

_context_cache: dict = {"text": "", "timestamp": 0}
_CACHE_TTL = 120  # 2 minutes

router = APIRouter(prefix="/api/chat", tags=["chat"])

MENTOR_SYSTEM_PROMPT = """Voce e o FinanceAI, um mentor financeiro pessoal completo e inteligente.

## Seu Papel
Voce e mais do que um assistente — voce e um mentor financeiro dedicado. Seu objetivo e ajudar o usuario a ter controle total das financas, tomar decisoes inteligentes e construir riqueza a longo prazo.

## Suas Capacidades
Voce pode EXECUTAR ACOES no sistema financeiro do usuario:
- Registrar receitas e despesas
- Marcar contas como pagas
- Cadastrar investimentos
- Registrar e gerenciar dividas
- Consultar extratos e resumos
- Verificar alertas de vencimento

Quando o usuario pedir para registrar, adicionar, pagar, ou qualquer acao sobre dados financeiros, USE AS FERRAMENTAS DISPONIVEIS. Nao apenas responda — execute a acao.

## Contexto Financeiro Atual
{context}

## Como Agir

### Registro de Dados
- Quando o usuario disser algo como "gastei 50 reais no mercado", registre automaticamente como despesa de Alimentacao
- Quando disser "recebi meu salario de 5000", registre como receita de Salario
- Sempre confirme o registro: "Registrei a despesa de R$ 50,00 em Alimentacao"
- Se faltar informacao (ex: categoria), pergunte antes de registrar
- Use a data de hoje se o usuario nao especificar

### Mentoria Financeira Proativa
- Analise os dados e ALERTE sobre problemas: gastos excessivos, falta de reserva, contas atrasadas
- Sugira a regra 50-30-20 adaptada a realidade do usuario (50% necessidades, 30% desejos, 20% investimentos)
- Compare gastos mes a mes e aponte tendencias
- Se o usuario gasta muito em uma categoria, sugira alternativas praticas
- Incentive a criacao de reserva de emergencia (6 meses de despesas fixas)
- Sugira investimentos adequados ao perfil (conservador para iniciantes)

### Alertas e Preocupacoes
- Se houver contas vencidas, ALERTE imediatamente com urgencia
- Se os gastos do mes estao acima de 80% da receita, avise
- Se nao ha investimentos, sugira comecar com pouco
- Se uma categoria de gasto cresceu muito, aponte
- Se o saldo esta negativo, proponha um plano de corte

### Educacao Financeira
- Explique conceitos quando relevante: juros compostos, inflacao, diversificacao
- Use exemplos praticos com os numeros reais do usuario
- Sugira metas financeiras atingiveis baseadas na renda
- Ensine sobre armadilhas comuns: parcelamento excessivo, cheque especial, emprestimo para consumo

### Tom de Comunicacao
- Direto e pratico, sem enrolacao
- Use portugues brasileiro natural
- Seja motivador mas realista — nao passe a mao na cabeca
- Use numeros concretos dos dados do usuario
- Formate valores sempre como R$ X.XXX,XX
- Use emojis com moderacao para alertas importantes

### Dividas e Negociacao
- Se o usuario tem dividas, priorize a quitacao: primeiro cheque especial e cartao (juros mais altos), depois emprestimos
- Sugira negociacao direta com o credor — descontos de 40-80% sao comuns para dividas antigas
- Explique sobre prescricao (5 anos para dividas bancarias)
- Para dividas em acordo, acompanhe o progresso e motive
- Nunca julgue o usuario por ter dividas — seja empatico e pratico
- Sugira o metodo avalanche (pagar primeiro a de maior juros) ou bola de neve (pagar primeiro a menor)
- Use as ferramentas create_debt, update_debt e list_debts para gerenciar dividas

### Objetivos e Metas
- Ajude o usuario a priorizar: primeiro quitar dividas de juros altos, depois reserva de emergencia, depois objetivos
- Calcule quanto precisa guardar por mes para atingir cada meta no prazo
- Se o usuario quer algo caro mas tem dividas, seja honesto: "Sugiro quitar X primeiro, depois focar na TV"
- Celebre progresso: "Voce ja tem 40% da meta da TV! Continue assim"
- Sugira estrategias: separar um valor fixo por mes, vender coisas que nao usa, renda extra
- Quando um objetivo for concluido, parabenize e sugira o proximo
- Relacione objetivos com o orcamento: "Se guardar R$ 500/mes, alcanca a meta em 10 meses"
- Use as ferramentas create_goal, update_goal e list_goals para gerenciar objetivos

### Contas Recorrentes
- Quando o usuario disser que paga algo todo mes (agua, luz, internet, aluguel), registre como transacao recorrente
- Use create_recurring para criar e list_recurring para consultar
- Sugira gerar as transacoes pendentes periodicamente

### Orcamento por Categoria
- Quando o usuario definir um orcamento, acompanhe e alerte quando estiver perto do limite
- Se ultrapassou o limite, alerte imediatamente e sugira onde cortar
- Compare gastos reais vs orcamento e de nota (ex: "Voce esta otimo em Transporte, 45% do limite")
- Sugira limites baseados na regra 50-30-20 adaptada a renda do usuario
- Use create_budget para definir limites e get_budget_status para verificar status

### Planejamento Financeiro
- O planejamento funciona em CICLOS DE 3 MESES com revisao ao final. Ja existe um plano completo de Mai-Dez 2026.
- Quando o usuario pedir revisao ou ajuste, use get_plan_vs_actual para ver o que foi pago e o que faltou, depois ajuste os meses seguintes.
- Gere um plano SEPARADO para CADA mes. Use save_financial_plan uma vez por mes.
- Cada plano mensal DEVE ter:
  - Titulo motivacional (ex: "Agosto — SportAcao Cai")
  - Observations com comentario estrategico explicando POR QUE aquele mes e importante, o que negociar, e como se sentir
  - 4 sections: custo_vida, dividas, reserva, sobra
  - Cada item com description, amount e notes com dicas praticas
- Use PSICOLOGIA COMPORTAMENTAL nos textos:
  - Framing de missao ("missao do mes", "voce venceu", "primeira vitoria")
  - Bola de neve pra dividas (menores primeiro = sensacao de progresso)
  - Celebrar conquistas ("6 de 9 quitadas!", "R$ 15k pro carro!")
  - Nunca culpar — sempre motivar e mostrar o caminho
  - Mostrar o antes vs depois ("lembra quando tinha R$ 12.500 em dividas?")

### Prioridades do usuario (RESPEITAR SEMPRE):
1. Despesas fixas + dizimo/primicia (nao negociavel)
2. Dividas — metodo bola de neve (menores primeiro pra ganhar momentum)
3. CARRO — prioridade ALTA. Meta R$ 25.000. Precisa sair em 2026 (Outubro)
4. Reserva de emergencia — R$ 1.500/mes (reduzida pra priorizar carro)
5. Gastos pessoais — R$ 2.000/mes fixo (nao sacrificar demais)
6. Investimentos — comecar apos quitar dividas (Nov/Dez)

### Jornada 2026 (ja planejada):
- Mai: Limpeza (cartao R$ 5k + atrasados + Recovery + Merc.Pago)
- Jun: Estacio + Vivo + carro comeca (R$ 5.746)
- Jul: Ipanema + Nubank + CNH (R$ 1k) + carro R$ 10k
- Ago: SportAcao + carro R$ 15k
- Set: Ipanema grande (negociar desconto!) + carro R$ 19k
- Out: COMPRA DO CARRO (R$ 25k) + ultima divida
- Nov: Livre de dividas! Investir + reserva
- Dez: Consolidacao + 13o salario

### Dados base mensais:
- Receita: R$ 18.099 (Salario Gov R$ 12k + Cebi R$ 3.269 + Paula R$ 2.800 + Wagner R$ 30)
- Custo de vida: R$ 7.336 (fixas + dizimo R$ 1.810 + primicia R$ 603)
- Sobra bruta: R$ 10.763/mes

- IMPORTANTE: receitas fixas (salarios) NAO sao despesas. NUNCA misture.
- Use dados reais: nomes das dividas, valores exatos. Nunca invente.
- Transacoes recorrentes ja estao geradas ate Dezembro/2026. NAO crie duplicatas.

## Regras
- SEMPRE use as ferramentas quando o usuario pedir uma acao
- NUNCA invente dados — use apenas o que esta no sistema
- NUNCA crie transacoes duplicadas. Antes de criar uma transacao, verifique com list_transactions se ja existe uma com a mesma descricao no mesmo mes. Se ja existir, use update_transaction para alterar em vez de criar nova.
- As contas recorrentes ja estao geradas ate Dezembro/2026. NAO crie transacoes manuais para contas que ja existem (aluguel, faculdade, salarios, etc). So crie transacoes para gastos NOVOS e EXTRAS.
- Se nao tem certeza da categoria ou valor, PERGUNTE
- Apos registrar algo, mostre o resumo atualizado se relevante
- Ao dar conselhos, baseie-se nos dados reais, nao em suposicoes
"""


def build_financial_context() -> str:
    """Build a detailed financial context string for the AI system prompt."""
    today = date.today()
    m, y = today.month, today.year
    start = f"{y}-{m:02d}-01"
    end_month = m + 1 if m < 12 else 1
    end_year = y if m < 12 else y + 1
    end = f"{end_year}-{end_month:02d}-01"

    # Monthly transactions
    txns = (
        supabase.table("transactions")
        .select("*")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expenses = sum(t["amount"] for t in txns if t["type"] == "expense")
    balance = income - expenses

    # Expenses by category
    by_category: dict[str, float] = {}
    for t in txns:
        if t["type"] == "expense":
            cat = t["category"]
            by_category[cat] = by_category.get(cat, 0) + t["amount"]
    cat_lines = [f"  - {cat}: R$ {val:.2f}" for cat, val in sorted(by_category.items(), key=lambda x: -x[1])]
    cat_text = "\n".join(cat_lines) if cat_lines else "  Nenhuma despesa registrada"

    # Recent transactions (last 10)
    recent = (
        supabase.table("transactions")
        .select("id, description, amount, type, category, status, due_date")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    ).data
    recent_lines = []
    for t in recent:
        tipo = "Receita" if t["type"] == "income" else "Despesa"
        status_map = {"pending": "Pendente", "paid": "Pago", "overdue": "Vencido"}
        st = status_map.get(t["status"], t["status"])
        recent_lines.append(
            f"  - [{t['id'][:8]}] {tipo}: {t['description']} | R$ {t['amount']:.2f} | {t['category']} | {st} | {t['due_date']}"
        )
    recent_text = "\n".join(recent_lines) if recent_lines else "  Nenhuma transacao recente"

    # Overdue
    overdue = (
        supabase.table("transactions")
        .select("id, description, amount, due_date")
        .eq("status", "overdue")
        .execute()
    ).data
    overdue_count = len(overdue)
    overdue_total = sum(t["amount"] for t in overdue)
    overdue_lines = [
        f"  - [{t['id'][:8]}] {t['description']} | R$ {t['amount']:.2f} | Venceu em {t['due_date']}"
        for t in overdue
    ]
    overdue_text = "\n".join(overdue_lines) if overdue_lines else "  Nenhuma"

    # Investments
    investments = (
        supabase.table("investments")
        .select("id, name, type, institution, invested_amount, current_amount")
        .execute()
    ).data
    invested = sum(i["invested_amount"] for i in investments)
    current = sum(i["current_amount"] for i in investments)
    inv_lines = [
        f"  - [{i['id'][:8]}] {i['name']} ({i['type']}) | {i['institution']} | Investido: R$ {i['invested_amount']:.2f} | Atual: R$ {i['current_amount']:.2f}"
        for i in investments
    ]
    inv_text = "\n".join(inv_lines) if inv_lines else "  Nenhum investimento cadastrado"

    # Open invoices
    open_invoices = (
        supabase.table("card_invoices")
        .select("total_amount, due_date, status, credit_cards(name)")
        .in_("status", ["open", "closed"])
        .execute()
    ).data
    invoice_lines = []
    for inv in open_invoices:
        card_name = inv.get("credit_cards", {}).get("name", "Cartao") if inv.get("credit_cards") else "Cartao"
        invoice_lines.append(f"  - {card_name}: R$ {inv['total_amount']:.2f} | Vence: {inv.get('due_date', 'N/A')} | Status: {inv['status']}")
    invoices_text = "\n".join(invoice_lines) if invoice_lines else "  Nenhuma fatura aberta"

    # Debts
    try:
        all_debts = supabase.table("debts").select("*").execute().data
    except Exception:
        logger.exception("Failed to fetch debts for financial context")
        all_debts = []
    active_debts = [d for d in all_debts if d.get("status") in ("ativa", "negociando")]
    agreement_debts = [d for d in all_debts if d.get("status") == "acordo"]
    settled_debts = [d for d in all_debts if d.get("status") == "quitada"]
    debt_total = sum(d["current_amount"] for d in active_debts)
    monthly_agreement = sum(d.get("monthly_payment") or 0 for d in agreement_debts)
    cat_labels = {
        "cartao": "Cartao", "emprestimo": "Emprestimo", "financiamento": "Financiamento",
        "cheque_especial": "Cheque Especial", "conta_consumo": "Conta de Consumo", "outros": "Outros",
    }
    status_labels = {
        "ativa": "Ativa", "negociando": "Negociando", "acordo": "Em acordo",
        "quitada": "Quitada", "prescrita": "Prescrita",
    }
    debt_detail_lines = []
    for d in all_debts:
        cat = cat_labels.get(d["category"], d["category"])
        st = status_labels.get(d["status"], d["status"])
        line = f"  - [{d['id'][:8]}] {d['creditor']} | {cat} | R$ {d['current_amount']:.2f} | {st}"
        if d.get("monthly_payment"):
            line += f" | Parcela: R$ {d['monthly_payment']:.2f}"
        debt_detail_lines.append(line)
    debts_text = (
        f"- Dividas ativas: {len(active_debts)} (total: R$ {debt_total:.2f})\n"
        f"- Dividas em acordo: {len(agreement_debts)} (parcela mensal total: R$ {monthly_agreement:.2f})\n"
        f"- Dividas quitadas: {len(settled_debts)}\n"
        f"- Detalhes:\n" + ("\n".join(debt_detail_lines) if debt_detail_lines else "  Nenhuma divida cadastrada")
    )

    # Goals
    try:
        all_goals = supabase.table("goals").select("*").execute().data
    except Exception:
        logger.exception("Failed to fetch goals for financial context")
        all_goals = []
    active_goals = [g for g in all_goals if g.get("status") == "ativa"]
    total_target = sum(g["target_amount"] for g in active_goals)
    total_saved = sum(g["saved_amount"] for g in active_goals)
    goals_pct = (total_saved / total_target * 100) if total_target > 0 else 0
    priority_labels = {"alta": "Alta", "media": "Media", "baixa": "Baixa"}
    goal_detail_lines = []
    for g in all_goals:
        prio = priority_labels.get(g["priority"], g["priority"])
        g_pct = (g["saved_amount"] / g["target_amount"] * 100) if g["target_amount"] > 0 else 0
        line = f"  - [{g['id'][:8]}] {g['name']} (Prioridade: {prio}): R$ {g['saved_amount']:.2f} / R$ {g['target_amount']:.2f} ({g_pct:.0f}%)"
        if g.get("target_date"):
            line += f" - Meta: {g['target_date']}"
        if g.get("status") != "ativa":
            status_map = {"pausada": "Pausada", "concluida": "Concluida", "cancelada": "Cancelada"}
            line += f" [{status_map.get(g['status'], g['status'])}]"
        goal_detail_lines.append(line)
    goals_text = (
        f"- Objetivos ativos: {len(active_goals)}\n"
        f"- Total necessario: R$ {total_target:.2f}\n"
        f"- Total guardado: R$ {total_saved:.2f} ({goals_pct:.0f}%)\n"
        f"- Detalhes dos objetivos:\n" + ("\n".join(goal_detail_lines) if goal_detail_lines else "  Nenhum objetivo cadastrado")
    )

    # Recurring transactions
    try:
        all_recurring = supabase.table("recurring_transactions").select("*").eq("is_active", True).execute().data
    except Exception:
        all_recurring = []
    recurring_incomes = [r for r in all_recurring if r["type"] == "income"]
    recurring_expenses = [r for r in all_recurring if r["type"] == "expense"]
    recurring_income_total = sum(r["amount"] for r in recurring_incomes)
    recurring_expense_total = sum(r["amount"] for r in recurring_expenses)
    recurring_income_lines = [
        f"  - {r['description']}: R$ {r['amount']:.2f} ({r['frequency']})"
        for r in recurring_incomes
    ]
    recurring_expense_lines = [
        f"  - {r['description']}: R$ {r['amount']:.2f} ({r['frequency']})"
        for r in recurring_expenses
    ]
    recurring_text = (
        f"- Receitas fixas mensais: {len(recurring_incomes)} (total: R$ {recurring_income_total:.2f})\n"
        + ("\n".join(recurring_income_lines) if recurring_income_lines else "  Nenhuma receita recorrente") + "\n"
        f"- Despesas fixas mensais: {len(recurring_expenses)} (total: R$ {recurring_expense_total:.2f})\n"
        + ("\n".join(recurring_expense_lines) if recurring_expense_lines else "  Nenhuma despesa recorrente")
    )

    # Budgets
    try:
        all_budgets = supabase.table("budgets").select("*").eq("is_active", True).execute().data
    except Exception:
        all_budgets = []

    budget_lines = []
    if all_budgets:
        spent_by_cat_budget: dict[str, float] = {}
        for t in txns:
            if t["type"] == "expense":
                cat = t["category"]
                spent_by_cat_budget[cat] = spent_by_cat_budget.get(cat, 0) + t["amount"]
        for b in all_budgets:
            spent = spent_by_cat_budget.get(b["category"], 0)
            limit_val = b["monthly_limit"]
            pct = (spent / limit_val * 100) if limit_val > 0 else 0
            warning = " ⚠️" if pct >= 80 else ""
            budget_lines.append(f"  - {b['category']}: R$ {spent:.2f} / R$ {limit_val:.2f} ({pct:.0f}%){warning}")
    budgets_text = (
        "- Orcamentos definidos:\n" + ("\n".join(budget_lines) if budget_lines else "  Nenhum orcamento definido")
    )

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
        if p.get("content") and p["content"].get("sections"):
            for s in p["content"]["sections"]:
                plan_lines.append(f"    {s['title']}: R$ {s['total']:.2f}")
                for item in s.get("items", []):
                    plan_lines.append(f"      - {item['description']}: R$ {item['amount']:.2f}")
        if p.get("observations"):
            plan_lines.append(f"    Obs: {p['observations']}")
    plans_text = "\n".join(plan_lines) if plan_lines else "  Nenhum plano cadastrado"

    # Projection: next 3 months with detailed breakdown
    from dateutil.relativedelta import relativedelta
    month_names = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    projection_lines = []
    for offset in range(1, 4):
        proj_date = today + relativedelta(months=offset)
        pm, py = proj_date.month, proj_date.year
        p_start = f"{py}-{pm:02d}-01"
        p_end_month = pm + 1 if pm < 12 else 1
        p_end_year = py if pm < 12 else py + 1
        p_end = f"{p_end_year}-{p_end_month:02d}-01"

        try:
            future_txns = (
                supabase.table("transactions")
                .select("description, amount, type, category, status, due_date")
                .gte("due_date", p_start)
                .lt("due_date", p_end)
                .order("due_date")
                .execute()
            ).data
        except Exception:
            future_txns = []

        f_income = sum(t["amount"] for t in future_txns if t["type"] == "income")
        f_expenses = sum(t["amount"] for t in future_txns if t["type"] == "expense")
        f_balance = f_income - f_expenses

        projection_lines.append(f"\n  [{month_names[pm - 1]} {py}] Receitas: R$ {f_income:.2f} | Despesas: R$ {f_expenses:.2f} | Saldo: R$ {f_balance:.2f}")

        # Group by category for expenses
        f_by_cat: dict[str, float] = {}
        for t in future_txns:
            if t["type"] == "expense":
                f_by_cat[t["category"]] = f_by_cat.get(t["category"], 0) + t["amount"]
        for cat, val in sorted(f_by_cat.items(), key=lambda x: -x[1]):
            projection_lines.append(f"    {cat}: R$ {val:.2f}")

        # List income sources
        income_sources = [t for t in future_txns if t["type"] == "income"]
        if income_sources:
            projection_lines.append("    Fontes de renda:")
            for t in income_sources:
                projection_lines.append(f"      - {t['description']}: R$ {t['amount']:.2f}")

    projection_text = "\n".join(projection_lines) if projection_lines else "  Sem projecao (transacoes futuras nao geradas)"

    # Historical: last 3 months summary for trend analysis
    history_lines = []
    for offset in range(1, 4):
        hist_date = today - relativedelta(months=offset)
        hm, hy = hist_date.month, hist_date.year
        h_start = f"{hy}-{hm:02d}-01"
        h_end_month = hm + 1 if hm < 12 else 1
        h_end_year = hy if hm < 12 else hy + 1
        h_end = f"{h_end_year}-{h_end_month:02d}-01"

        try:
            hist_txns = (
                supabase.table("transactions")
                .select("amount, type")
                .gte("due_date", h_start)
                .lt("due_date", h_end)
                .execute()
            ).data
        except Exception:
            hist_txns = []

        h_income = sum(t["amount"] for t in hist_txns if t["type"] == "income")
        h_expenses = sum(t["amount"] for t in hist_txns if t["type"] == "expense")
        h_balance = h_income - h_expenses
        history_lines.append(f"  {month_names[hm - 1]} {hy}: Receitas R$ {h_income:.2f} | Despesas R$ {h_expenses:.2f} | Saldo R$ {h_balance:.2f}")

    history_text = "\n".join(history_lines) if history_lines else "  Sem historico"

    # Debt payment schedule
    debt_schedule_lines = []
    paying_debts = [d for d in all_debts if d.get("is_paying") and d.get("monthly_payment")]
    for d in paying_debts:
        remaining = d.get("total_installments", 0) - d.get("paid_installments", 0)
        months_left = remaining if remaining > 0 else 0
        line = f"  - {d['creditor']}: R$ {d['monthly_payment']:.2f}/mes"
        if d.get("total_installments"):
            line += f" | {d['paid_installments']}/{d['total_installments']} parcelas pagas | {months_left} restantes"
        if d.get("payment_day"):
            line += f" | Dia {d['payment_day']}"
        debt_schedule_lines.append(line)
    debt_schedule_text = "\n".join(debt_schedule_lines) if debt_schedule_lines else "  Nenhum pagamento de divida ativo"

    return f"""Data de hoje: {today.isoformat()}
Mes atual: {m:02d}/{y}

### Resumo do Mes Atual ({month_names[m - 1]} {y})
- Receitas: R$ {income:.2f}
- Despesas: R$ {expenses:.2f}
- Saldo: R$ {balance:.2f}

### Despesas por Categoria (Mes Atual)
{cat_text}

### Contas Vencidas ({overdue_count} — total: R$ {overdue_total:.2f})
{overdue_text}

### Ultimas 10 Transacoes
{recent_text}

### Historico dos Ultimos 3 Meses (Tendencia)
{history_text}

### Projecao dos Proximos 3 Meses (Baseado em recorrentes + lancamentos futuros)
{projection_text}

### Investimentos (Total investido: R$ {invested:.2f} | Valor atual: R$ {current:.2f})
{inv_text}

### Faturas de Cartao
{invoices_text}

### Dividas
{debts_text}

### Cronograma de Pagamento de Dividas
{debt_schedule_text}

### Objetivos e Metas
{goals_text}

### Contas Fixas (Recorrentes)
{recurring_text}

### Orcamentos por Categoria
{budgets_text}

### Planejamento Financeiro (Ultimos planos)
{plans_text}"""


def get_financial_context() -> str:
    now = time.time()
    if now - _context_cache["timestamp"] < _CACHE_TTL and _context_cache["text"]:
        return _context_cache["text"]
    text = build_financial_context()
    _context_cache["text"] = text
    _context_cache["timestamp"] = now
    return text


@router.post("/")
async def chat(request: ChatRequest):
    try:
        context = get_financial_context()
        system_prompt = MENTOR_SYSTEM_PROMPT.format(context=context)
        provider = get_ai_provider()
        history = [{"role": m.role, "content": m.content} for m in request.history]

        response_text = await provider.generate_response(
            message=request.message,
            history=history,
            system_prompt=system_prompt,
            tools=TOOL_DEFINITIONS,
            tool_executor=execute_tool,
        )

        # Save to chat_history
        supabase.table("chat_history").insert({"role": "user", "content": request.message}).execute()
        supabase.table("chat_history").insert({"role": "assistant", "content": response_text}).execute()

        return ChatResponse(response=response_text)
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail="Erro ao processar mensagem. Tente novamente.")


@router.get("/history")
async def get_chat_history(limit: int = 50):
    result = (
        supabase.table("chat_history")
        .select("*")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data
