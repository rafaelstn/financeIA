"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/lib/api";

interface ComparisonData {
  month: number;
  year: number;
  plan: {
    content: {
      sections: {
        category: string;
        title: string;
        total: number;
      }[];
    };
  } | null;
  actual: {
    income: number;
    expenses: number;
    balance: number;
    by_category: Record<string, number>;
    debts_paid: string[];
    total_invested: number;
  };
}

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function PlanComparison({ month, year }: { month: number; year: number }) {
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.get(`/plans/${month}/${year}/comparison`)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [month, year]);

  if (loading) return (
    <Card>
      <CardContent className="p-6">
        <div className="h-32 bg-muted animate-pulse rounded" />
      </CardContent>
    </Card>
  );

  if (!data || !data.plan) return null;

  const sections = data.plan.content.sections || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">
          Planejado vs Realizado — {MONTH_NAMES[month - 1]}/{year}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 text-xs font-medium text-muted-foreground border-b border-border pb-2">
          <span>Categoria</span>
          <span className="text-right">Planejado</span>
          <span className="text-right">Realizado</span>
        </div>

        {sections.map((section) => {
          const actual = section.category === "custo_vida"
            ? data.actual.expenses
            : section.category === "reserva"
            ? data.actual.total_invested
            : 0;

          const diff = section.total - actual;
          const diffColor = diff >= 0 ? "text-emerald-400" : "text-red-400";

          return (
            <div key={section.category} className="grid grid-cols-3 text-sm">
              <span>{section.title}</span>
              <span className="text-right">
                R$ {section.total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
              <span className={`text-right ${diffColor}`}>
                R$ {actual.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>
          );
        })}

        <div className="border-t border-border pt-2 grid grid-cols-3 text-sm font-bold">
          <span>Receita Total</span>
          <span className="text-right">—</span>
          <span className="text-right text-emerald-400">
            R$ {data.actual.income.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
          </span>
        </div>

        {data.actual.debts_paid.length > 0 && (
          <div className="text-xs text-emerald-400 mt-2">
            Dívidas quitadas: {data.actual.debts_paid.join(", ")}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
