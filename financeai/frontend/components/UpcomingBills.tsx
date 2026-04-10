"use client";

import { useEffect, useState } from "react";
import { formatDate } from "@/lib/utils";
import api from "@/lib/api";

interface Bill {
  description: string;
  amount: number;
  due_date: string;
  days_until: number;
  status: string;
}

export default function UpcomingBills() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/summary/upcoming")
      .then((res) => setBills(res.data.upcoming || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <div className="h-4 w-40 bg-muted animate-pulse rounded mb-4" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-8 bg-muted animate-pulse rounded mb-2" />
      ))}
    </div>
  );

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border card-hover">
      <h3 className="text-sm font-semibold mb-3">Proximos vencimentos</h3>
      {bills.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhuma conta proxima</p>
      ) : (
        <div>
          {/* Header */}
          <div className="grid grid-cols-[1fr_auto_auto] gap-2 pb-2 border-b border-border mb-1">
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">Conta</span>
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">Vence</span>
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground text-right">Valor</span>
          </div>
          {bills.slice(0, 6).map((bill, i) => (
            <div key={i} className="grid grid-cols-[1fr_auto_auto] gap-2 py-2 border-b border-[#0f1825] last:border-0 items-center">
              <div>
                <p className="text-sm">{bill.description}</p>
                {bill.status === "overdue" && (
                  <span className="text-[10px] text-[#fca5a5]">Atrasada</span>
                )}
              </div>
              <span className="text-sm text-muted-foreground">{formatDate(bill.due_date)}</span>
              <span className="text-sm font-semibold text-right">
                R$ {bill.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
