"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";

interface Goal {
  id: string;
  name: string;
  target_amount: number;
  saved_amount: number;
  status: string;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

export default function GoalsProgress() {
  const [goals, setGoals] = useState<Goal[]>([]);

  useEffect(() => {
    api.get("/goals", { params: { status: "ativa" } }).then((res) => setGoals(res.data));
  }, []);

  const displayed = goals.slice(0, 3);

  if (displayed.length === 0) return null;

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border card-hover">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold">Metas</h3>
        <Link href="/goals" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          Ver todas &#8250;
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {displayed.map((g) => {
          const pct = g.target_amount > 0 ? Math.min((g.saved_amount / g.target_amount) * 100, 100) : 0;
          return (
            <div key={g.id} className="rounded-lg p-3 bg-[#0f1825] border border-border">
              <div className="flex justify-between items-center">
                <p className="text-sm font-medium">{g.name}</p>
                <span className="text-xs text-muted-foreground">{pct.toFixed(0)}%</span>
              </div>
              <div className="w-full h-1 bg-border rounded-full mt-2 overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#60a5fa] transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                R$ {fmt(g.saved_amount)} / R$ {fmt(g.target_amount)}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
