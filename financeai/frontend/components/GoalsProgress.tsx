"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Target } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";

interface Goal {
  id: string;
  name: string;
  target_amount: number;
  saved_amount: number;
  status: string;
}

export default function GoalsProgress() {
  const [goals, setGoals] = useState<Goal[]>([]);

  useEffect(() => {
    api.get("/goals", { params: { status: "ativa" } }).then((res) => setGoals(res.data));
  }, []);

  const displayed = goals.slice(0, 4);

  if (displayed.length === 0) return null;

  const progressColor = (pct: number) => {
    if (pct >= 80) return "bg-emerald-500";
    if (pct >= 50) return "bg-blue-500";
    if (pct >= 25) return "bg-yellow-500";
    return "bg-red-400";
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-500" />
          Progresso dos Objetivos
        </CardTitle>
        <Link href="/goals" className="text-sm text-blue-500 hover:underline">
          Ver todos
        </Link>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayed.map((g) => {
            const pct = g.target_amount > 0 ? Math.min((g.saved_amount / g.target_amount) * 100, 100) : 0;
            return (
              <div key={g.id} className="space-y-2 p-3 rounded-lg border">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium truncate">{g.name}</p>
                  <span className="text-xs text-muted-foreground">{pct.toFixed(0)}%</span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${progressColor(pct)}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>
                    R$ {g.saved_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                  <span>
                    R$ {g.target_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
