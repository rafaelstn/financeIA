"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface Summary {
  income: number;
  expenses: number;
  balance: number;
  total_invested: number;
  total_current: number;
  tithe: number;
  tithe_status: string;
  firstfruits: number;
  firstfruits_status: string;
}

interface Props {
  month: number;
  year: number;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

export default function SummaryCards({ month, year }: Props) {
  const [data, setData] = useState<Summary | null>(null);

  useEffect(() => {
    setData(null);
    api.get(`/summary/monthly?month=${month}&year=${year}`).then((res) => setData(res.data));
  }, [month, year]);

  if (!data) return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-[120px] rounded-xl bg-card border border-border animate-pulse" />
        ))}
      </div>
      <div className="grid grid-cols-4 gap-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-[80px] rounded-[10px] bg-card border border-border animate-pulse" />
        ))}
      </div>
    </div>
  );

  const pctExpenses = data.income > 0 ? ((data.expenses / data.income) * 100).toFixed(1) : "0";
  const pctBalance = data.income > 0 ? ((data.balance / data.income) * 100).toFixed(1) : "0";

  return (
    <div className="space-y-3">
      {/* Hero Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Saldo */}
        <div className="relative overflow-hidden rounded-xl p-5 border card-hover"
          style={{ background: "linear-gradient(135deg, var(--hero-saldo-from), var(--hero-saldo-to))", borderColor: "var(--hero-saldo-border)" }}>
          <svg className="absolute bottom-0 left-0 right-0 h-10 opacity-20" viewBox="0 0 200 40" preserveAspectRatio="none">
            <polyline points="0,35 20,30 40,32 60,25 80,28 100,18 120,22 140,15 160,12 180,8 200,5" fill="none" stroke="var(--sparkline-saldo)" strokeWidth="2"/>
          </svg>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">Saldo</p>
          <p className="text-3xl font-bold mt-1 relative" style={{ color: data.balance >= 0 ? "var(--accent-green)" : "var(--accent-red)" }}>
            R$ {fmt(data.balance)}
          </p>
          <p className="text-sm text-muted-foreground mt-1.5 relative">
            {data.balance >= 0 ? "+" : ""}{pctBalance}% vs despesas
          </p>
        </div>

        {/* Receitas */}
        <div className="relative overflow-hidden rounded-xl p-5 border card-hover"
          style={{ background: "linear-gradient(135deg, var(--hero-receitas-from), var(--hero-receitas-to))", borderColor: "var(--hero-receitas-border)" }}>
          <svg className="absolute bottom-0 left-0 right-0 h-10 opacity-15" viewBox="0 0 200 40" preserveAspectRatio="none">
            <polyline points="0,30 30,28 60,25 90,20 120,22 150,15 200,10" fill="none" stroke="var(--sparkline-receitas)" strokeWidth="2"/>
          </svg>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">Receitas</p>
          <p className="text-3xl font-bold mt-1 relative">R$ {fmt(data.income)}</p>
          <p className="text-sm text-muted-foreground mt-1.5 relative">3 fontes de renda</p>
        </div>

        {/* Despesas */}
        <div className="relative overflow-hidden rounded-xl p-5 border card-hover"
          style={{ background: "linear-gradient(135deg, var(--hero-despesas-from), var(--hero-despesas-to))", borderColor: "var(--hero-despesas-border)" }}>
          <svg className="absolute bottom-0 left-0 right-0 h-10 opacity-15" viewBox="0 0 200 40" preserveAspectRatio="none">
            <polyline points="0,25 30,20 60,28 90,22 120,30 150,18 200,15" fill="none" stroke="var(--sparkline-despesas)" strokeWidth="2"/>
          </svg>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">Despesas</p>
          <p className="text-3xl font-bold mt-1 relative">R$ {fmt(data.expenses)}</p>
          <p className="text-sm text-muted-foreground mt-1.5 relative">{pctExpenses}% da receita</p>
        </div>
      </div>

      {/* Secondary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-[10px] p-3 bg-card border border-border card-hover">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Investido</p>
          <p className="text-lg font-semibold mt-1 text-muted-foreground">R$ {fmt(data.total_invested)}</p>
        </div>
        <div className="rounded-[10px] p-3 bg-card border border-border card-hover">
          <div className="flex justify-between items-center">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Dizimo</p>
            <span className="text-xs font-medium px-1.5 py-0.5 rounded-full"
              style={{
                color: data.tithe_status === "paid" ? "var(--status-paid-text)" : "var(--status-overdue-text)",
                background: data.tithe_status === "paid" ? "var(--status-paid-bg)" : "var(--status-overdue-bg)",
              }}>
              {data.tithe_status === "paid" ? "Pago" : "Pendente"}
            </span>
          </div>
          <p className="text-lg font-semibold mt-1">R$ {fmt(data.tithe)}</p>
        </div>
        <div className="rounded-[10px] p-3 bg-card border border-border card-hover">
          <div className="flex justify-between items-center">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Primicia</p>
            <span className="text-xs font-medium px-1.5 py-0.5 rounded-full"
              style={{
                color: data.firstfruits_status === "paid" ? "var(--status-paid-text)" : "var(--status-overdue-text)",
                background: data.firstfruits_status === "paid" ? "var(--status-paid-bg)" : "var(--status-overdue-bg)",
              }}>
              {data.firstfruits_status === "paid" ? "Pago" : "Pendente"}
            </span>
          </div>
          <p className="text-lg font-semibold mt-1">R$ {fmt(data.firstfruits)}</p>
        </div>
        <div className="rounded-[10px] p-3 bg-card border border-border card-hover">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Dividas</p>
          <p className="text-lg font-semibold mt-1" style={{ color: "var(--accent-red)" }}>—</p>
          <p className="text-xs text-muted-foreground mt-0.5">ver pagina de dividas</p>
        </div>
      </div>
    </div>
  );
}
