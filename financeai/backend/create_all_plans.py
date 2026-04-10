"""Planejamento completo Mai-Dez 2026 — Carro sai esse ano!"""
from database import supabase

def upsert_plan(month, year, title, status, observations, sections):
    content = {"sections": sections}
    existing = supabase.table("financial_plans").select("id").eq("month", month).eq("year", year).execute().data
    if existing:
        supabase.table("financial_plans").update({
            "title": title, "status": status, "observations": observations, "content": content,
        }).eq("id", existing[0]["id"]).execute()
        print(f"  Atualizado: {title}")
    else:
        supabase.table("financial_plans").insert({
            "month": month, "year": year, "title": title, "status": status,
            "observations": observations, "content": content,
        }).execute()
        print(f"  Criado: {title}")

# Custo de vida base
cv = [
    {"description": "Aluguel", "amount": 1200.0, "notes": "Vence dia 5"},
    {"description": "Faculdade", "amount": 1305.0, "notes": "Pagar no prazo (atraso = R$ 1.570)"},
    {"description": "Mercado", "amount": 2000.0, "notes": ""},
    {"description": "Baba", "amount": 1000.0, "notes": ""},
    {"description": "Dizimo", "amount": 1810.0, "notes": "10% da renda"},
    {"description": "Primicia", "amount": 603.0, "notes": "1/30 da renda"},
    {"description": "Luz", "amount": 190.0, "notes": ""},
    {"description": "Gas", "amount": 130.0, "notes": ""},
    {"description": "Internet", "amount": 130.0, "notes": ""},
    {"description": "Parcelamento DAS", "amount": 100.0, "notes": "Dia 20"},
    {"description": "DAS MEI Mensal", "amount": 86.0, "notes": "Ate 10o dia util"},
    {"description": "Agua", "amount": 80.0, "notes": ""},
    {"description": "Celular Rafael", "amount": 75.0, "notes": ""},
    {"description": "PlayStation", "amount": 65.0, "notes": "Wagner paga metade R$ 30"},
    {"description": "Celular Paula", "amount": 62.0, "notes": ""},
]
cv_total = sum(i["amount"] for i in cv)

# ============================================================
# MAIO — Limpeza (mes apertado com cartao)
# ============================================================
upsert_plan(5, 2026,
    "Maio — Limpeza Geral",
    "planejado",
    "O mes mais pesado. Cartao de R$ 5k + atrasados + 2 dividas menores. "
    "Vai ser apertado mas necessario. Pense assim: voce ta tirando todo o lixo financeiro de uma vez. "
    "A partir de Junho, a estrada fica limpa pra correr.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Limpar o Passado", "total": 8282.0, "items": [
            {"description": "Fatura Cartao Rogerio", "amount": 5000.0, "notes": "PRIORIDADE MAXIMA. Rotativo = 15%/mes de juros!"},
            {"description": "Faculdade Abril atrasada", "amount": 1507.0, "notes": "Multa inclusa"},
            {"description": "IR Paula + Rafael", "amount": 588.0, "notes": "Vence 29/05"},
            {"description": "DAS atrasados Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Parcelamento DAS Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Recovery — QUITAR", "amount": 253.0, "notes": "Primeira vitoria! Negocie desconto."},
            {"description": "Mercado Pago — QUITAR", "amount": 334.0, "notes": "Segunda vitoria!"},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 500.0, "notes": "Mes apertado. O importante e comecar."},
        ]},
        {"category": "sobra", "title": "Sobra Livre", "total": 1981.0, "items": [
            {"description": "Gastos pessoais", "amount": 1981.0, "notes": "Apertado mas temporario. Proximo mes alivia."},
        ]},
    ]
)

# ============================================================
# JUNHO — Ataque + Carro comeca
# ============================================================
upsert_plan(6, 2026,
    "Junho — Ataque + Carro Comeca",
    "planejado",
    "Passado limpo! Agora o jogo muda: quitar Estacio e Vivo E comecar o fundo do carro. "
    "O carro e prioridade — vamos ser agressivos. R$ 5.746 pro carro este mes. "
    "Em Outubro voce ja tem os R$ 25k. Acredita.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Bola de Neve", "total": 1517.0, "items": [
            {"description": "Estacio — QUITAR", "amount": 708.0, "notes": "Negocie no Serasa! Desconto de 50% e comum."},
            {"description": "Vivo — QUITAR", "amount": 809.0, "notes": "App da Vivo ou Serasa. Sempre negocie."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 2.000. Reduzida pra priorizar o carro."},
        ]},
        {"category": "sobra", "title": "Carro + Pessoal", "total": 7746.0, "items": [
            {"description": "Fundo Primeiro Carro", "amount": 5746.0, "notes": "INICIO! Acumulado: R$ 5.746. Meta: R$ 25.000 ate Outubro."},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": "Fixo por mes. Lazer, imprevistos, vida."},
        ]},
    ]
)

# ============================================================
# JULHO — Mais duas + CNH + Carro
# ============================================================
upsert_plan(7, 2026,
    "Julho — CNH + Mais Duas Caem",
    "planejado",
    "Mes forte: Ipanema e Nubank quitados, CNH paga, carro passando de R$ 11k. "
    "6 dividas eliminadas de 9. Voce ja cruzou a metade. "
    "A CNH e o primeiro passo pro carro — tudo conectado.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Continuacao", "total": 2803.0, "items": [
            {"description": "Ipanema (858) — QUITAR", "amount": 858.0, "notes": "Divida antiga = desconto bom. Negocie."},
            {"description": "Nubank — QUITAR", "amount": 945.0, "notes": "Use o app. Nubank costuma dar boas condicoes."},
            {"description": "CNH — Carteira de Motorista", "amount": 1000.0, "notes": "Prioridade alta. Precisa pra dirigir o carro!"},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 3.500"},
        ]},
        {"category": "sobra", "title": "Carro + Pessoal", "total": 6460.0, "items": [
            {"description": "Fundo Primeiro Carro", "amount": 4460.0, "notes": "Acumulado: R$ 10.206. Quase metade!"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# AGOSTO — SportAcao + Carro
# ============================================================
upsert_plan(8, 2026,
    "Agosto — SportAcao Cai",
    "planejado",
    "7 de 9 dividas eliminadas. So sobra a Ipanema grande. "
    "O carro ja passou de R$ 15k — mais da metade. "
    "Voce ta no ritmo. Nao para agora.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — SportAcao", "total": 2000.0, "items": [
            {"description": "SportAcao — QUITAR", "amount": 2000.0, "notes": "Negocie! R$ 2k pode virar R$ 1.200 com desconto."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 5.000. Quase 1 mes de custo de vida."},
        ]},
        {"category": "sobra", "title": "Carro + Pessoal", "total": 7263.0, "items": [
            {"description": "Fundo Primeiro Carro", "amount": 5263.0, "notes": "Acumulado: R$ 15.469. Passando da metade!"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# SETEMBRO — Chefao + Carro acelerando
# ============================================================
upsert_plan(9, 2026,
    "Setembro — Negociando o Chefao",
    "planejado",
    "Ultima divida grande: Ipanema R$ 5.645. Estrategia: negociar FORTE no Serasa. "
    "Dividas antigas costumam ter desconto de 60-80%. Tente pagar R$ 2.000-3.000 total. "
    "Se conseguir desconto bom, quita tudo neste mes! O carro passa de R$ 20k.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — O Chefao", "total": 3000.0, "items": [
            {"description": "Ipanema (grande) — Parcial/Total", "amount": 3000.0, "notes": "NEGOCIE! Valor R$ 5.645 mas desconto pode chegar a R$ 2k. Ligue pro Serasa."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 6.500"},
        ]},
        {"category": "sobra", "title": "Carro + Pessoal", "total": 6263.0, "items": [
            {"description": "Fundo Primeiro Carro", "amount": 4263.0, "notes": "Acumulado: R$ 19.732. QUASE LA!"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# OUTUBRO — Ultima divida + CARRO!
# ============================================================
upsert_plan(10, 2026,
    "Outubro — Carro + Ultima Divida!",
    "planejado",
    "O MES DO CARRO! Com R$ 25k+ acumulados, voce compra seu primeiro carro. "
    "E a Ipanema grande e quitada de vez (se nao quitou em Setembro). "
    "Dois marcos no mesmo mes: livre de dividas + carro proprio. "
    "Lembra quando parecia impossivel? Foram 5 meses de disciplina.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Final!", "total": 2645.0, "items": [
            {"description": "Ipanema (grande) — QUITAR RESTO", "amount": 2645.0, "notes": "Se negociou desconto em Set, pode ser menos ou zero!"},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 8.000. Mais de 1 mes de seguranca."},
        ]},
        {"category": "sobra", "title": "CARRO! + Pessoal", "total": 6618.0, "items": [
            {"description": "Fundo Primeiro Carro — COMPRAR!", "amount": 4618.0, "notes": "Acumulado: R$ 24.350+. E HORA DE COMPRAR! Pesquise, negocie, leve um mecanico."},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": "Comemore. Voce merece."},
        ]},
    ]
)

# ============================================================
# NOVEMBRO — Livre + Investir
# ============================================================
upsert_plan(11, 2026,
    "Novembro — Vida Nova",
    "planejado",
    "Primeiro mes da nova era. Sem dividas. Com carro. Com reserva. "
    "Agora o dinheiro que ia pra dividas vai pra VOCE: investimentos, reserva, objetivos. "
    "Em Janeiro voce tinha R$ 12.500 em dividas. Em 6 meses zerou tudo e comprou um carro. "
    "Isso e transformacao real.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 2500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 2500.0, "notes": "Acumulado: R$ 10.500. Agora acelera sem dividas atrapalhando."},
        ]},
        {"category": "sobra", "title": "Investimentos + Pessoal", "total": 8263.0, "items": [
            {"description": "Investimento — Tesouro Selic", "amount": 3000.0, "notes": "Comece simples. Seu dinheiro trabalhando pra voce."},
            {"description": "Seguro + manutencao carro", "amount": 500.0, "notes": "Reserva mensal pra custos do carro"},
            {"description": "Gastos pessoais e lazer", "amount": 4763.0, "notes": "Voce conquistou. Curta sem culpa."},
        ]},
    ]
)

# ============================================================
# DEZEMBRO — Consolidacao + 13o
# ============================================================
upsert_plan(12, 2026,
    "Dezembro — Consolidacao + 13o",
    "planejado",
    "Ultimo mes do ano da transformacao. Com o 13o voce pode turbinar a reserva ou investir mais. "
    "Olha pra tras: R$ 12.500 em dividas -> R$ 0. Zero de reserva -> R$ 13.000. Sem carro -> com carro. "
    "2027 comeca DIFERENTE. Voce tem controle. Voce tem plano. Voce tem disciplina. "
    "A jornada continua — mas agora voce ta no volante (literalmente).",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 2500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 2500.0, "notes": "Acumulado: R$ 13.000. Quase 2 meses de seguranca."},
        ]},
        {"category": "sobra", "title": "Investimentos + 13o + Pessoal", "total": 8263.0, "items": [
            {"description": "Investimento", "amount": 3000.0, "notes": "Diversifique: Tesouro Selic + CDB. Estude FIIs pro ano que vem."},
            {"description": "Seguro + manutencao carro", "amount": 500.0, "notes": ""},
            {"description": "Festas e familia", "amount": 4763.0, "notes": "Final de ano. Voce trabalhou duro. Curta."},
        ]},
    ]
)

print()
print("=" * 60)
print("JORNADA 2026 — CARRO SAI EM OUTUBRO!")
print("=" * 60)
print()
print("DIVIDAS (bola de neve):")
print("  Mai: Recovery + M.Pago + cartao + atrasados  -> 2 quitadas")
print("  Jun: Estacio + Vivo                          -> 4 quitadas")
print("  Jul: Ipanema + Nubank + CNH                  -> 6 quitadas")
print("  Ago: SportAcao                               -> 7 quitadas")
print("  Set: Ipanema grande (parcial)                 -> negociando")
print("  Out: Ipanema grande (quitar)                  -> 8 quitadas = LIVRE!")
print()
print("CARRO (R$ 25.000):")
print("  Jun: R$ 5.746  | Jul: R$ 10.206 | Ago: R$ 15.469")
print("  Set: R$ 19.732 | Out: R$ 24.350+ = COMPRA!")
print()
print("RESERVA:")
print("  R$ 500 > 2.000 > 3.500 > 5.000 > 6.500 > 8.000 > 10.500 > 13.000")
print()
print("RESULTADO FINAL (Dez/2026):")
print("  Dividas: R$ 0 (era R$ 12.552)")
print("  Reserva: R$ 13.000")
print("  Carro: COMPRADO")
print("  CNH: PAGA")
print("  Investimentos: R$ 6.000+")
