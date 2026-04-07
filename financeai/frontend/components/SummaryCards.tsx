"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, TrendingUp, TrendingDown, PiggyBank } from "lucide-react";
import api from "@/lib/api";

interface Summary {
  income: number;
  expenses: number;
  balance: number;
  total_invested: number;
  total_current: number;
}

export default function SummaryCards() {
  const [data, setData] = useState<Summary | null>(null);

  useEffect(() => {
    api.get("/summary/monthly").then((res) => setData(res.data));
  }, []);

  if (!data) return null;

  const cards = [
    { title: "Saldo do Mes", value: data.balance, icon: DollarSign, color: data.balance >= 0 ? "text-emerald-500" : "text-red-500" },
    { title: "Receitas", value: data.income, icon: TrendingUp, color: "text-emerald-500" },
    { title: "Despesas", value: data.expenses, icon: TrendingDown, color: "text-red-500" },
    { title: "Investido", value: data.total_current, icon: PiggyBank, color: "text-blue-500" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${card.color}`}>
              R$ {card.value.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
