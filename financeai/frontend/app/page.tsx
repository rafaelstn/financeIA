"use client";

import { useEffect, useRef, useState } from "react";
import SummaryCards from "@/components/SummaryCards";
import SpendingChart from "@/components/SpendingChart";
import GoalsProgress from "@/components/GoalsProgress";
import UpcomingBills from "@/components/UpcomingBills";
import AlertsPanel from "@/components/AlertsPanel";
import PlanSummary from "@/components/PlanSummary";
import api from "@/lib/api";

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function Dashboard() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const generatedRef = useRef(false);

  // Auto-generate recurring transactions on first load (once per session)
  useEffect(() => {
    if (generatedRef.current) return;
    generatedRef.current = true;
    api.post("/recurring/generate").catch(() => {});
  }, []);

  function prev() {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  }

  function next() {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  }

  return (
    <div className="space-y-4 w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Dashboard Financeiro</h2>
          <p className="text-sm text-muted-foreground">Visao geral financeira</p>
        </div>
        <div className="flex gap-px bg-secondary rounded-md overflow-hidden border border-border">
          <button onClick={prev} className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
            &#8249; {MONTH_NAMES[month === 1 ? 11 : month - 2]?.slice(0, 3)}
          </button>
          <div className="px-4 py-1.5 text-sm font-semibold bg-accent">
            {MONTH_NAMES[month - 1]} {year}
          </div>
          <button onClick={next} className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
            {MONTH_NAMES[month === 12 ? 0 : month]?.slice(0, 3)} &#8250;
          </button>
        </div>
      </div>

      {/* Row 1-2: Summary Cards */}
      <SummaryCards month={month} year={year} />

      {/* Row 3: Charts */}
      <SpendingChart month={month} year={year} />

      {/* Row 4: Upcoming + Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <UpcomingBills />
        <AlertsPanel />
      </div>

      {/* Row 5: Plan Summary */}
      <PlanSummary month={month} year={year} />

      {/* Row 6: Goals */}
      <GoalsProgress />
    </div>
  );
}
