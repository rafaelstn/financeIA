"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ClipboardList, AlertTriangle, PiggyBank, ShoppingCart, Banknote, Wallet } from "lucide-react";
import api from "@/lib/api";

interface PlanItem {
  description: string;
  amount: number;
}

interface PlanSection {
  category: string;
  title: string;
  items: PlanItem[];
  total: number;
}

interface Plan {
  id: string;
  title: string;
  content: { sections: PlanSection[] };
  status: string;
  observations: string | null;
}

const CATEGORY_ICONS: Record<string, typeof Wallet> = {
  dividas: AlertTriangle,
  reserva: PiggyBank,
  custo_vida: ShoppingCart,
  sobra: Banknote,
};

const STATUS_LABELS: Record<string, { label: string; color: string; bg: string }> = {
  planejado: { label: "Planejado", color: "var(--status-info-text)", bg: "var(--status-info-bg)" },
  em_andamento: { label: "Em andamento", color: "var(--status-pending-text)", bg: "var(--status-pending-bg)" },
  concluido: { label: "Concluido", color: "var(--status-paid-text)", bg: "var(--status-paid-bg)" },
};

interface Props {
  month: number;
  year: number;
}

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

export default function PlanSummary({ month, year }: Props) {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    api.get(`/plans/${month}/${year}`)
      .then((res) => setPlan(res.data))
      .catch(() => {
        setPlan(null);
        setNotFound(true);
      })
      .finally(() => setLoading(false));
  }, [month, year]);

  if (loading) return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <div className="h-5 w-48 bg-muted animate-pulse rounded mb-4" />
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-10 bg-muted animate-pulse rounded" />
        ))}
      </div>
    </div>
  );

  // Sem plano — CTA pra criar
  if (notFound || !plan) {
    return (
      <div className="rounded-[10px] p-6 bg-card border border-border card-hover text-center">
        <ClipboardList className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
        <h3 className="text-base font-semibold mb-1">Sem planejamento este mes</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Crie um plano financeiro para organizar suas despesas, dividas e metas do mes.
        </p>
        <Link
          href="/planning"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
        >
          <ClipboardList className="h-4 w-4" />
          Criar planejamento
        </Link>
      </div>
    );
  }

  // Tem plano — mostra resumo
  const sections = plan.content?.sections || [];
  const totalPlan = sections.reduce((sum, s) => sum + s.total, 0);
  const status = STATUS_LABELS[plan.status] || STATUS_LABELS.planejado;

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border card-hover">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <ClipboardList className="h-4 w-4 text-primary" />
          <h3 className="text-base font-semibold">Planejamento</h3>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="text-xs font-medium px-2 py-0.5 rounded-full"
            style={{ color: status.color, background: status.bg }}
          >
            {status.label}
          </span>
          <Link href="/planning" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
            Editar &#8250;
          </Link>
        </div>
      </div>

      {/* Titulo do plano */}
      <p className="text-sm font-medium mb-3">{plan.title}</p>

      {/* Seções resumidas */}
      <div className="space-y-2">
        {sections.map((section) => {
          const Icon = CATEGORY_ICONS[section.category] || Wallet;
          return (
            <div
              key={section.category}
              className="flex items-center justify-between py-2 border-b border-border/50 last:border-0"
            >
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">{section.title}</span>
                <span className="text-xs text-muted-foreground">({section.items.length} itens)</span>
              </div>
              <span className="text-sm font-semibold">R$ {fmt(section.total)}</span>
            </div>
          );
        })}
      </div>

      {/* Total */}
      {sections.length > 0 && (
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
          <span className="text-sm font-semibold">Total planejado</span>
          <span className="text-base font-bold text-primary">R$ {fmt(totalPlan)}</span>
        </div>
      )}
    </div>
  );
}
