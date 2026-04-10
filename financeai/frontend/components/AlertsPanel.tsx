"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface Alert {
  id: string;
  message: string;
  level: string;
  due_date: string | null;
  amount: number | null;
  source: string;
}

const LEVEL_STYLES: Record<string, { bgVar: string; borderVar: string; textVar: string }> = {
  danger: { bgVar: "var(--status-overdue-bg)", borderVar: "var(--accent-red)", textVar: "var(--status-overdue-text)" },
  warning: { bgVar: "var(--status-pending-bg)", borderVar: "var(--accent-amber)", textVar: "var(--status-pending-text)" },
  info: { bgVar: "var(--status-info-bg)", borderVar: "var(--primary)", textVar: "var(--status-info-text)" },
};

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/alerts").then((res) => setAlerts(res.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="rounded-[10px] p-4 bg-card border border-border">
      <div className="h-4 w-24 bg-muted animate-pulse rounded mb-4" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-14 bg-muted animate-pulse rounded mb-2" />
      ))}
    </div>
  );

  const displayed = alerts.slice(0, 5);

  return (
    <div className="rounded-[10px] p-4 bg-card border border-border card-hover">
      <h3 className="text-base font-semibold mb-3">Alertas</h3>
      {displayed.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhum alerta ativo</p>
      ) : (
        <div className="space-y-2">
          {displayed.map((alert) => {
            const style = LEVEL_STYLES[alert.level] || LEVEL_STYLES.info;
            return (
              <div
                key={alert.id}
                className="p-3 rounded-lg"
                style={{ background: style.bgVar, borderLeft: `3px solid ${style.borderVar}` }}
              >
                <p className="text-sm font-semibold" style={{ color: style.textVar }}>{alert.message}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
