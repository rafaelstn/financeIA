"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Circle, AlertTriangle, PiggyBank, ShoppingCart, Banknote, Wallet, Trophy } from "lucide-react";
import api from "@/lib/api";

interface PlanItem {
  description: string;
  amount: number;
  notes?: string;
}

interface PlanSection {
  category: string;
  title: string;
  items: PlanItem[];
  total: number;
}

interface Plan {
  id: string;
  month: number;
  year: number;
  title: string;
  content: { sections: PlanSection[] };
  observations: string | null;
  status: string;
}

interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: string;
  category: string;
  status: string;
  due_date: string;
}

const CATEGORY_ICONS: Record<string, typeof Wallet> = {
  dividas: AlertTriangle,
  reserva: PiggyBank,
  custo_vida: ShoppingCart,
  sobra: Banknote,
};

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

function matchTransaction(item: PlanItem, transactions: Transaction[]): Transaction | null {
  // Try exact description match
  const desc = item.description.toLowerCase().replace(/[^a-z0-9]/g, "");
  for (const t of transactions) {
    const tDesc = t.description.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (tDesc === desc || tDesc.includes(desc) || desc.includes(tDesc)) {
      return t;
    }
  }
  // Try partial match for common items
  const keywords = item.description.toLowerCase().split(/[\s-]+/).filter(w => w.length > 3);
  for (const t of transactions) {
    const tLower = t.description.toLowerCase();
    if (keywords.some(k => tLower.includes(k))) {
      return t;
    }
  }
  return null;
}

export default function PlanView({ plan }: { plan: Plan }) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/transactions", { params: { month: plan.month, year: plan.year, per_page: 100 } })
      .then((res) => setTransactions(res.data.data || res.data))
      .finally(() => setLoading(false));
  }, [plan.month, plan.year]);

  const sections = plan.content?.sections || [];

  // Calculate overall progress
  let totalItems = 0;
  let completedItems = 0;
  const sectionStats: Record<string, { total: number; done: number }> = {};

  for (const section of sections) {
    let done = 0;
    for (const item of section.items) {
      totalItems++;
      const match = matchTransaction(item, transactions);
      if (match && match.status === "paid") {
        completedItems++;
        done++;
      }
    }
    sectionStats[section.category] = { total: section.items.length, done };
  }

  const progressPct = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;

  return (
    <div className="space-y-4">
      {/* Header with progress */}
      <div className="rounded-[10px] p-5 bg-card border border-border">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold">{plan.title}</h3>
            <p className="text-sm text-muted-foreground mt-0.5">
              {completedItems} de {totalItems} itens concluidos
            </p>
          </div>
          <div className="flex items-center gap-3">
            {progressPct === 100 && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold"
                style={{ color: "var(--status-paid-text)", background: "var(--status-paid-bg)" }}>
                <Trophy className="h-4 w-4" />
                Concluido!
              </div>
            )}
            <div className="text-2xl font-bold" style={{ color: progressPct === 100 ? "var(--accent-green)" : "var(--primary)" }}>
              {progressPct}%
            </div>
          </div>
        </div>
        {/* Progress bar */}
        <div className="w-full h-2.5 rounded-full overflow-hidden" style={{ background: "var(--card-inner)" }}>
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progressPct}%`,
              background: progressPct === 100 ? "var(--accent-green)" : "var(--primary)",
            }}
          />
        </div>
      </div>

      {/* Sections */}
      {sections.map((section) => {
        const Icon = CATEGORY_ICONS[section.category] || Wallet;
        const stats = sectionStats[section.category] || { total: 0, done: 0 };
        const sectionPct = stats.total > 0 ? Math.round((stats.done / stats.total) * 100) : 0;

        return (
          <div key={section.category} className="rounded-[10px] bg-card border border-border overflow-hidden">
            {/* Section header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-3">
                <Icon className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h4 className="text-sm font-semibold">{section.title}</h4>
                  <p className="text-xs text-muted-foreground">{stats.done}/{stats.total} concluidos</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-base font-bold">R$ {fmt(section.total)}</p>
                <div className="w-20 h-1.5 rounded-full mt-1" style={{ background: "var(--card-inner)" }}>
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${sectionPct}%`,
                      background: sectionPct === 100 ? "var(--accent-green)" : "var(--primary)",
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Items */}
            <div className="divide-y" style={{ borderColor: "var(--card-inner)" }}>
              {section.items.map((item, i) => {
                const match = matchTransaction(item, transactions);
                const isPaid = match?.status === "paid";
                const isOverdue = match?.status === "overdue";
                const isPending = match?.status === "pending";

                return (
                  <div
                    key={i}
                    className={`flex items-center gap-3 px-4 py-3 transition-all ${isPaid ? "opacity-60" : ""}`}
                  >
                    {/* Status icon */}
                    {isPaid ? (
                      <CheckCircle2 className="h-5 w-5 flex-shrink-0" style={{ color: "var(--accent-green)" }} />
                    ) : isOverdue ? (
                      <AlertTriangle className="h-5 w-5 flex-shrink-0" style={{ color: "var(--accent-red)" }} />
                    ) : (
                      <Circle className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                    )}

                    {/* Description */}
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm ${isPaid ? "line-through text-muted-foreground" : ""}`}>
                        {item.description}
                      </p>
                      {item.notes && (
                        <p className="text-xs text-muted-foreground truncate">{item.notes}</p>
                      )}
                    </div>

                    {/* Amount + status */}
                    <div className="text-right flex-shrink-0">
                      <p className={`text-sm font-semibold ${isPaid ? "text-muted-foreground line-through" : ""}`}>
                        R$ {fmt(item.amount)}
                      </p>
                      {isPaid && (
                        <span className="text-[10px] font-medium" style={{ color: "var(--status-paid-text)" }}>Pago</span>
                      )}
                      {isOverdue && (
                        <span className="text-[10px] font-medium" style={{ color: "var(--status-overdue-text)" }}>Atrasado</span>
                      )}
                      {isPending && (
                        <span className="text-[10px] font-medium" style={{ color: "var(--status-pending-text)" }}>Pendente</span>
                      )}
                      {!match && section.category !== "sobra" && section.category !== "reserva" && (
                        <span className="text-[10px] text-muted-foreground">Sem registro</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
