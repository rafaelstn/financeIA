"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Clock, AlertTriangle, Wallet, PiggyBank, ShoppingCart, Banknote } from "lucide-react";

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

const CATEGORY_ICONS: Record<string, typeof Wallet> = {
  dividas: AlertTriangle,
  reserva: PiggyBank,
  custo_vida: ShoppingCart,
  sobra: Banknote,
};

const CATEGORY_COLORS: Record<string, string> = {
  dividas: "text-red-500",
  reserva: "text-blue-500",
  custo_vida: "text-amber-500",
  sobra: "text-emerald-500",
};

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  planejado: { label: "Planejado", color: "bg-blue-500/20 text-blue-400" },
  em_andamento: { label: "Em andamento", color: "bg-amber-500/20 text-amber-400" },
  concluido: { label: "Concluído", color: "bg-emerald-500/20 text-emerald-400" },
};

export default function PlanView({ plan }: { plan: Plan }) {
  const statusCfg = STATUS_CONFIG[plan.status] || STATUS_CONFIG.planejado;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">{plan.title}</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${statusCfg.color}`}>
          {statusCfg.label}
        </span>
      </div>

      {plan.content.sections?.map((section) => {
        const Icon = CATEGORY_ICONS[section.category] || Wallet;
        const color = CATEGORY_COLORS[section.category] || "text-gray-500";

        return (
          <Card key={section.category}>
            <CardHeader className="flex flex-row items-center gap-3 pb-2">
              <Icon className={`h-5 w-5 ${color}`} />
              <CardTitle className="text-sm font-medium">{section.title}</CardTitle>
              <span className={`ml-auto text-lg font-bold ${color}`}>
                R$ {section.total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {section.items.map((item, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div>
                      <span>{item.description}</span>
                      {item.notes && (
                        <p className="text-xs text-muted-foreground">{item.notes}</p>
                      )}
                    </div>
                    <span className="font-medium">
                      R$ {item.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        );
      })}

      {plan.observations && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Observações</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">{plan.observations}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
