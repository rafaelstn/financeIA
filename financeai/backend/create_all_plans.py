"""Planejamento DEFINITIVO v5 — CNH 3x em Maio, equilibrado"""
from database import supabase

def upsert(m, y, title, obs, sections):
    content = {"sections": sections}
    ex = supabase.table("financial_plans").select("id").eq("month", m).eq("year", y).execute().data
    if ex:
        supabase.table("financial_plans").update({"title": title, "observations": obs, "content": content}).eq("id", ex[0]["id"]).execute()
    else:
        supabase.table("financial_plans").insert({"month": m, "year": y, "title": title, "status": "planejado", "observations": obs, "content": content}).execute()
    print(f"  {title}")

cv = [
    {"description": "Mercado", "amount": 2000.0, "notes": ""},
    {"description": "Dizimo", "amount": 1810.0, "notes": "10% da renda"},
    {"description": "Faculdade", "amount": 1305.0, "notes": "No prazo!"},
    {"description": "Aluguel", "amount": 1200.0, "notes": ""},
    {"description": "Baba", "amount": 1000.0, "notes": ""},
    {"description": "Primicia", "amount": 603.0, "notes": ""},
    {"description": "Luz", "amount": 190.0, "notes": ""},
    {"description": "Gas", "amount": 130.0, "notes": ""},
    {"description": "Internet", "amount": 130.0, "notes": ""},
    {"description": "Parcelamento DAS", "amount": 100.0, "notes": ""},
    {"description": "DAS MEI Mensal", "amount": 86.0, "notes": ""},
    {"description": "Agua", "amount": 80.0, "notes": ""},
    {"description": "Celular Rafael", "amount": 75.0, "notes": ""},
    {"description": "Crefito Paula", "amount": 72.0, "notes": ""},
    {"description": "PlayStation", "amount": 65.0, "notes": ""},
    {"description": "Celular Paula", "amount": 62.0, "notes": ""},
]
T = 7408.0

# MAIO — Urgentes + CNH 1/3
upsert(5, 2026, "Maio — Limpeza + CNH",
    "Mes de limpeza: cartao, atrasados e IR. Mais a primeira parcela da CNH. "
    "As dividas pequenas da Paula ficam pra Junho/Agosto — assim Maio nao aperta demais. "
    "Sobra R$ 662 pra imprevistos. Apertado mas possivel.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "dividas", "title": "Dividas — Urgentes + CNH 1/3", "total": 8029.0, "items": [
            {"description": "Fatura Cartao Rogerio", "amount": 5000.0, "notes": "PRIORIDADE. Rotativo = 15%/mes!"},
            {"description": "Faculdade Abril atrasada", "amount": 1507.0, "notes": "Com multa"},
            {"description": "IR Paula + Rafael", "amount": 588.0, "notes": "Vence 29/05"},
            {"description": "DAS atrasados Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Parcelamento DAS Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "CNH — Parcela 1/3", "amount": 334.0, "notes": "Auto-escola. Parcela 1 de 3."},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 500.0, "notes": "Acum: R$ 500"},
        ]},
        {"category": "sobra", "title": "Sobra", "total": 1254.0, "items": [
            {"description": "Gastos pessoais", "amount": 1254.0, "notes": "Apertado mas respira em Junho."},
        ]},
    ])

# JUNHO — Bola de neve + 4 menores Paula + CNH 2/3
upsert(6, 2026, "Junho — Comeca a Construir",
    "Estacio e Vivo caem. 4 dividas menores da Paula caem tambem (Claro, Estacio, Nubank Cartao). "
    "Comeca Carro, Congresso e Tratamento. A maquina ligou.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "dividas", "title": "Dividas — 6 quitadas!", "total": 2351.0, "items": [
            {"description": "Vivo — QUITAR", "amount": 809.0, "notes": "Negocie!"},
            {"description": "Estacio Rafael — QUITAR", "amount": 708.0, "notes": "Negocie!"},
            {"description": "CNH — Parcela 2/3", "amount": 334.0, "notes": ""},
            {"description": "Mercado Pago — QUITAR", "amount": 334.0, "notes": ""},
            {"description": "Claro 80 Paula — QUITAR", "amount": 80.0, "notes": ""},
            {"description": "Claro 68 Paula — QUITAR", "amount": 68.0, "notes": ""},
            {"description": "Estacio Paula — QUITAR", "amount": 92.0, "notes": ""},
            {"description": "Nubank Cartao Paula — QUITAR", "amount": 260.0, "notes": ""},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acum: R$ 1.500"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6640.0, "items": [
            {"description": "Fundo Carro", "amount": 2973.0, "notes": "Inicio! Acum: R$ 2.973"},
            {"description": "Congresso + Viagem", "amount": 1667.0, "notes": "Acum: R$ 1.667"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# JULHO — Ipanema + Nubank + CNH 3/3 + Aniversario Paula
upsert(7, 2026, "Julho — Aniversario Paula + CNH Pronta",
    "CNH finalizada! Ipanema e Nubank caem. Presente da Paula — voces estao juntos nessa. "
    "Comeca o Tratamento dela este mes.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "dividas", "title": "Dividas + CNH Final", "total": 2137.0, "items": [
            {"description": "Nubank Rafael — QUITAR", "amount": 945.0, "notes": ""},
            {"description": "Ipanema (858) — QUITAR", "amount": 858.0, "notes": "Negocie!"},
            {"description": "CNH — Parcela 3/3", "amount": 334.0, "notes": "ULTIMA! CNH completa."},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acum: R$ 2.500"},
        ]},
        {"category": "sobra", "title": "Objetivos + Aniversario", "total": 7554.0, "items": [
            {"description": "Fundo Carro", "amount": 2687.0, "notes": "Acum: R$ 5.660"},
            {"description": "Congresso + Viagem", "amount": 1667.0, "notes": "Acum: R$ 3.334"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Inicio! Acum: R$ 700"},
            {"description": "Aniversario Paula", "amount": 500.0, "notes": "Presente + jantar ou passeio especial"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# AGOSTO — Bradesco + 5 dividas Paula restantes
upsert(8, 2026, "Agosto — Paula Livre!",
    "Bradesco + 5 dividas da Paula caem de vez. Depois desse mes, Paula ZERO no Serasa! "
    "So sobra a Ipanema grande do Rafael. Quase la.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "dividas", "title": "Dividas — Paula Livre!", "total": 3800.0, "items": [
            {"description": "Bradesco Paula — QUITAR", "amount": 1710.0, "notes": "A maior. Negocie!"},
            {"description": "Nubank Emp Paula — QUITAR", "amount": 663.0, "notes": "Negocie!"},
            {"description": "Marisa Recovery Paula — QUITAR", "amount": 460.0, "notes": ""},
            {"description": "Crefito Paula — QUITAR", "amount": 380.0, "notes": ""},
            {"description": "Recovery Rafael — QUITAR", "amount": 253.0, "notes": ""},
            {"description": "Recovery — QUITAR", "amount": 334.0, "notes": ""},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acum: R$ 3.500"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 5891.0, "items": [
            {"description": "Fundo Carro", "amount": 2024.0, "notes": "Acum: R$ 7.684"},
            {"description": "Congresso + Viagem", "amount": 1667.0, "notes": "Acum: R$ 5.001. Metade!"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Acum: R$ 1.400"},
            {"description": "Gastos pessoais", "amount": 1500.0, "notes": ""},
        ]},
    ])

# SETEMBRO — Chefao + TV comeca
upsert(9, 2026, "Setembro — O Chefao + TV",
    "Ultima divida grande: Ipanema R$ 5.645. NEGOCIE forte. TV OLED comeca a ser juntada. "
    "Presente de aniversario em Dezembro ta sendo construido.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "dividas", "title": "Dividas — Chefao", "total": 3000.0, "items": [
            {"description": "Ipanema grande — NEGOCIAR", "amount": 3000.0, "notes": "Original R$ 5.645. Tente R$ 2k-3k!"},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acum: R$ 4.500"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6691.0, "items": [
            {"description": "Fundo Carro", "amount": 1624.0, "notes": "Acum: R$ 9.308"},
            {"description": "Congresso + Viagem", "amount": 1667.0, "notes": "Acum: R$ 6.668"},
            {"description": "TV OLED Samsung", "amount": 1200.0, "notes": "Inicio! Acum: R$ 1.200"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Acum: R$ 2.100"},
            {"description": "Gastos pessoais", "amount": 1500.0, "notes": ""},
        ]},
    ])

# OUTUBRO — Ipanema resto + Tratamento completo
upsert(10, 2026, "Outubro — Livre de Dividas!",
    "TODAS AS DIVIDAS ZERADAS! Tratamento Paula completo. "
    "TV em R$ 3.400. Carro em R$ 11k. Congresso em R$ 8.335.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "dividas", "title": "Dividas — FINAL", "total": 2645.0, "items": [
            {"description": "Ipanema grande — RESTO", "amount": 2645.0, "notes": "Se negociou em Set, pode ser zero!"},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acum: R$ 5.500"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 7046.0, "items": [
            {"description": "Fundo Carro", "amount": 1979.0, "notes": "Acum: R$ 11.287"},
            {"description": "Congresso + Viagem", "amount": 1667.0, "notes": "Acum: R$ 8.335"},
            {"description": "TV OLED Samsung", "amount": 1200.0, "notes": "Acum: R$ 2.400"},
            {"description": "Tratamento Paula — COMPLETO", "amount": 700.0, "notes": "Acum: R$ 2.800. Quase! Completa em breve."},
            {"description": "Gastos pessoais", "amount": 1500.0, "notes": ""},
        ]},
    ])

# NOVEMBRO — Congresso pago!
upsert(11, 2026, "Novembro — Congresso Pago!",
    "Congresso + Viagem PAGO! R$ 10k antes do deadline 20/Nov. "
    "TV em R$ 4.900. Carro em R$ 16.811. Dezembro fecha tudo.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acum: R$ 6.500"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 9691.0, "items": [
            {"description": "Fundo Carro", "amount": 5024.0, "notes": "Acum: R$ 16.311. Sem dividas = carro voa!"},
            {"description": "Congresso + Viagem — PAGAR", "amount": 1667.0, "notes": "Acum: R$ 10.002. META BATIDA!"},
            {"description": "TV OLED Samsung", "amount": 1500.0, "notes": "Acum: R$ 3.900"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Acum: R$ 3.500. COMPLETO!"},
            {"description": "Gastos pessoais", "amount": 800.0, "notes": "Reduzido pra fechar TV em Dez"},
        ]},
    ])

# DEZEMBRO — Carro + TV! Aniversario!
upsert(12, 2026, "Dezembro — Carro + TV! Feliz Aniversario!",
    "SEU MES! Carro bate R$ 25k. TV OLED bate R$ 6k. Dois presentes de aniversario! "
    "A jornada: R$ 16.842 em dividas -> R$ 0. Sem nada -> carro + TV + reserva + CNH + congresso + tratamento. "
    "Em 8 meses voce transformou tudo. Parabens, Rafael.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": T, "items": cv},
        {"category": "reserva", "title": "Reserva", "total": 500.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 500.0, "notes": "Acum: R$ 7.000. Reduzida pra fechar TV."},
        ]},
        {"category": "sobra", "title": "Carro + TV + Aniversario!", "total": 10191.0, "items": [
            {"description": "Carro — COMPRAR!", "amount": 5591.0, "notes": "Acum: R$ 21.902. Pesquise, negocie, leve mecanico!"},
            {"description": "TV OLED Samsung — COMPRAR!", "amount": 2100.0, "notes": "Acum: R$ 6.000. META BATIDA! Presente de aniversario!"},
            {"description": "Gastos pessoais + aniversario", "amount": 2500.0, "notes": "Seu mes. Comemore TUDO."},
        ]},
    ])

print()
print("=" * 60)
print("VERSAO FINAL v5 — EQUILIBRADA")
print("=" * 60)
print("Mai: R$ 1.254 livre (era R$ 22)")
print("Jun-Dez: R$ 1.500-2.500 livre")
print("CNH: 3x Mai/Jun/Jul")
print("Carro: R$ 25.000 Dez")
print("TV OLED: R$ 6.000 Dez (aniversario!)")
print("Congresso: R$ 10.000 Nov")
print("Tratamento: R$ 3.500 Nov")
print("Reserva: R$ 7.000")
