"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";

const STATUSES: Record<string, string> = {
  ativa: "Ativa",
  negociando: "Negociando",
  acordo: "Em Acordo",
  quitada: "Quitada",
  prescrita: "Prescrita",
};

interface Debt {
  id: string;
  creditor: string;
  current_amount: number;
  status: string;
}

export default function DebtsOverview() {
  const [debts, setDebts] = useState<Debt[]>([]);

  useEffect(() => {
    api.get("/debts").then((res) => setDebts(res.data.data || res.data));
  }, []);

  const activeDebts = debts.filter((d) => ["ativa", "negociando"].includes(d.status));
  const activeTotal = activeDebts.reduce((s, d) => s + d.current_amount, 0);
  const agreementCount = debts.filter((d) => d.status === "acordo").length;

  const topDebts = [...activeDebts]
    .sort((a, b) => b.current_amount - a.current_amount)
    .slice(0, 3);

  if (debts.length === 0) return null;

  const statusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      ativa: "destructive",
      negociando: "outline",
      acordo: "secondary",
      quitada: "default",
      prescrita: "secondary",
    };
    const colors: Record<string, string> = {
      negociando: "border-yellow-500 text-yellow-600",
      acordo: "border-blue-500 text-blue-600 bg-blue-50",
      quitada: "bg-emerald-600",
      prescrita: "border-gray-400 text-gray-500",
    };
    return (
      <Badge variant={variants[status] || "secondary"} className={colors[status] || ""}>
        {STATUSES[status] || status}
      </Badge>
    );
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          Visao Geral de Dividas
        </CardTitle>
        <Link href="/debts" className="text-sm text-blue-500 hover:underline">
          Ver todas
        </Link>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 rounded-lg border">
            <p className="text-2xl font-bold text-red-500">{activeDebts.length}</p>
            <p className="text-xs text-muted-foreground">Dividas Ativas</p>
          </div>
          <div className="text-center p-3 rounded-lg border">
            <p className="text-lg font-bold text-red-500">
              R$ {activeTotal.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </p>
            <p className="text-xs text-muted-foreground">Valor Total</p>
          </div>
          <div className="text-center p-3 rounded-lg border">
            <p className="text-2xl font-bold text-blue-500">{agreementCount}</p>
            <p className="text-xs text-muted-foreground">Em Acordo</p>
          </div>
        </div>
        {topDebts.length > 0 && (
          <div className="space-y-2">
            {topDebts.map((d) => (
              <div key={d.id} className="flex items-center justify-between p-2 rounded-lg border">
                <span className="text-sm font-medium truncate">{d.creditor}</span>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-red-500 font-medium">
                    R$ {d.current_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                  {statusBadge(d.status)}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
