from fastapi import APIRouter, HTTPException
from database import supabase
from models.chat import ChatRequest, ChatResponse
from services.ai import get_ai_provider
from services.chat_tools import TOOL_DEFINITIONS, execute_tool
from datetime import date

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

## Regras
- SEMPRE use as ferramentas quando o usuario pedir uma acao
- NUNCA invente dados — use apenas o que esta no sistema
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

    return f"""Data de hoje: {today.isoformat()}
Mes atual: {m:02d}/{y}

### Resumo do Mes
- Receitas: R$ {income:.2f}
- Despesas: R$ {expenses:.2f}
- Saldo: R$ {balance:.2f}

### Despesas por Categoria
{cat_text}

### Contas Vencidas ({overdue_count} — total: R$ {overdue_total:.2f})
{overdue_text}

### Ultimas 10 Transacoes
{recent_text}

### Investimentos (Total investido: R$ {invested:.2f} | Valor atual: R$ {current:.2f})
{inv_text}

### Faturas de Cartao
{invoices_text}

### Dividas
{debts_text}

### Objetivos e Metas
{goals_text}"""


@router.post("/")
async def chat(request: ChatRequest):
    try:
        context = build_financial_context()
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
        raise HTTPException(status_code=500, detail=str(e))


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
