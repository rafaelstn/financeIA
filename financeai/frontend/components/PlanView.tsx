"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Circle, AlertTriangle, PiggyBank, ShoppingCart, Banknote, Wallet, Trophy, Target, TrendingDown, Shield, Flame } from "lucide-react";
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
  dividas: TrendingDown,
  reserva: Shield,
  custo_vida: ShoppingCart,
  sobra: Banknote,
};

const CATEGORY_COMMENTARY: Record<string, { emoji: string; why: string; tip: string }> = {
  custo_vida: {
    emoji: "🏠",
    why: "Suas despesas fixas sao a base. Pagar tudo em dia evita multas e mantem sua credibilidade financeira.",
    tip: "Dica: pague as contas assim que o salario cair. O dinheiro que fica na conta some rapido.",
  },
  dividas: {
    emoji: "⚔️",
    why: "Cada divida quitada e uma corrente a menos. Estamos usando o metodo bola de neve: quitando as menores primeiro pra ganhar momentum.",
    tip: "Negocie sempre! No Serasa, descontos de 40-80% sao comuns. Ligue antes de pagar o valor cheio.",
  },
  reserva: {
    emoji: "🛡️",
    why: "A reserva de emergencia e o que separa voce de uma nova divida. Sem ela, qualquer imprevisto vira cartao de credito.",
    tip: "Coloque num CDB com liquidez diaria. Rende mais que poupanca e voce saca quando precisar.",
  },
  sobra: {
    emoji: "🎯",
    why: "Voce merece viver bem enquanto organiza as financas. Essa sobra e pra voce — lazer, desejos, imprevistos.",
    tip: "Nao se culpe por gastar com voce. O plano ja separou o necessario. Essa parte e livre.",
  },
};

const MONTH_NAMES = [
  "", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

function fmt(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
}

function matchTransaction(item: PlanItem, transactions: Transaction[]): Transaction | null {
  const desc = item.description.toLowerCase().replace(/[^a-z0-9]/g, "");
  for (const t of transactions) {
    const tDesc = t.description.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (tDesc === desc || tDesc.includes(desc) || desc.includes(tDesc)) {
      return t;
    }
  }
  const keywords = item.description.toLowerCase().split(/[\s-]+/).filter(w => w.length > 3);
  for (const t of transactions) {
    const tLower = t.description.toLowerCase();
    if (keywords.some(k => tLower.includes(k))) {
      return t;
    }
  }
  return null;
}

function getMotivationalMessage(pct: number): { text: string; sub: string } {
  if (pct === 100) return { text: "Mes concluido! Voce e imparavel.", sub: "Cada mes assim te aproxima da liberdade financeira." };
  if (pct >= 80) return { text: "Quase la! Falta pouco.", sub: "Voce ja provou que consegue. Termina esse mes forte." };
  if (pct >= 60) return { text: "Mais da metade feito!", sub: "O progresso e real. Continue no ritmo." };
  if (pct >= 40) return { text: "Bom progresso!", sub: "Cada conta paga e uma vitoria. Nao para." };
  if (pct >= 20) return { text: "Comecou bem!", sub: "O primeiro passo e o mais dificil. Voce ja deu." };
  return { text: "Hora de comecar!", sub: "Abra o mes pagando as primeiras contas. O momentum vem." };
}

export default function PlanView({ plan }: { plan: Plan }) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  useEffect(() => {
    api.get("/transactions", { params: { month: plan.month, year: plan.year, per_page: 100 } })
      .then((res) => setTransactions(res.data.data || res.data))
      .finally(() => setLoading(false));
  }, [plan.month, plan.year]);

  const sections = plan.content?.sections || [];

  // Calculate stats
  let totalItems = 0;
  let completedItems = 0;
  const sectionStats: Record<string, { total: number; done: number; paidAmount: number }> = {};

  for (const section of sections) {
    let done = 0;
    let paidAmount = 0;
    for (const item of section.items) {
      totalItems++;
      const match = matchTransaction(item, transactions);
      if (match && match.status === "paid") {
        completedItems++;
        done++;
        paidAmount += match.amount;
      }
    }
    sectionStats[section.category] = { total: section.items.length, done, paidAmount };
  }

  const progressPct = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
  const motivation = getMotivationalMessage(progressPct);

  // Calculate debt reduction this cycle
  const debtSection = sections.find(s => s.category === "dividas");
  const debtTotal = debtSection?.total || 0;
  const debtPaid = sectionStats.dividas?.paidAmount || 0;

  // Calculate future vision
  const reserveSection = sections.find(s => s.category === "reserva");
  const reserveTarget = reserveSection?.total || 0;

  return (
    <div className="space-y-4">
      {/* Hero: Vision + Progress */}
      <div className="rounded-xl p-6 border border-border relative overflow-hidden"
        style={{ background: "linear-gradient(135deg, var(--card), var(--card-inner, var(--card)))" }}>

        {/* Motivational header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className="text-xs uppercase tracking-widest text-muted-foreground mb-1">
              {MONTH_NAMES[plan.month]} {plan.year} — Missao do Mes
            </p>
            <h3 className="text-xl font-bold">{plan.title.replace(/^Ciclo \d+ - \w+\/\d+ - /, "")}</h3>
            <p className="text-sm text-muted-foreground mt-1">{plan.observations || motivation.sub}</p>
          </div>
          <div className="text-right ml-4">
            <div className="text-3xl font-bold" style={{ color: progressPct === 100 ? "var(--accent-green)" : "var(--primary)" }}>
              {progressPct}%
            </div>
            <p className="text-xs text-muted-foreground">{completedItems}/{totalItems} missoes</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full h-3 rounded-full overflow-hidden" style={{ background: "var(--card-inner, rgba(0,0,0,0.2))" }}>
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${progressPct}%`,
              background: progressPct === 100
                ? "var(--accent-green)"
                : `linear-gradient(90deg, var(--primary), var(--accent-purple, var(--primary)))`,
            }}
          />
        </div>

        {/* Motivational message */}
        <p className="text-sm font-medium mt-3" style={{ color: progressPct === 100 ? "var(--accent-green)" : "var(--primary)" }}>
          {progressPct === 100 ? "🏆 " : progressPct >= 60 ? "🔥 " : "💪 "}
          {motivation.text}
        </p>
      </div>

      {/* Vision cards: what this month achieves */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {debtTotal > 0 && (
          <div className="rounded-[10px] p-4 bg-card border border-border">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="h-4 w-4" style={{ color: "var(--accent-red)" }} />
              <span className="text-xs uppercase tracking-wide text-muted-foreground">Dividas este mes</span>
            </div>
            <p className="text-lg font-bold">R$ {fmt(debtTotal)}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {debtPaid > 0 ? `R$ ${fmt(debtPaid)} ja pago` : "Negocie antes de pagar"}
            </p>
          </div>
        )}
        {reserveTarget > 0 && (
          <div className="rounded-[10px] p-4 bg-card border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-4 w-4" style={{ color: "var(--primary)" }} />
              <span className="text-xs uppercase tracking-wide text-muted-foreground">Reserva este mes</span>
            </div>
            <p className="text-lg font-bold">R$ {fmt(reserveTarget)}</p>
            <p className="text-xs text-muted-foreground mt-1">Seu escudo contra imprevistos</p>
          </div>
        )}
        <div className="rounded-[10px] p-4 bg-card border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-4 w-4" style={{ color: "var(--accent-green)" }} />
            <span className="text-xs uppercase tracking-wide text-muted-foreground">Ao final do mes</span>
          </div>
          <p className="text-lg font-bold" style={{ color: "var(--accent-green)" }}>
            {debtSection ? `${debtSection.items.filter(i => i.description.includes("QUITAR")).length} dividas a menos` : "Contas em dia"}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Cada mes e um passo pra frente</p>
        </div>
      </div>

      {/* Sections with commentary */}
      {sections.map((section) => {
        const Icon = CATEGORY_ICONS[section.category] || Wallet;
        const stats = sectionStats[section.category] || { total: 0, done: 0, paidAmount: 0 };
        const sectionPct = stats.total > 0 ? Math.round((stats.done / stats.total) * 100) : 0;
        const commentary = CATEGORY_COMMENTARY[section.category];
        const isExpanded = expandedSection === section.category;

        return (
          <div key={section.category} className="rounded-[10px] bg-card border border-border overflow-hidden">
            {/* Section header - clickable */}
            <button
              className="w-full flex items-center justify-between p-4 border-b border-border hover:bg-accent/30 transition-colors"
              onClick={() => setExpandedSection(isExpanded ? null : section.category)}
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg flex items-center justify-center text-lg"
                  style={{ background: "var(--card-inner, rgba(0,0,0,0.1))" }}>
                  {commentary?.emoji || "📋"}
                </div>
                <div className="text-left">
                  <h4 className="text-sm font-semibold">{section.title}</h4>
                  <p className="text-xs text-muted-foreground">
                    {stats.done === stats.total && stats.total > 0
                      ? "✅ Tudo concluido!"
                      : `${stats.done}/${stats.total} concluidos`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-base font-bold">R$ {fmt(section.total)}</p>
                  <div className="w-20 h-1.5 rounded-full mt-1" style={{ background: "var(--card-inner, rgba(0,0,0,0.2))" }}>
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${sectionPct}%`,
                        background: sectionPct === 100 ? "var(--accent-green)" : "var(--primary)",
                      }}
                    />
                  </div>
                </div>
                <span className="text-muted-foreground text-sm">{isExpanded ? "▲" : "▼"}</span>
              </div>
            </button>

            {/* Commentary */}
            {isExpanded && commentary && (
              <div className="px-4 py-3 border-b border-border" style={{ background: "var(--card-inner, rgba(0,0,0,0.05))" }}>
                <p className="text-sm">{commentary.why}</p>
                <p className="text-xs text-muted-foreground mt-1.5">💡 {commentary.tip}</p>
              </div>
            )}

            {/* Items */}
            {isExpanded && (
              <div className="divide-y" style={{ borderColor: "var(--card-inner, var(--border))" }}>
                {section.items.map((item, i) => {
                  const match = matchTransaction(item, transactions);
                  const isPaid = match?.status === "paid";
                  const isOverdue = match?.status === "overdue";
                  const isPending = match?.status === "pending";

                  return (
                    <div
                      key={i}
                      className={`flex items-center gap-3 px-4 py-3 transition-all ${isPaid ? "opacity-50" : ""}`}
                    >
                      {isPaid ? (
                        <CheckCircle2 className="h-5 w-5 flex-shrink-0" style={{ color: "var(--accent-green)" }} />
                      ) : isOverdue ? (
                        <AlertTriangle className="h-5 w-5 flex-shrink-0" style={{ color: "var(--accent-red)" }} />
                      ) : (
                        <Circle className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                      )}

                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${isPaid ? "line-through text-muted-foreground" : ""}`}>
                          {item.description}
                        </p>
                        {item.notes && (
                          <p className="text-xs text-muted-foreground truncate">{item.notes}</p>
                        )}
                      </div>

                      <div className="text-right flex-shrink-0">
                        <p className={`text-sm font-semibold ${isPaid ? "text-muted-foreground line-through" : ""}`}>
                          R$ {fmt(item.amount)}
                        </p>
                        {isPaid && <span className="text-[10px] font-medium" style={{ color: "var(--status-paid-text)" }}>Pago</span>}
                        {isOverdue && <span className="text-[10px] font-medium" style={{ color: "var(--status-overdue-text)" }}>Atrasado</span>}
                        {isPending && <span className="text-[10px] font-medium" style={{ color: "var(--status-pending-text)" }}>Pendente</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Collapsed summary */}
            {!isExpanded && (
              <div className="px-4 py-2 flex gap-1 flex-wrap">
                {section.items.map((item, i) => {
                  const match = matchTransaction(item, transactions);
                  const isPaid = match?.status === "paid";
                  return (
                    <div
                      key={i}
                      className="h-2 flex-1 min-w-[20px] rounded-full"
                      title={`${item.description}: R$ ${fmt(item.amount)} - ${isPaid ? "Pago" : "Pendente"}`}
                      style={{
                        background: isPaid ? "var(--accent-green)" : "var(--card-inner, rgba(0,0,0,0.2))",
                      }}
                    />
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
