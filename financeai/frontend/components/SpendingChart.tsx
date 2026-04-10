"use client";

import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";
import api from "@/lib/api";

const CATEGORY_COLORS = ["#60a5fa", "#c084fc", "#f59e0b", "#34d399", "#f87171", "#fb923c", "#a78bfa", "#38bdf8"];
const MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

interface Props {
  month: number;
  year: number;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

export default function SpendingChart({ month, year }: Props) {
  const [categoryData, setCategoryData] = useState<{ name: string; value: number }[]>([]);
  const [yearlyData, setYearlyData] = useState<{ name: string; receitas: number; despesas: number }[]>([]);

  useEffect(() => {
    api.get(`/summary/monthly?month=${month}&year=${year}`).then((res) => {
      const byCategory = res.data.by_category as Record<string, number>;
      const sorted = Object.entries(byCategory)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5);
      setCategoryData(sorted);
    });

    api.get(`/summary/yearly?year=${year}`).then((res) => {
      setYearlyData(
        res.data.months
          .filter((m: { income: number; expenses: number }) => m.income > 0 || m.expenses > 0)
          .map((m: { month: number; income: number; expenses: number }) => ({
            name: MONTH_LABELS[m.month - 1],
            receitas: m.income,
            despesas: m.expenses,
          }))
      );
    });
  }, [month, year]);

  const isLoading = categoryData.length === 0 && yearlyData.length === 0;

  if (isLoading) return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-3">
      <div className="lg:col-span-3 h-[280px] rounded-[10px] bg-card border border-border animate-pulse" />
      <div className="lg:col-span-2 h-[280px] rounded-[10px] bg-card border border-border animate-pulse" />
    </div>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-3">
      {/* Bar chart - Evolução mensal */}
      <div className="lg:col-span-3 rounded-[10px] p-4 bg-card border border-border card-hover">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-semibold">Evolucao mensal</h3>
          <div className="flex gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-sm bg-[#60a5fa]" />
              <span className="text-xs text-muted-foreground">Receitas</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-sm bg-[#f87171]" />
              <span className="text-xs text-muted-foreground">Despesas</span>
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={yearlyData} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" vertical={false} />
            <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false}
              tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v)} />
            <Tooltip
              contentStyle={{ background: "#111a2e", border: "1px solid #1e2d4a", borderRadius: "8px", fontSize: "12px" }}
              formatter={(value: number) => `R$ ${fmt(value)}`}
            />
            <Bar dataKey="receitas" fill="#60a5fa" radius={[3, 3, 0, 0]} />
            <Bar dataKey="despesas" fill="#f87171" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Donut chart - Top 5 categorias */}
      <div className="lg:col-span-2 rounded-[10px] p-4 bg-card border border-border card-hover">
        <h3 className="text-sm font-semibold mb-3">Top 5 Despesas por categoria</h3>
        {categoryData.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sem dados</p>
        ) : (
          <div className="flex gap-3 items-center">
            <div className="w-[100px] h-[100px] flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    dataKey="value"
                    cx="50%"
                    cy="50%"
                    innerRadius={28}
                    outerRadius={45}
                    strokeWidth={0}
                  >
                    {categoryData.map((_, i) => (
                      <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-2">
              {categoryData.map((cat, i) => (
                <div key={cat.name} className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-sm flex-shrink-0" style={{ background: CATEGORY_COLORS[i] }} />
                  <span className="text-xs text-muted-foreground flex-1">{cat.name}</span>
                  <span className="text-xs font-medium">R$ {fmt(cat.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
