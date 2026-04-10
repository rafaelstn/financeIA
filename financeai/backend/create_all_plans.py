"""Planejamento DEFINITIVO Mai-Dez 2026"""
from database import supabase

def upsert_plan(month, year, title, status, observations, sections):
    content = {"sections": sections}
    existing = supabase.table("financial_plans").select("id").eq("month", month).eq("year", year).execute().data
    if existing:
        supabase.table("financial_plans").update({
            "title": title, "status": status, "observations": observations, "content": content,
        }).eq("id", existing[0]["id"]).execute()
        print(f"  {title}")
    else:
        supabase.table("financial_plans").insert({
            "month": month, "year": year, "title": title, "status": status,
            "observations": observations, "content": content,
        }).execute()
        print(f"  {title}")

# Custo de vida base (todo mes)
cv = [
    {"description": "Mercado", "amount": 2000.0, "notes": ""},
    {"description": "Dizimo", "amount": 1810.0, "notes": "10% da renda"},
    {"description": "Faculdade", "amount": 1305.0, "notes": "Pagar no prazo"},
    {"description": "Aluguel", "amount": 1200.0, "notes": ""},
    {"description": "Baba", "amount": 1000.0, "notes": ""},
    {"description": "Primicia", "amount": 603.0, "notes": "1/30 da renda"},
    {"description": "Luz", "amount": 190.0, "notes": ""},
    {"description": "Gas", "amount": 130.0, "notes": ""},
    {"description": "Internet", "amount": 130.0, "notes": ""},
    {"description": "Parcelamento DAS", "amount": 100.0, "notes": ""},
    {"description": "DAS MEI Mensal", "amount": 86.0, "notes": ""},
    {"description": "Agua", "amount": 80.0, "notes": ""},
    {"description": "Celular Rafael", "amount": 75.0, "notes": ""},
    {"description": "Crefito Vigente Paula", "amount": 72.0, "notes": "Parcela mensal"},
    {"description": "PlayStation", "amount": 65.0, "notes": ""},
    {"description": "Celular Paula", "amount": 62.0, "notes": ""},
]
cv_total = 7408.0

# ============================================================
# MAIO — Limpeza Total (mes mais pesado)
# Disponivel: R$ 10.691 | Compromissos: R$ 10.369
# ============================================================
upsert_plan(5, 2026,
    "Maio — Limpeza Total",
    "planejado",
    "O mes mais pesado do ano. Cartao de R$ 5k, atrasados, e quitar as 6 menores dividas (suas + Paula). "
    "Vai ser apertado, mas depois desse mes voce nunca mais olha pra tras. "
    "As dividas da Paula que sao pequenas (Claro, Estacio, Nubank Cartao) caem TODAS agora. "
    "Sao R$ 580 que somem de vez. Primeira vitoria do casal.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Limpeza Geral", "total": 10369.0, "items": [
            {"description": "Fatura Cartao Rogerio", "amount": 5000.0, "notes": "PRIORIDADE. Rotativo = 15%/mes!"},
            {"description": "Faculdade Abril atrasada", "amount": 1507.0, "notes": "Com multa"},
            {"description": "IR Paula + Rafael", "amount": 588.0, "notes": "Vence 29/05"},
            {"description": "DAS atrasados Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Parcelamento DAS Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Mercado Pago — QUITAR", "amount": 334.0, "notes": "Negocie desconto!"},
            {"description": "Recovery — QUITAR", "amount": 253.0, "notes": "Negocie desconto!"},
            {"description": "Nubank Cartao Paula — QUITAR", "amount": 260.0, "notes": "Menor da Paula"},
            {"description": "Estacio Paula — QUITAR", "amount": 92.0, "notes": "R$ 92 some de vez"},
            {"description": "Claro 80 Paula — QUITAR", "amount": 80.0, "notes": ""},
            {"description": "Claro 68 Paula — QUITAR", "amount": 68.0, "notes": ""},
            {"description": "Crefito Paula — QUITAR", "amount": 380.0, "notes": "Negocie desconto"},
            {"description": "Marisa Recovery Paula — QUITAR", "amount": 460.0, "notes": "Negocie desconto"},
            {"description": "Nubank Emp Paula — QUITAR", "amount": 663.0, "notes": "Negocie desconto"},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 300.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 300.0, "notes": "Mes apertadissimo. Comeca com o que da."},
        ]},
        {"category": "sobra", "title": "Sobra Livre", "total": 622.0, "items": [
            {"description": "Pessoal + imprevistos", "amount": 622.0, "notes": "Apertado. Mas em Junho explode a sobra. Aguenta firme."},
        ]},
    ]
)

# ============================================================
# JUNHO — Ataque Rafael + Carro + Congresso comeca
# Disponivel: R$ 10.691
# ============================================================
upsert_plan(6, 2026,
    "Junho — Ataque + Carro + Congresso",
    "planejado",
    "Dividas da Paula ZERADAS no mes passado! Agora foco no Rafael. "
    "Estacio e Vivo caem. E comeca os 3 fundos: Carro, Congresso e Tratamento Paula. "
    "O carro precisa de R$ 25k ate Outubro. O congresso precisa de R$ 6k ate Novembro. "
    "O tratamento nao tem data mas e urgente. Vamos atacar os 3 ao mesmo tempo.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Bola de Neve Rafael", "total": 1517.0, "items": [
            {"description": "Estacio Rafael — QUITAR", "amount": 708.0, "notes": "Negocie no Serasa! 50% desconto e real."},
            {"description": "Vivo — QUITAR", "amount": 809.0, "notes": "Serasa ou app Vivo. Desconto sempre tem."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 1.800"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 7674.0, "items": [
            {"description": "Fundo Carro", "amount": 3674.0, "notes": "INICIO! Acumulado: R$ 3.674. Meta R$ 25k ate Out."},
            {"description": "Fundo Congresso Espada", "amount": 1000.0, "notes": "Inicio! Acumulado: R$ 1.000. Meta R$ 6k ate Nov."},
            {"description": "Tratamento Paula", "amount": 1000.0, "notes": "Inicio! Acumulado: R$ 1.000. Meta R$ 3.500."},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# JULHO — CNH + mais duas + fundos crescem
# ============================================================
upsert_plan(7, 2026,
    "Julho — CNH + Mais Duas Caem",
    "planejado",
    "Ipanema e Nubank Rafael caem. CNH paga — precisa pra dirigir o carro! "
    "Ja sao 10+ dividas quitadas (suas + Paula). Mais da metade. "
    "Carro passando de R$ 7k, congresso em R$ 2k, tratamento em R$ 2k. "
    "Tudo caminhando junto.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas + CNH", "total": 2803.0, "items": [
            {"description": "Ipanema (858) — QUITAR", "amount": 858.0, "notes": "Negocie!"},
            {"description": "Nubank Rafael — QUITAR", "amount": 945.0, "notes": "Use o app."},
            {"description": "CNH — Carteira de Motorista", "amount": 1000.0, "notes": "Prioridade! Precisa pra dirigir o carro."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 3.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6388.0, "items": [
            {"description": "Fundo Carro", "amount": 2888.0, "notes": "Acumulado: R$ 6.562"},
            {"description": "Fundo Congresso Espada", "amount": 1000.0, "notes": "Acumulado: R$ 2.000"},
            {"description": "Tratamento Paula", "amount": 500.0, "notes": "Acumulado: R$ 1.500"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# AGOSTO — SportAcao + Bradesco Paula + fundos aceleram
# ============================================================
upsert_plan(8, 2026,
    "Agosto — SportAcao + Bradesco Paula",
    "planejado",
    "Duas dividas grandes caem: SportAcao R$ 2k e Bradesco Paula R$ 1.710. "
    "Depois desse mes so sobra UMA divida: Ipanema grande de R$ 5.645. "
    "Tratamento Paula pode ja ser iniciado se o acumulado chegar em R$ 3.5k. "
    "Carro passando de R$ 11k. Congresso em R$ 3k.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — As Grandes", "total": 3710.0, "items": [
            {"description": "SportAcao — QUITAR", "amount": 2000.0, "notes": "Negocie! Pode baixar pra R$ 1.200."},
            {"description": "Bradesco Paula — QUITAR", "amount": 1710.0, "notes": "Maior divida da Paula. Negocie forte!"},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 4.800"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 4981.0, "items": [
            {"description": "Fundo Carro", "amount": 1481.0, "notes": "Acumulado: R$ 8.043. Mes apertado com 2 dividas grandes."},
            {"description": "Fundo Congresso Espada", "amount": 1000.0, "notes": "Acumulado: R$ 3.000. Metade!"},
            {"description": "Tratamento Paula", "amount": 500.0, "notes": "Acumulado: R$ 2.000"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# SETEMBRO — Chefao Ipanema + fundos aceleram
# ============================================================
upsert_plan(9, 2026,
    "Setembro — O Chefao Final",
    "planejado",
    "Ultima divida: Ipanema R$ 5.645. Negocie FORTE — desconto de 60-80% e possivel. "
    "Se conseguir pagar R$ 2.500-3.000, sobra MUITO mais pros objetivos. "
    "Tratamento Paula deve estar completo. Congresso passando de R$ 4k.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Chefao Final", "total": 3000.0, "items": [
            {"description": "Ipanema grande — NEGOCIAR E QUITAR", "amount": 3000.0, "notes": "Valor original R$ 5.645. NEGOCIE! Divida antiga = desconto de 50-80%. Tente R$ 2.000-3.000."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 6.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6191.0, "items": [
            {"description": "Fundo Carro", "amount": 2191.0, "notes": "Acumulado: R$ 10.234"},
            {"description": "Fundo Congresso Espada", "amount": 1000.0, "notes": "Acumulado: R$ 4.000"},
            {"description": "Tratamento Paula", "amount": 1000.0, "notes": "Acumulado: R$ 3.000. Quase la!"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# OUTUBRO — Ipanema resto + Carro acelera + Tratamento completo
# ============================================================
upsert_plan(10, 2026,
    "Outubro — Livre de Dividas!",
    "planejado",
    "Se restou algo da Ipanema, quita aqui. TODAS AS DIVIDAS QUITADAS! "
    "Agora todo o dinheiro de dividas vai pro carro. "
    "Tratamento Paula completo. Congresso passando de R$ 5k. "
    "O carro e a meta — tudo que sobrar vai pra ele.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Resto Ipanema (se houver)", "total": 2645.0, "items": [
            {"description": "Ipanema grande — RESTO", "amount": 2645.0, "notes": "Se negociou desconto em Set, pode ser zero! Se nao, quita o resto."},
        ]},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 7.800"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6546.0, "items": [
            {"description": "Fundo Carro", "amount": 3046.0, "notes": "Acumulado: R$ 13.280. Apertou mas ta crescendo!"},
            {"description": "Fundo Congresso Espada", "amount": 1000.0, "notes": "Acumulado: R$ 5.000"},
            {"description": "Tratamento Paula — COMPLETAR", "amount": 500.0, "notes": "Acumulado: R$ 3.500. META BATIDA!"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ]
)

# ============================================================
# NOVEMBRO — Congresso + Carro COMPRA! + Viagem comeca
# ============================================================
upsert_plan(11, 2026,
    "Novembro — Congresso + Carro!",
    "planejado",
    "MES HISTORICO. Congresso Espada na Fase PAGO (deadline dia 20). "
    "E com o acumulado do carro chegando perto de R$ 20k+, pode ser hora de comprar! "
    "Se esperar Dezembro com o 13o, chega em R$ 25k tranquilo. "
    "Sem dividas, sem parcelamentos. Tudo seu. "
    "Viagem: comeca a pesquisar destinos e precos.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 9.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 9191.0, "items": [
            {"description": "Fundo Carro", "amount": 4191.0, "notes": "Acumulado: R$ 17.471. Se comprar em Dez com 13o = R$ 25k+!"},
            {"description": "Congresso Espada na Fase — PAGAR", "amount": 1000.0, "notes": "Acumulado: R$ 6.000. META BATIDA! Deadline 20/Nov."},
            {"description": "Fundo Viagem", "amount": 1000.0, "notes": "Inicio! Pesquise destinos e datas."},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": "Sem dividas. Respira."},
            {"description": "Investimento", "amount": 1000.0, "notes": "Comece! Tesouro Selic ou CDB 100% CDI."},
        ]},
    ]
)

# ============================================================
# DEZEMBRO — Carro COMPRA + 13o + TV + Viagem
# ============================================================
upsert_plan(12, 2026,
    "Dezembro — O Carro Chega!",
    "planejado",
    "COM O 13o SALARIO, o carro bate os R$ 25k. COMPRA! "
    "O 13o do Rafael (~R$ 12k) + Paula (~R$ 2.800) = R$ 14.800 extras. "
    "Isso abre espaco pra TV OLED e viagem comecar a sair. "
    "Olha a jornada: R$ 16.842 em dividas, 0 de reserva, 0 de patrimonio. "
    "Agora: R$ 0 divida, R$ 11k reserva, carro, CNH, congresso pago, "
    "tratamento feito, e investimentos comecando. "
    "VOCE E OUTRA PESSOA. 2027 comeca no volante.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "reserva", "title": "Reserva de Emergencia", "total": 1500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1500.0, "notes": "Acumulado: R$ 10.800. Quase 1.5 mes de seguranca."},
        ]},
        {"category": "sobra", "title": "Carro + Viagem + TV + 13o", "total": 9191.0, "items": [
            {"description": "Carro — COMPRAR!", "amount": 4191.0, "notes": "Acumulado: R$ 21.662 + 13o = R$ 25k+. E HORA!"},
            {"description": "TV OLED Samsung", "amount": 2000.0, "notes": "Comeca! Com 13o pode completar. Ou Black Friday!"},
            {"description": "Fundo Viagem", "amount": 2000.0, "notes": "Acumulado: R$ 3.000. Viagem curta em Jan/Fev ou continua juntando."},
            {"description": "Gastos pessoais + festas", "amount": 1000.0, "notes": "Final de ano. Curta com a familia."},
        ]},
    ]
)

print()
print("=" * 60)
print("JORNADA 2026 — VERSAO DEFINITIVA")
print("=" * 60)
print()
print("DIVIDAS (R$ 16.842):")
print("  Mai: Cartao 5k + atrasados + 8 menores (Rafael+Paula) = R$ 10.369")
print("  Jun: Estacio + Vivo = R$ 1.517")
print("  Jul: Ipanema + Nubank + CNH = R$ 2.803")
print("  Ago: SportAcao + Bradesco Paula = R$ 3.710")
print("  Set: Ipanema grande (negociar) = R$ 3.000")
print("  Out: Ipanema resto = R$ 2.645")
print("  TOTAL QUITADO: ~R$ 24.000 (com desconto ~R$ 16.000)")
print()
print("OBJETIVOS:")
print("  CNH: Jul (R$ 1.000)")
print("  Tratamento Paula: Out (R$ 3.500)")
print("  Congresso Espada: Nov (R$ 6.000)")
print("  Carro: Dez com 13o (R$ 25.000)")
print("  Viagem: comeca Dez (R$ 3.000)")
print("  TV OLED: comeca Dez (R$ 2.000)")
print()
print("RESERVA: R$ 300 > 1.800 > 3.300 > 4.800 > 6.300 > 7.800 > 9.300 > 10.800")
print()
print("DE: R$ 16.842 dividas, R$ 0 tudo")
print("PARA: R$ 0 dividas, R$ 10.800 reserva, carro, CNH, congresso, tratamento")
