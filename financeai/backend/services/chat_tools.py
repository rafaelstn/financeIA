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
