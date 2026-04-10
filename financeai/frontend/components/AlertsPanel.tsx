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

const LEVEL_STYLES: Record<string, { bg: string; border: string; text: string }> = {
  danger: { bg: "rgba(248,113,113,0.08)", border: "#f87171", text: "#fca5a5" },
  warning: { bg: "rgba(251,191,36,0.06)", border: "#fbbf24", text: "#fde68a" },
  info: { bg: "rgba(96,165,250,0.06)", border: "#60a5fa", text: "#93c5fd" },
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
      <h3 className="text-sm font-semibold mb-3">Alertas</h3>
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
                style={{ background: style.bg, borderLeft: `3px solid ${style.border}` }}
              >
                <p className="text-xs font-semibold" style={{ color: style.text }}>{alert.message}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
