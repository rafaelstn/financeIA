"""Script para criar o Ciclo 1 de planejamento financeiro (Mai-Jul 2026)"""
import json
import httpx

BASE = "http://localhost:8000/api"
headers = {"Content-Type": "application/json"}

plans = [
    {
        "month": 5, "year": 2026,
        "title": "Ciclo 1 - Maio/2026 - Limpeza e Organizacao",
        "status": "planejado",
        "observations": "Primeiro mes do ciclo. Regularizar atrasados, quitar dividas menores (bola de neve) e comecar reserva.",
        "content": {"sections": [
            {"category": "custo_vida", "title": "Custo de Vida", "total": 7336.0, "items": [
                {"description": "Aluguel", "amount": 1200.0, "notes": "Vence dia 5"},
                {"description": "Faculdade", "amount": 1305.0, "notes": "Pagar no prazo pra nao virar 1.570"},
                {"description": "Baba", "amount": 1000.0, "notes": ""},
                {"description": "Mercado", "amount": 500.0, "notes": ""},
                {"description": "Luz", "amount": 190.0, "notes": ""},
                {"description": "Gas", "amount": 130.0, "notes": ""},
                {"description": "Internet", "amount": 130.0, "notes": ""},
                {"description": "DAS MEI Mensal", "amount": 86.0, "notes": "Ate 10o dia util"},
                {"description": "Parcelamento DAS", "amount": 100.0, "notes": "Dia 20"},
                {"description": "Agua", "amount": 80.0, "notes": ""},
                {"description": "Celular Rafael", "amount": 75.0, "notes": ""},
                {"description": "PlayStation", "amount": 65.0, "notes": "Wagner paga metade R$30"},
                {"description": "Celular Paula", "amount": 62.0, "notes": ""},
                {"description": "Dizimo", "amount": 1810.0, "notes": "10% da renda R$ 18.099"},
                {"description": "Primicia", "amount": 603.0, "notes": "1/30 da renda"},
            ]},
            {"category": "dividas", "title": "Dividas - Regularizacao + Bola de Neve", "total": 3282.0, "items": [
                {"description": "Faculdade Abril atrasada", "amount": 1507.0, "notes": "Pagar com multa pra limpar"},
                {"description": "IR Paula + Rafael", "amount": 588.0, "notes": "2 boletos vence 29/05"},
                {"description": "DAS atrasados Jan-Mar", "amount": 300.0, "notes": "3x R$100"},
                {"description": "Parcelamento DAS atrasado Jan-Mar", "amount": 300.0, "notes": "3x R$100"},
                {"description": "Recovery - QUITAR", "amount": 253.0, "notes": "Menor divida"},
                {"description": "Mercado Pago - QUITAR", "amount": 334.0, "notes": "Segunda menor"},
            ]},
            {"category": "reserva", "title": "Reserva de Emergencia", "total": 2000.0, "items": [
                {"description": "CDB liquidez diaria", "amount": 2000.0, "notes": "Inicio da reserva. Meta: 6 meses de custo de vida"},
            ]},
            {"category": "sobra", "title": "Sobra Livre", "total": 5481.0, "items": [
                {"description": "Gastos pessoais e imprevistos", "amount": 5481.0, "notes": "Receita 18.099 - custo vida 7.336 - dividas 3.282 - reserva 2.000"},
            ]},
        ]},
    },
    {
        "month": 6, "year": 2026,
        "title": "Ciclo 1 - Junho/2026 - Ataque nas Dividas",
        "status": "planejado",
        "observations": "Segundo mes. Atrasados limpos. Quitar Estacio e Vivo (bola de neve). Reserva crescendo.",
        "content": {"sections": [
            {"category": "custo_vida", "title": "Custo de Vida", "total": 7336.0, "items": [
                {"description": "Aluguel", "amount": 1200.0, "notes": ""},
                {"description": "Faculdade", "amount": 1305.0, "notes": ""},
                {"description": "Baba", "amount": 1000.0, "notes": ""},
                {"description": "Mercado", "amount": 500.0, "notes": ""},
                {"description": "Luz", "amount": 190.0, "notes": ""},
                {"description": "Gas", "amount": 130.0, "notes": ""},
                {"description": "Internet", "amount": 130.0, "notes": ""},
                {"description": "DAS MEI Mensal", "amount": 86.0, "notes": ""},
                {"description": "Parcelamento DAS", "amount": 100.0, "notes": ""},
                {"description": "Agua", "amount": 80.0, "notes": ""},
                {"description": "Celular Rafael", "amount": 75.0, "notes": ""},
                {"description": "PlayStation", "amount": 65.0, "notes": ""},
                {"description": "Celular Paula", "amount": 62.0, "notes": ""},
                {"description": "Dizimo", "amount": 1810.0, "notes": ""},
                {"description": "Primicia", "amount": 603.0, "notes": ""},
            ]},
            {"category": "dividas", "title": "Dividas - Bola de Neve (medias)", "total": 1517.0, "items": [
                {"description": "Estacio - QUITAR", "amount": 708.0, "notes": "Negociar desconto no Serasa"},
                {"description": "Vivo - QUITAR", "amount": 809.0, "notes": "Negociar desconto no Serasa"},
            ]},
            {"category": "reserva", "title": "Reserva de Emergencia", "total": 2000.0, "items": [
                {"description": "CDB liquidez diaria", "amount": 2000.0, "notes": "Acumulado: R$ 4.000"},
            ]},
            {"category": "sobra", "title": "Sobra Livre", "total": 7246.0, "items": [
                {"description": "Gastos pessoais e imprevistos", "amount": 7246.0, "notes": "Mes tranquilo sem atrasados"},
            ]},
        ]},
    },
    {
        "month": 7, "year": 2026,
        "title": "Ciclo 1 - Julho/2026 - Fim do Ciclo",
        "status": "planejado",
        "observations": "Ultimo mes do Ciclo 1. Quitar Ipanema (858) e Nubank. CNH paga. Proximo ciclo: SportAcao, Ipanema grande, investimentos.",
        "content": {"sections": [
            {"category": "custo_vida", "title": "Custo de Vida", "total": 7336.0, "items": [
                {"description": "Aluguel", "amount": 1200.0, "notes": ""},
                {"description": "Faculdade", "amount": 1305.0, "notes": ""},
                {"description": "Baba", "amount": 1000.0, "notes": ""},
                {"description": "Mercado", "amount": 500.0, "notes": ""},
                {"description": "Luz", "amount": 190.0, "notes": ""},
                {"description": "Gas", "amount": 130.0, "notes": ""},
                {"description": "Internet", "amount": 130.0, "notes": ""},
                {"description": "DAS MEI Mensal", "amount": 86.0, "notes": ""},
                {"description": "Parcelamento DAS", "amount": 100.0, "notes": ""},
                {"description": "Agua", "amount": 80.0, "notes": ""},
                {"description": "Celular Rafael", "amount": 75.0, "notes": ""},
                {"description": "PlayStation", "amount": 65.0, "notes": ""},
                {"description": "Celular Paula", "amount": 62.0, "notes": ""},
                {"description": "Dizimo", "amount": 1810.0, "notes": ""},
                {"description": "Primicia", "amount": 603.0, "notes": ""},
            ]},
            {"category": "dividas", "title": "Dividas - Bola de Neve (continuacao)", "total": 1803.0, "items": [
                {"description": "Ipanema (858) - QUITAR", "amount": 858.0, "notes": "Negociar desconto"},
                {"description": "Nubank - QUITAR", "amount": 945.0, "notes": "Negociar desconto"},
            ]},
            {"category": "reserva", "title": "Reserva de Emergencia", "total": 2000.0, "items": [
                {"description": "CDB liquidez diaria", "amount": 2000.0, "notes": "Acumulado: R$ 6.000"},
            ]},
            {"category": "sobra", "title": "Sobra Livre", "total": 6960.0, "items": [
                {"description": "Gastos pessoais e imprevistos", "amount": 5960.0, "notes": ""},
                {"description": "CNH - Carteira de Motorista", "amount": 1000.0, "notes": "Meta prioritaria - quitar neste mes"},
            ]},
        ]},
    },
]

for p in plans:
    r = httpx.post(f"{BASE}/plans/", headers=headers, json=p)
    if r.status_code == 201:
        print(f"OK: {p['title']}")
    else:
        print(f"ERRO: {p['title']} - {r.status_code} - {r.text}")

print()
print("=== RESUMO CICLO 1 (Mai-Jul 2026) ===")
print("Dividas quitadas: Recovery, Mercado Pago, Estacio, Vivo, Ipanema (858), Nubank")
print("Total quitado: R$ 3.908")
print("Dividas restantes: SportAcao R$ 2.000 + Ipanema R$ 5.645 + DAS R$ 1.000 = R$ 8.645")
print("Reserva acumulada: R$ 6.000")
print("Meta CNH: quitada em julho")
