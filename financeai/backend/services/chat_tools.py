import json
from datetime import date
from database import supabase
from services.alert_service import get_active_alerts


TOOL_DEFINITIONS = [
    {
        "name": "create_transaction",
        "description": "Cria uma nova transacao (receita ou despesa). Use quando o usuario pedir para registrar, adicionar ou lancar uma conta, gasto, receita ou pagamento.",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Descricao da transacao"},
                "amount": {"type": "number", "description": "Valor em reais"},
                "type": {"type": "string", "enum": ["income", "expense"], "description": "income=receita, expense=despesa"},
                "category": {
                    "type": "string",
                    "enum": ["Alimentacao", "Moradia", "Transporte", "Saude", "Lazer", "Educacao", "Salario", "Freelance", "Investimento", "Outros"],
                    "description": "Categoria da transacao",
                },
                "status": {"type": "string", "enum": ["pending", "paid", "overdue"], "description": "Status: pending=pendente, paid=pago, overdue=vencido"},
                "due_date": {"type": "string", "description": "Data de vencimento no formato YYYY-MM-DD"},
                "paid_date": {"type": "string", "description": "Data de pagamento no formato YYYY-MM-DD (se ja pago)"},
                "notes": {"type": "string", "description": "Observacoes opcionais"},
            },
            "required": ["description", "amount", "type", "category"],
        },
    },
    {
        "name": "update_transaction",
        "description": "Atualiza uma transacao existente. Use para marcar como pago, alterar valor, mudar status, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "ID da transacao a atualizar"},
                "description": {"type": "string"},
                "amount": {"type": "number"},
                "type": {"type": "string", "enum": ["income", "expense"]},
                "category": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "paid", "overdue"]},
                "due_date": {"type": "string"},
                "paid_date": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["transaction_id"],
        },
    },
    {
        "name": "delete_transaction",
        "description": "Remove uma transacao. Use quando o usuario pedir para apagar ou remover uma transacao.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "ID da transacao a remover"},
            },
            "required": ["transaction_id"],
        },
    },
    {
        "name": "list_transactions",
        "description": "Lista transacoes com filtros opcionais. Use para consultar gastos, receitas, buscar transacoes especificas.",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["income", "expense"], "description": "Filtrar por tipo"},
                "category": {"type": "string", "description": "Filtrar por categoria"},
                "status": {"type": "string", "enum": ["pending", "paid", "overdue"], "description": "Filtrar por status"},
                "month": {"type": "integer", "description": "Mes (1-12)"},
                "year": {"type": "integer", "description": "Ano"},
            },
        },
    },
    {
        "name": "create_investment",
        "description": "Registra um novo investimento.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nome do investimento"},
                "type": {"type": "string", "description": "Tipo: CDB, Acoes, FII, Tesouro, Poupanca, Cripto, etc"},
                "institution": {"type": "string", "description": "Instituicao financeira"},
                "invested_amount": {"type": "number", "description": "Valor investido"},
                "current_amount": {"type": "number", "description": "Valor atual"},
                "start_date": {"type": "string", "description": "Data de inicio YYYY-MM-DD"},
                "maturity_date": {"type": "string", "description": "Data de vencimento YYYY-MM-DD (se aplicavel)"},
                "notes": {"type": "string"},
            },
            "required": ["name", "type", "institution", "invested_amount", "current_amount", "start_date"],
        },
    },
    {
        "name": "update_investment",
        "description": "Atualiza um investimento existente. Use para atualizar valor atual, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "investment_id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string"},
                "institution": {"type": "string"},
                "invested_amount": {"type": "number"},
                "current_amount": {"type": "number"},
                "start_date": {"type": "string"},
                "maturity_date": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["investment_id"],
        },
    },
    {
        "name": "get_monthly_summary",
        "description": "Obtem resumo financeiro de um mes especifico. Retorna receitas, despesas, saldo e gastos por categoria.",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {"type": "integer", "description": "Mes (1-12)"},
                "year": {"type": "integer", "description": "Ano"},
            },
        },
    },
    {
        "name": "get_alerts",
        "description": "Lista alertas ativos: contas vencidas e proximas do vencimento.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "create_debt",
        "description": "Registra uma divida antiga ou atual. Use quando o usuario mencionar dividas, debitos pendentes, emprestimos nao pagos, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "creditor": {"type": "string", "description": "Nome do credor (banco, loja, pessoa)"},
                "original_amount": {"type": "number", "description": "Valor original da divida"},
                "current_amount": {"type": "number", "description": "Valor atualizado com juros/multa"},
                "category": {
                    "type": "string",
                    "enum": ["cartao", "emprestimo", "financiamento", "cheque_especial", "conta_consumo", "outros"],
                },
                "status": {
                    "type": "string",
                    "enum": ["ativa", "negociando", "acordo", "quitada", "prescrita"],
                    "description": "ativa=nao paga, negociando=em negociacao, acordo=pagando acordo, quitada=paga, prescrita=mais de 5 anos",
                },
                "origin_date": {"type": "string", "description": "Data de origem da divida YYYY-MM-DD"},
                "is_paying": {"type": "boolean", "description": "Se esta pagando atualmente"},
                "monthly_payment": {"type": "number", "description": "Valor da parcela mensal (se em acordo)"},
                "notes": {"type": "string"},
            },
            "required": ["creditor", "original_amount", "current_amount", "category", "origin_date"],
        },
    },
    {
        "name": "update_debt",
        "description": "Atualiza uma divida existente. Use para mudar status, registrar pagamento, atualizar valor, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "debt_id": {"type": "string"},
                "creditor": {"type": "string"},
                "original_amount": {"type": "number"},
                "current_amount": {"type": "number"},
                "category": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["ativa", "negociando", "acordo", "quitada", "prescrita"],
                },
                "is_paying": {"type": "boolean"},
                "monthly_payment": {"type": "number"},
                "paid_installments": {"type": "integer"},
                "notes": {"type": "string"},
            },
            "required": ["debt_id"],
        },
    },
    {
        "name": "list_debts",
        "description": "Lista todas as dividas com filtros opcionais.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["ativa", "negociando", "acordo", "quitada", "prescrita"],
                },
                "category": {"type": "string"},
            },
        },
    },
    {
        "name": "create_goal",
        "description": "Registra um novo objetivo ou meta financeira. Use quando o usuario disser que quer comprar algo, juntar dinheiro para algo, realizar um sonho, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nome do objetivo (ex: TV 65\", Viagem Europa)"},
                "target_amount": {"type": "number", "description": "Valor total necessario"},
                "category": {
                    "type": "string",
                    "enum": ["eletronico", "veiculo", "imovel", "viagem", "educacao", "saude", "lazer", "outros"],
                    "description": "Categoria do objetivo",
                },
                "saved_amount": {"type": "number", "description": "Valor ja guardado (default 0)"},
                "priority": {
                    "type": "string",
                    "enum": ["alta", "media", "baixa"],
                    "description": "Prioridade do objetivo",
                },
                "target_date": {"type": "string", "description": "Data alvo no formato YYYY-MM-DD"},
                "notes": {"type": "string", "description": "Observacoes opcionais"},
            },
            "required": ["name", "target_amount", "category"],
        },
    },
    {
        "name": "update_goal",
        "description": "Atualiza um objetivo existente. Use para adicionar valor guardado, mudar prioridade, marcar como concluido, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "string", "description": "ID do objetivo a atualizar"},
                "name": {"type": "string"},
                "target_amount": {"type": "number"},
                "saved_amount": {"type": "number"},
                "priority": {"type": "string", "enum": ["alta", "media", "baixa"]},
                "category": {
                    "type": "string",
                    "enum": ["eletronico", "veiculo", "imovel", "viagem", "educacao", "saude", "lazer", "outros"],
                },
                "status": {"type": "string", "enum": ["ativa", "pausada", "concluida", "cancelada"]},
                "target_date": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["goal_id"],
        },
    },
    {
        "name": "list_goals",
        "description": "Lista objetivos e metas financeiras com filtros opcionais.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["ativa", "pausada", "concluida", "cancelada"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["alta", "media", "baixa"],
                },
            },
        },
    },
    {
        "name": "create_recurring",
        "description": "Cria uma transacao recorrente (conta fixa mensal). Use quando o usuario disser que paga algo todo mes, como agua, luz, internet, aluguel.",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Descricao da conta recorrente"},
                "amount": {"type": "number", "description": "Valor em reais"},
                "type": {"type": "string", "enum": ["income", "expense"], "description": "income=receita, expense=despesa"},
                "category": {
                    "type": "string",
                    "enum": ["Alimentacao", "Moradia", "Transporte", "Saude", "Lazer", "Educacao", "Salario", "Freelance", "Investimento", "Outros"],
                    "description": "Categoria",
                },
                "frequency": {"type": "string", "enum": ["monthly", "weekly", "yearly"], "description": "Frequencia: monthly=mensal, weekly=semanal, yearly=anual"},
                "day_of_month": {"type": "integer", "description": "Dia do mes para vencimento"},
                "next_due_date": {"type": "string", "description": "Proxima data de vencimento YYYY-MM-DD (opcional se use_business_day=true)"},
                "use_business_day": {"type": "boolean", "description": "Se true, usa dia util ao inves de dia fixo. Ex: 5o dia util do mes"},
                "business_day_number": {"type": "integer", "description": "Numero do dia util (ex: 5 = quinto dia util do mes)"},
                "notes": {"type": "string", "description": "Observacoes opcionais"},
            },
            "required": ["description", "amount", "type", "category"],
        },
    },
    {
        "name": "list_recurring",
        "description": "Lista transacoes recorrentes ativas.",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["income", "expense"], "description": "Filtrar por tipo"},
            },
        },
    },
    {
        "name": "create_budget",
        "description": "Define um limite de orcamento mensal para uma categoria.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["Alimentacao", "Moradia", "Transporte", "Saude", "Lazer", "Educacao", "Salario", "Freelance", "Investimento", "Outros"],
                    "description": "Categoria do orcamento",
                },
                "monthly_limit": {"type": "number", "description": "Limite mensal em reais"},
            },
            "required": ["category", "monthly_limit"],
        },
    },
    {
        "name": "get_budget_status",
        "description": "Verifica o status dos orcamentos por categoria (quanto ja gastou vs limite).",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
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
    # --- Ferramentas adicionais ---
    {
        "name": "delete_investment",
        "description": "Remove um investimento. Use quando o usuario pedir para apagar ou remover um investimento.",
        "parameters": {
            "type": "object",
            "properties": {
                "investment_id": {"type": "string", "description": "ID do investimento a remover"},
            },
            "required": ["investment_id"],
        },
    },
    {
        "name": "list_investments",
        "description": "Lista todos os investimentos cadastrados.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "delete_debt",
        "description": "Remove uma divida do cadastro. Use quando o usuario pedir para apagar uma divida.",
        "parameters": {
            "type": "object",
            "properties": {
                "debt_id": {"type": "string", "description": "ID da divida a remover"},
            },
            "required": ["debt_id"],
        },
    },
    {
        "name": "delete_goal",
        "description": "Remove um objetivo/meta. Use quando o usuario pedir para apagar uma meta.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "string", "description": "ID do objetivo a remover"},
            },
            "required": ["goal_id"],
        },
    },
    {
        "name": "update_recurring",
        "description": "Atualiza uma transacao recorrente. Use para mudar valor, descricao, categoria, ativar/desativar, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "recurring_id": {"type": "string", "description": "ID da recorrente a atualizar"},
                "description": {"type": "string"},
                "amount": {"type": "number"},
                "type": {"type": "string", "enum": ["income", "expense"]},
                "category": {"type": "string"},
                "frequency": {"type": "string", "enum": ["monthly", "weekly", "yearly"]},
                "day_of_month": {"type": "integer"},
                "is_active": {"type": "boolean", "description": "true=ativa, false=desativada"},
                "use_business_day": {"type": "boolean"},
                "business_day_number": {"type": "integer"},
                "notes": {"type": "string"},
            },
            "required": ["recurring_id"],
        },
    },
    {
        "name": "delete_recurring",
        "description": "Remove uma transacao recorrente. Use quando o usuario pedir para apagar uma conta fixa.",
        "parameters": {
            "type": "object",
            "properties": {
                "recurring_id": {"type": "string", "description": "ID da recorrente a remover"},
            },
            "required": ["recurring_id"],
        },
    },
    {
        "name": "update_budget",
        "description": "Atualiza um orcamento existente. Use para mudar o limite mensal ou ativar/desativar.",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_id": {"type": "string", "description": "ID do orcamento a atualizar"},
                "category": {"type": "string"},
                "monthly_limit": {"type": "number"},
                "is_active": {"type": "boolean"},
            },
            "required": ["budget_id"],
        },
    },
    {
        "name": "delete_budget",
        "description": "Remove um orcamento. Use quando o usuario pedir para apagar um limite de orcamento.",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_id": {"type": "string", "description": "ID do orcamento a remover"},
            },
            "required": ["budget_id"],
        },
    },
    {
        "name": "list_budgets",
        "description": "Lista todos os orcamentos cadastrados com limites e status.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "update_plan",
        "description": "Atualiza um plano financeiro existente. Use para mudar status, observacoes ou conteudo.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "ID do plano a atualizar"},
                "title": {"type": "string"},
                "content": {"type": "object"},
                "status": {"type": "string", "enum": ["planejado", "em_andamento", "concluido"]},
                "observations": {"type": "string"},
            },
            "required": ["plan_id"],
        },
    },
    {
        "name": "generate_recurring",
        "description": "Gera transacoes pendentes a partir das contas recorrentes. Cria lancamentos para os proximos 3 meses. Seguro contra duplicatas.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name with the given arguments. Returns JSON string."""
    try:
        if name == "create_transaction":
            return _create_transaction(args)
        elif name == "update_transaction":
            return _update_transaction(args)
        elif name == "delete_transaction":
            return _delete_transaction(args)
        elif name == "list_transactions":
            return _list_transactions(args)
        elif name == "create_investment":
            return _create_investment(args)
        elif name == "update_investment":
            return _update_investment(args)
        elif name == "get_monthly_summary":
            return _get_monthly_summary(args)
        elif name == "get_alerts":
            return _get_alerts(args)
        elif name == "create_debt":
            return _create_debt(args)
        elif name == "update_debt":
            return _update_debt(args)
        elif name == "list_debts":
            return _list_debts(args)
        elif name == "create_goal":
            return _create_goal(args)
        elif name == "update_goal":
            return _update_goal(args)
        elif name == "list_goals":
            return _list_goals(args)
        elif name == "create_recurring":
            return _create_recurring(args)
        elif name == "list_recurring":
            return _list_recurring(args)
        elif name == "create_budget":
            return _create_budget(args)
        elif name == "get_budget_status":
            return _get_budget_status(args)
        elif name == "save_financial_plan":
            return _save_financial_plan(args)
        elif name == "get_plan_vs_actual":
            return _get_plan_vs_actual(args)
        elif name == "delete_investment":
            return _delete_investment(args)
        elif name == "list_investments":
            return _list_investments(args)
        elif name == "delete_debt":
            return _delete_debt(args)
        elif name == "delete_goal":
            return _delete_goal(args)
        elif name == "update_recurring":
            return _update_recurring(args)
        elif name == "delete_recurring":
            return _delete_recurring(args)
        elif name == "update_budget":
            return _update_budget(args)
        elif name == "delete_budget":
            return _delete_budget(args)
        elif name == "list_budgets":
            return _list_budgets(args)
        elif name == "update_plan":
            return _update_plan(args)
        elif name == "generate_recurring":
            return _generate_recurring(args)
        else:
            return json.dumps({"error": f"Tool desconhecida: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _create_transaction(args: dict) -> str:
    data = {
        "description": args["description"],
        "amount": args["amount"],
        "type": args["type"],
        "category": args["category"],
    }
    if "status" in args:
        data["status"] = args["status"]
    else:
        data["status"] = "pending"
    if "due_date" in args:
        data["due_date"] = args["due_date"]
    else:
        data["due_date"] = str(date.today())
    if "paid_date" in args:
        data["paid_date"] = args["paid_date"]
    if "notes" in args:
        data["notes"] = args["notes"]

    result = supabase.table("transactions").insert(data).execute()
    return json.dumps({"success": True, "transaction": result.data[0]}, default=str)


def _update_transaction(args: dict) -> str:
    tid = args.pop("transaction_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("transactions").update(args).eq("id", tid).execute()
    if not result.data:
        return json.dumps({"error": "Transacao nao encontrada"})
    return json.dumps({"success": True, "transaction": result.data[0]}, default=str)


def _delete_transaction(args: dict) -> str:
    tid = args["transaction_id"]
    result = supabase.table("transactions").delete().eq("id", tid).execute()
    if not result.data:
        return json.dumps({"error": "Transacao nao encontrada"})
    return json.dumps({"success": True, "message": "Transacao removida"})


def _list_transactions(args: dict) -> str:
    query = supabase.table("transactions").select("*")
    if "type" in args:
        query = query.eq("type", args["type"])
    if "category" in args:
        query = query.eq("category", args["category"])
    if "status" in args:
        query = query.eq("status", args["status"])
    if "month" in args and "year" in args:
        m, y = args["month"], args["year"]
        start = f"{y}-{m:02d}-01"
        end_month = m + 1 if m < 12 else 1
        end_year = y if m < 12 else y + 1
        end = f"{end_year}-{end_month:02d}-01"
        query = query.gte("due_date", start).lt("due_date", end)
    result = query.order("due_date", desc=True).limit(50).execute()
    return json.dumps({"transactions": result.data}, default=str)


def _create_investment(args: dict) -> str:
    data = {
        "name": args["name"],
        "type": args["type"],
        "institution": args["institution"],
        "invested_amount": args["invested_amount"],
        "current_amount": args["current_amount"],
        "start_date": args["start_date"],
    }
    if "maturity_date" in args:
        data["maturity_date"] = args["maturity_date"]
    if "notes" in args:
        data["notes"] = args["notes"]

    result = supabase.table("investments").insert(data).execute()
    return json.dumps({"success": True, "investment": result.data[0]}, default=str)


def _update_investment(args: dict) -> str:
    iid = args.pop("investment_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("investments").update(args).eq("id", iid).execute()
    if not result.data:
        return json.dumps({"error": "Investimento nao encontrado"})
    return json.dumps({"success": True, "investment": result.data[0]}, default=str)


def _get_monthly_summary(args: dict) -> str:
    today = date.today()
    m = args.get("month", today.month)
    y = args.get("year", today.year)
    start = f"{y}-{m:02d}-01"
    end_month = m + 1 if m < 12 else 1
    end_year = y if m < 12 else y + 1
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

    return json.dumps({
        "month": m,
        "year": y,
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "by_category": by_category,
    }, default=str)


def _get_alerts(_args: dict) -> str:
    alerts = get_active_alerts()
    return json.dumps({"alerts": alerts}, default=str)


def _create_debt(args: dict) -> str:
    data = {
        "creditor": args["creditor"],
        "original_amount": args["original_amount"],
        "current_amount": args["current_amount"],
        "category": args["category"],
        "origin_date": args["origin_date"],
    }
    if "status" in args:
        data["status"] = args["status"]
    if "is_paying" in args:
        data["is_paying"] = args["is_paying"]
    if "monthly_payment" in args:
        data["monthly_payment"] = args["monthly_payment"]
    if "notes" in args:
        data["notes"] = args["notes"]

    result = supabase.table("debts").insert(data).execute()
    return json.dumps({"success": True, "debt": result.data[0]}, default=str)


def _update_debt(args: dict) -> str:
    did = args.pop("debt_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("debts").update(args).eq("id", did).execute()
    if not result.data:
        return json.dumps({"error": "Divida nao encontrada"})
    return json.dumps({"success": True, "debt": result.data[0]}, default=str)


def _list_debts(args: dict) -> str:
    query = supabase.table("debts").select("*")
    if "status" in args:
        query = query.eq("status", args["status"])
    if "category" in args:
        query = query.eq("category", args["category"])
    result = query.order("created_at", desc=True).execute()
    return json.dumps({"debts": result.data}, default=str)


def _create_goal(args: dict) -> str:
    data = {
        "name": args["name"],
        "target_amount": args["target_amount"],
        "category": args["category"],
    }
    if "saved_amount" in args:
        data["saved_amount"] = args["saved_amount"]
    if "priority" in args:
        data["priority"] = args["priority"]
    if "target_date" in args:
        data["target_date"] = args["target_date"]
    if "notes" in args:
        data["notes"] = args["notes"]

    result = supabase.table("goals").insert(data).execute()
    return json.dumps({"success": True, "goal": result.data[0]}, default=str)


def _update_goal(args: dict) -> str:
    gid = args.pop("goal_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("goals").update(args).eq("id", gid).execute()
    if not result.data:
        return json.dumps({"error": "Objetivo nao encontrado"})
    return json.dumps({"success": True, "goal": result.data[0]}, default=str)


def _list_goals(args: dict) -> str:
    query = supabase.table("goals").select("*")
    if "status" in args:
        query = query.eq("status", args["status"])
    if "priority" in args:
        query = query.eq("priority", args["priority"])
    result = query.order("created_at", desc=True).execute()
    return json.dumps({"goals": result.data}, default=str)


def _create_recurring(args: dict) -> str:
    data = {
        "description": args["description"],
        "amount": args["amount"],
        "type": args["type"],
        "category": args["category"],
    }
    if "frequency" in args:
        data["frequency"] = args["frequency"]
    if "day_of_month" in args:
        data["day_of_month"] = args["day_of_month"]
    if "notes" in args:
        data["notes"] = args["notes"]
    if "use_business_day" in args:
        data["use_business_day"] = args["use_business_day"]
    if "business_day_number" in args:
        data["business_day_number"] = args["business_day_number"]

    # Auto-calculate next_due_date for business day mode
    if data.get("use_business_day") and data.get("business_day_number"):
        from routes.recurring import get_nth_business_day

        today = date.today()
        bd = get_nth_business_day(today.year, today.month, data["business_day_number"])
        if bd <= today:
            next_m = today.month + 1 if today.month < 12 else 1
            next_y = today.year if today.month < 12 else today.year + 1
            bd = get_nth_business_day(next_y, next_m, data["business_day_number"])
        data["next_due_date"] = str(bd)
    elif "next_due_date" in args:
        data["next_due_date"] = args["next_due_date"]
    else:
        data["next_due_date"] = str(date.today())

    result = supabase.table("recurring_transactions").insert(data).execute()
    return json.dumps({"success": True, "recurring": result.data[0]}, default=str)


def _list_recurring(args: dict) -> str:
    query = supabase.table("recurring_transactions").select("*").eq("is_active", True)
    if "type" in args:
        query = query.eq("type", args["type"])
    result = query.order("next_due_date").execute()
    return json.dumps({"recurring": result.data}, default=str)


def _create_budget(args: dict) -> str:
    data = {
        "category": args["category"],
        "monthly_limit": args["monthly_limit"],
    }
    result = supabase.table("budgets").insert(data).execute()
    return json.dumps({"success": True, "budget": result.data[0]}, default=str)


def _save_financial_plan(args: dict) -> str:
    month = args["month"]
    year = args["year"]
    title = args["title"]
    content = args["content"]
    status = args.get("status", "planejado")

    existing = (
        supabase.table("financial_plans")
        .select("id")
        .eq("month", month)
        .eq("year", year)
        .execute()
    ).data

    if existing:
        result = (
            supabase.table("financial_plans")
            .update({"title": title, "content": content, "status": status})
            .eq("id", existing[0]["id"])
            .execute()
        )
        return json.dumps({"success": True, "action": "updated", "plan": result.data[0]}, default=str)
    else:
        result = (
            supabase.table("financial_plans")
            .insert({"month": month, "year": year, "title": title, "content": content, "status": status})
            .execute()
        )
        return json.dumps({"success": True, "action": "created", "plan": result.data[0]}, default=str)


def _get_plan_vs_actual(args: dict) -> str:
    month = args["month"]
    year = args["year"]

    plan_data = (
        supabase.table("financial_plans")
        .select("*")
        .eq("month", month)
        .eq("year", year)
        .execute()
    ).data
    plan = plan_data[0] if plan_data else None

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


def _get_budget_status(_args: dict) -> str:
    today = date.today()
    m, y = today.month, today.year
    start = f"{y}-{m:02d}-01"
    end_month = m + 1 if m < 12 else 1
    end_year = y if m < 12 else y + 1
    end = f"{end_year}-{end_month:02d}-01"

    budgets = supabase.table("budgets").select("*").eq("is_active", True).execute().data
    txns = (
        supabase.table("transactions")
        .select("category, amount")
        .eq("type", "expense")
        .gte("due_date", start)
        .lt("due_date", end)
        .execute()
    ).data

    spent_by_cat: dict[str, float] = {}
    for t in txns:
        cat = t["category"]
        spent_by_cat[cat] = spent_by_cat.get(cat, 0) + t["amount"]

    status_list = []
    for b in budgets:
        spent = spent_by_cat.get(b["category"], 0)
        limit_val = b["monthly_limit"]
        remaining = limit_val - spent
        pct = (spent / limit_val * 100) if limit_val > 0 else 0
        status_list.append({
            "category": b["category"],
            "limit": limit_val,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": round(pct, 1),
        })

    return json.dumps({"budgets": status_list}, default=str)


def _delete_investment(args: dict) -> str:
    iid = args["investment_id"]
    result = supabase.table("investments").delete().eq("id", iid).execute()
    if not result.data:
        return json.dumps({"error": "Investimento nao encontrado"})
    return json.dumps({"success": True, "message": "Investimento removido"})


def _list_investments(_args: dict) -> str:
    result = supabase.table("investments").select("*").order("created_at", desc=True).execute()
    return json.dumps({"investments": result.data}, default=str)


def _delete_debt(args: dict) -> str:
    did = args["debt_id"]
    result = supabase.table("debts").delete().eq("id", did).execute()
    if not result.data:
        return json.dumps({"error": "Divida nao encontrada"})
    return json.dumps({"success": True, "message": "Divida removida"})


def _delete_goal(args: dict) -> str:
    gid = args["goal_id"]
    result = supabase.table("goals").delete().eq("id", gid).execute()
    if not result.data:
        return json.dumps({"error": "Objetivo nao encontrado"})
    return json.dumps({"success": True, "message": "Objetivo removido"})


def _update_recurring(args: dict) -> str:
    rid = args.pop("recurring_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("recurring_transactions").update(args).eq("id", rid).execute()
    if not result.data:
        return json.dumps({"error": "Recorrente nao encontrada"})
    return json.dumps({"success": True, "recurring": result.data[0]}, default=str)


def _delete_recurring(args: dict) -> str:
    rid = args["recurring_id"]
    result = supabase.table("recurring_transactions").delete().eq("id", rid).execute()
    if not result.data:
        return json.dumps({"error": "Recorrente nao encontrada"})
    return json.dumps({"success": True, "message": "Recorrente removida"})


def _update_budget(args: dict) -> str:
    bid = args.pop("budget_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("budgets").update(args).eq("id", bid).execute()
    if not result.data:
        return json.dumps({"error": "Orcamento nao encontrado"})
    return json.dumps({"success": True, "budget": result.data[0]}, default=str)


def _delete_budget(args: dict) -> str:
    bid = args["budget_id"]
    result = supabase.table("budgets").delete().eq("id", bid).execute()
    if not result.data:
        return json.dumps({"error": "Orcamento nao encontrado"})
    return json.dumps({"success": True, "message": "Orcamento removido"})


def _list_budgets(_args: dict) -> str:
    result = supabase.table("budgets").select("*").order("created_at", desc=True).execute()
    return json.dumps({"budgets": result.data}, default=str)


def _update_plan(args: dict) -> str:
    pid = args.pop("plan_id")
    if not args:
        return json.dumps({"error": "Nenhum campo para atualizar"})
    result = supabase.table("financial_plans").update(args).eq("id", pid).execute()
    if not result.data:
        return json.dumps({"error": "Plano nao encontrado"})
    return json.dumps({"success": True, "plan": result.data[0]}, default=str)


def _generate_recurring(_args: dict) -> str:
    import httpx
    try:
        resp = httpx.post("http://localhost:8000/api/recurring/generate", timeout=30)
        return resp.text
    except Exception as e:
        return json.dumps({"error": f"Erro ao gerar recorrentes: {str(e)}"})
