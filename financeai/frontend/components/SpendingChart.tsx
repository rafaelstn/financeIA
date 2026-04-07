"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
} from "recharts";
import api from "@/lib/api";

const COLORS = [
  "#10b981", "#f59e0b", "#ef4444", "#3b82f6",
  "#8b5cf6", "#ec4899", "#14b8a6", "#f97316",
  "#6366f1", "#84cc16",
];

const MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

export default function SpendingChart() {
  const [categoryData, setCategoryData] = useState<{ name: string; value: number }[]>([]);
  const [yearlyData, setYearlyData] = useState<{ name: string; receitas: number; despesas: number }[]>([]);

  useEffect(() => {
    api.get("/summary/monthly").then((res) => {
      const byCategory = res.data.by_category as Record<string, number>;
      setCategoryData(
        Object.entries(byCategory).map(([name, value]) => ({ name, value }))
      );
    });

    api.get("/summary/yearly").then((res) => {
      setYearlyData(
        res.data.months.map((m: { month: number; income: number; expenses: number }) => ({
          name: MONTH_LABELS[m.month - 1],
          receitas: m.income,
          despesas: m.expenses,
        }))
      );
    });
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Gastos por Categoria</CardTitle>
        </CardHeader>
        <CardContent>
          {categoryData.length === 0 ? (
            <p className="text-sm text-muted-foreground">Sem dados</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `R$ ${value.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Receitas x Despesas (Anual)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={yearlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip formatter={(value: number) => `R$ ${value.toFixed(2)}`} />
              <Legend />
              <Bar dataKey="receitas" fill="#10b981" />
              <Bar dataKey="despesas" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
