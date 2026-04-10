"""Planejamento DEFINITIVO v3 — Sem 13o, Congresso R$ 10k com viagem, sem viagem passeio"""
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
    {"description": "Crefito Paula", "amount": 72.0, "notes": "Parcela mensal"},
    {"description": "PlayStation", "amount": 65.0, "notes": ""},
    {"description": "Celular Paula", "amount": 62.0, "notes": ""},
]
cv_total = 7408.0

# MAIO
upsert(5, 2026, "Maio — Limpeza Total",
    "O mes mais pesado. Cartao R$ 5k + atrasados + 8 dividas menores (suas + Paula). "
    "TODAS as dividas pequenas da Paula morrem aqui. "
    "Maio vai ser apertado (R$ 22 de sobra) mas limpa o caminho inteiro. "
    "A partir de Junho voce respira e comeca a construir.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Limpeza Total", "total": 10369.0, "items": [
            {"description": "Fatura Cartao Rogerio", "amount": 5000.0, "notes": "PRIORIDADE. Rotativo e 15%/mes!"},
            {"description": "Faculdade Abril atrasada", "amount": 1507.0, "notes": "Com multa"},
            {"description": "Nubank Emp Paula — QUITAR", "amount": 663.0, "notes": "Negocie!"},
            {"description": "IR Paula + Rafael", "amount": 588.0, "notes": "Vence 29/05"},
            {"description": "Marisa Recovery Paula — QUITAR", "amount": 460.0, "notes": "Negocie!"},
            {"description": "Crefito Paula — QUITAR", "amount": 380.0, "notes": "Negocie!"},
            {"description": "Mercado Pago — QUITAR", "amount": 334.0, "notes": ""},
            {"description": "DAS atrasados Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Parcelamento DAS Jan-Mar", "amount": 300.0, "notes": "3x R$ 100"},
            {"description": "Nubank Cartao Paula — QUITAR", "amount": 260.0, "notes": ""},
            {"description": "Recovery — QUITAR", "amount": 253.0, "notes": ""},
            {"description": "Estacio Paula — QUITAR", "amount": 92.0, "notes": ""},
            {"description": "Claro 80 Paula — QUITAR", "amount": 80.0, "notes": ""},
            {"description": "Claro 68 Paula — QUITAR", "amount": 68.0, "notes": ""},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 300.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 300.0, "notes": "Mes apertado. O que da."},
        ]},
        {"category": "sobra", "title": "Sobra", "total": 22.0, "items": [
            {"description": "Imprevistos", "amount": 22.0, "notes": "Aperta em Maio, explode em Junho. Aguenta."},
        ]},
    ])

# JUNHO
upsert(6, 2026, "Junho — Comeca a Construir",
    "Paula livre! Agora ataca Estacio e Vivo do Rafael. "
    "E comeca 3 fundos simultaneos: Carro, Congresso e Tratamento. "
    "O carro precisa de R$ 25k ate Dezembro. O congresso precisa de R$ 10k ate Novembro. "
    "Voce tem capacidade. Tudo cabe se manter o foco.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Bola de Neve", "total": 1517.0, "items": [
            {"description": "Estacio Rafael — QUITAR", "amount": 708.0, "notes": "Negocie no Serasa!"},
            {"description": "Vivo — QUITAR", "amount": 809.0, "notes": "Negocie!"},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 1.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 7774.0, "items": [
            {"description": "Fundo Carro", "amount": 3807.0, "notes": "INICIO! Acumulado: R$ 3.807. Meta: R$ 25k Dez."},
            {"description": "Fundo Congresso + Viagem", "amount": 1667.0, "notes": "Inicio! Acumulado: R$ 1.667. Meta: R$ 10k Nov."},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Inicio! Acumulado: R$ 700."},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# JULHO
upsert(7, 2026, "Julho — CNH + Mais Duas",
    "CNH paga — precisa pra dirigir o carro! Ipanema e Nubank caem. "
    "Ja sao 12+ dividas eliminadas. O Serasa esta ficando limpo. "
    "Congresso em R$ 3.334. Carro em R$ 6.328. Tratamento em R$ 1.400.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas + CNH", "total": 2803.0, "items": [
            {"description": "CNH — Carteira de Motorista", "amount": 1000.0, "notes": "Precisa pra dirigir o carro!"},
            {"description": "Nubank Rafael — QUITAR", "amount": 945.0, "notes": "Use o app."},
            {"description": "Ipanema (858) — QUITAR", "amount": 858.0, "notes": "Negocie!"},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 2.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6888.0, "items": [
            {"description": "Fundo Carro", "amount": 2521.0, "notes": "Acumulado: R$ 6.328"},
            {"description": "Fundo Congresso + Viagem", "amount": 1667.0, "notes": "Acumulado: R$ 3.334"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Acumulado: R$ 1.400"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# AGOSTO
upsert(8, 2026, "Agosto — As Duas Grandes",
    "SportAcao R$ 2k e Bradesco Paula R$ 1.710 caem no mesmo mes. "
    "Depois desse mes: so sobra UMA divida (Ipanema grande). "
    "Negocie os dois — SportAcao pode baixar pra R$ 1.200, Bradesco pra R$ 1.000.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — As Grandes", "total": 3710.0, "items": [
            {"description": "SportAcao — QUITAR", "amount": 2000.0, "notes": "Negocie! Pode cair pra R$ 1.200."},
            {"description": "Bradesco Paula — QUITAR", "amount": 1710.0, "notes": "Maior da Paula. Negocie forte!"},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 3.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 5981.0, "items": [
            {"description": "Fundo Carro", "amount": 1614.0, "notes": "Acumulado: R$ 7.942. Mes pesado com 2 dividas grandes."},
            {"description": "Fundo Congresso + Viagem", "amount": 1667.0, "notes": "Acumulado: R$ 5.001. Metade!"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Acumulado: R$ 2.100"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# SETEMBRO
upsert(9, 2026, "Setembro — O Chefao",
    "Ultima divida: Ipanema R$ 5.645. NEGOCIE! Desconto de 50-80% e possivel em divida antiga. "
    "Tente pagar R$ 2.000-3.000. Cada real economizado aqui vai pro carro. "
    "Tratamento Paula quase completo. Congresso passando de R$ 6.600.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — Chefao", "total": 3000.0, "items": [
            {"description": "Ipanema grande — NEGOCIAR", "amount": 3000.0, "notes": "Original R$ 5.645. NEGOCIE! Tente R$ 2k-3k."},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 4.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 6691.0, "items": [
            {"description": "Fundo Carro", "amount": 2324.0, "notes": "Acumulado: R$ 10.266"},
            {"description": "Fundo Congresso + Viagem", "amount": 1667.0, "notes": "Acumulado: R$ 6.668"},
            {"description": "Tratamento Paula", "amount": 700.0, "notes": "Acumulado: R$ 2.800"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# OUTUBRO
upsert(10, 2026, "Outubro — Livre de Dividas!",
    "Ipanema resto quitada. TODAS AS DIVIDAS ZERADAS (suas + Paula)! "
    "Tratamento Paula completo em R$ 3.500. "
    "Carro em R$ 12.945. Congresso em R$ 8.335. Tudo acelerando!",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "dividas", "title": "Dividas — FINAL", "total": 2645.0, "items": [
            {"description": "Ipanema grande — QUITAR RESTO", "amount": 2645.0, "notes": "Se negociou em Set, pode ser zero!"},
        ]},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 5.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 7046.0, "items": [
            {"description": "Fundo Carro", "amount": 2679.0, "notes": "Acumulado: R$ 12.945"},
            {"description": "Fundo Congresso + Viagem", "amount": 1667.0, "notes": "Acumulado: R$ 8.335"},
            {"description": "Tratamento Paula — COMPLETAR", "amount": 700.0, "notes": "Acumulado: R$ 3.500. META BATIDA!"},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# NOVEMBRO
upsert(11, 2026, "Novembro — Congresso Pago!",
    "Congresso Espada na Fase PAGO! R$ 10k antes do deadline dia 20. "
    "Sem dividas. Tratamento feito. Carro quase la — R$ 18.969. "
    "Dezembro e so carro + TV. Voce venceu a batalha mais dificil.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 6.300"},
        ]},
        {"category": "sobra", "title": "Objetivos + Pessoal", "total": 9691.0, "items": [
            {"description": "Fundo Carro", "amount": 6024.0, "notes": "Acumulado: R$ 18.969. Sem dividas = carro acelera!"},
            {"description": "Congresso + Viagem — PAGAR", "amount": 1667.0, "notes": "Acumulado: R$ 10.002. META BATIDA! Deadline 20/Nov."},
            {"description": "Gastos pessoais", "amount": 2000.0, "notes": ""},
        ]},
    ])

# DEZEMBRO
upsert(12, 2026, "Dezembro — O Carro Chega!",
    "R$ 26.660 no fundo do carro. COMPRA! "
    "E ainda comeca o fundo da TV OLED. "
    "Olha a jornada: R$ 16.842 em dividas -> R$ 0. Sem carro -> com carro. "
    "Sem reserva -> R$ 7.300. Congresso pago. Tratamento feito. CNH tirada. "
    "Isso nao e sorte — e disciplina. 2027 comeca no volante.",
    [
        {"category": "custo_vida", "title": "Custo de Vida", "total": cv_total, "items": cv},
        {"category": "reserva", "title": "Reserva", "total": 1000.0, "items": [
            {"description": "CDB liquidez diaria", "amount": 1000.0, "notes": "Acumulado: R$ 7.300"},
        ]},
        {"category": "sobra", "title": "Carro + TV + Pessoal", "total": 9691.0, "items": [
            {"description": "Carro — COMPRAR!", "amount": 5691.0, "notes": "Acumulado: R$ 24.660+. Pesquise, negocie, leve mecanico. E SEU!"},
            {"description": "TV OLED Samsung", "amount": 2000.0, "notes": "Comeca! Continua em 2027 ou Black Friday."},
            {"description": "Gastos pessoais + festas", "amount": 2000.0, "notes": "Final de ano. Voce conquistou. Curta."},
        ]},
    ])

print()
print("=" * 60)
print("JORNADA 2026 — SEM 13o — VERSAO FINAL")
print("=" * 60)
print()
print("CARRO: Jun R$3.8k > Jul R$6.3k > Ago R$7.9k > Set R$10.3k > Out R$12.9k > Nov R$19k > Dez R$26.6k = COMPRA!")
print("CONGRESSO+VIAGEM: R$1.667/mes Jun-Nov = R$ 10k = PAGO!")
print("TRATAMENTO: R$700/mes Jun-Out = R$ 3.500 = COMPLETO!")
print("CNH: Julho = PAGA!")
print("TV OLED: Comeca em Dezembro")
print("RESERVA: R$ 7.300")
print()
print("DE: R$ 16.842 dividas, R$ 0 tudo")
print("PARA: R$ 0 divida, carro, CNH, congresso, tratamento, R$ 7.300 reserva")
