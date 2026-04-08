"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, TrendingUp, TrendingDown, PiggyBank, Heart, Star } from "lucide-react";
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

export default function SummaryCards() {
  const [data, setData] = useState<Summary | null>(null);

  useEffect(() => {
    api.get("/summary/monthly").then((res) => setData(res.data));
  }, []);

  if (!data) return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {[...Array(6)].map((_, i) => (
        <Card key={i}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div className="h-4 w-24 bg-muted animate-pulse rounded" />
          </CardHeader>
          <CardContent>
            <div className="h-8 w-32 bg-muted animate-pulse rounded" />
          </CardContent>
        </Card>
      ))}
    </div>
  );

  const cards = [
    { title: "Saldo do Mês", value: data.balance, icon: DollarSign, color: data.balance >= 0 ? "text-emerald-500" : "text-red-500" },
    { title: "Receitas", value: data.income, icon: TrendingUp, color: "text-emerald-500" },
    { title: "Despesas", value: data.expenses, icon: TrendingDown, color: "text-red-500" },
    { title: "Investido", value: data.total_current, icon: PiggyBank, color: "text-blue-500" },
    { title: "Dízimo", value: data.tithe, icon: Heart, color: "text-purple-500", status: data.tithe_status },
    { title: "Primícia", value: data.firstfruits, icon: Star, color: "text-amber-500", status: data.firstfruits_status },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
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
            {"status" in card && card.status && (
              <span className={`text-xs mt-1 inline-block px-2 py-0.5 rounded-full ${
                card.status === "paid"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-amber-500/20 text-amber-400"
              }`}>
                {card.status === "paid" ? "Pago" : "Pendente"}
              </span>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
