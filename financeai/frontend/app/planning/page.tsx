"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Trash2, ChevronLeft, ChevronRight, ClipboardList } from "lucide-react";
import ReactMarkdown from "react-markdown";
import PlanView from "@/components/PlanView";
import PlanComparison from "@/components/PlanComparison";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface Plan {
  id: string;
  month: number;
  year: number;
  title: string;
  content: { sections: any[] };
  observations: string | null;
  status: string;
}

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function PlanningPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [plan, setPlan] = useState<Plan | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loadingPlan, setLoadingPlan] = useState(true);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const timestamp = () => new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

  // Load plan for selected month
  useEffect(() => {
    setLoadingPlan(true);
    api.get(`/plans/${month}/${year}`)
      .then((res) => setPlan(res.data))
      .catch(() => setPlan(null))
      .finally(() => setLoadingPlan(false));
  }, [month, year]);

  // Load all plans for history
  useEffect(() => {
    api.get("/plans").then((res) => setPlans(res.data)).catch(() => setPlans([]));
  }, [plan]);

  // Chat scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function prev() {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  }

  function next() {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  }

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", content: input.trim(), timestamp: timestamp() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/chat/", { message: userMsg.content, history: messages });
      setMessages([...updated, { role: "assistant", content: res.data.response, timestamp: timestamp() }]);
      // Refresh plan after AI response (might have saved a new plan)
      api.get(`/plans/${month}/${year}`)
        .then((r) => setPlan(r.data))
        .catch(() => setPlan(null));
    } catch {
      setMessages([...updated, { role: "assistant", content: "Erro ao conectar com a IA. Tente novamente.", timestamp: timestamp() }]);
    } finally {
      setLoading(false);
    }
  };

  // Save observations
  const saveObservations = async (obs: string) => {
    if (!plan) return;
    await api.put(`/plans/${plan.id}`, { observations: obs });
    setPlan({ ...plan, observations: obs });
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-2rem)]">
      {/* Main area - Plan */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Planejamento Financeiro</h2>
          <div className="flex items-center gap-3">
            <button onClick={prev} className="p-2 rounded-lg hover:bg-muted transition-colors">
              <ChevronLeft className="h-5 w-5" />
            </button>
            <span className="text-lg font-semibold min-w-[180px] text-center">
              {MONTH_NAMES[month - 1]} {year}
            </span>
            <button onClick={next} className="p-2 rounded-lg hover:bg-muted transition-colors">
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>

        {loadingPlan ? (
          <Card>
            <CardContent className="p-6">
              <div className="h-64 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ) : plan ? (
          <>
            <PlanView plan={plan} />
            <PlanComparison month={month} year={year} />

            {/* Observations */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Suas Observações</CardTitle>
              </CardHeader>
              <CardContent>
                <textarea
                  className="w-full bg-transparent border border-border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-ring"
                  rows={3}
                  placeholder="Anote o que aconteceu de diferente neste mês..."
                  defaultValue={plan.observations || ""}
                  onBlur={(e) => saveObservations(e.target.value)}
                />
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <ClipboardList className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                Nenhum plano para {MONTH_NAMES[month - 1]}/{year}.
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Use o chat ao lado para pedir à IA que crie seu planejamento.
              </p>
            </CardContent>
          </Card>
        )}

        {/* History */}
        {plans.length > 0 && (
          <div className="rounded-[10px] p-4 bg-card border border-border">
            <h3 className="text-base font-semibold mb-3">Ciclos de Planejamento</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[...plans].sort((a, b) => a.year === b.year ? a.month - b.month : a.year - b.year).map((p) => {
                const isActive = p.month === month && p.year === year;
                const statusCfg = p.status === "concluido"
                  ? { label: "Concluído", style: { color: "var(--status-paid-text)", background: "var(--status-paid-bg)" } }
                  : p.status === "em_andamento"
                  ? { label: "Em andamento", style: { color: "var(--status-pending-text)", background: "var(--status-pending-bg)" } }
                  : { label: "Planejado", style: { color: "var(--status-info-text)", background: "var(--status-info-bg)" } };

                // Calculate total from sections
                const total = p.content?.sections?.reduce((s: number, sec: { total: number }) => s + sec.total, 0) || 0;

                return (
                  <button
                    key={p.id}
                    onClick={() => { setMonth(p.month); setYear(p.year); }}
                    className={`text-left p-4 rounded-lg border transition-all ${
                      isActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs text-muted-foreground">
                        {MONTH_NAMES[p.month - 1]} {p.year}
                      </span>
                      <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-full" style={statusCfg.style}>
                        {statusCfg.label}
                      </span>
                    </div>
                    <p className="text-sm font-semibold mb-1 line-clamp-1">{p.title.replace(/^Ciclo \d+ - \w+\/\d+ - /, '')}</p>
                    {p.content?.sections && (
                      <div className="space-y-1 mt-2">
                        {p.content.sections.map((sec: { category: string; title: string; total: number }) => (
                          <div key={sec.category} className="flex justify-between text-xs">
                            <span className="text-muted-foreground">{sec.title.split(' - ')[0]}</span>
                            <span className="font-medium">R$ {sec.total.toLocaleString("pt-BR", { minimumFractionDigits: 0 })}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Sidebar - Chat */}
      <div className="w-[380px] flex flex-col border-l border-border bg-card rounded-lg">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h3 className="font-semibold text-sm">Chat de Planejamento</h3>
          <Button variant="ghost" size="icon" onClick={() => setMessages([])}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <p className="text-sm text-muted-foreground text-center mt-8">
              Peça para a IA criar seu planejamento financeiro!
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose prose-sm prose-invert max-w-none [&>p]:m-0 [&>ul]:m-0 [&>ol]:m-0">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>
              <span className="text-xs text-muted-foreground mt-1">{msg.timestamp}</span>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-3 py-2 text-sm text-muted-foreground">
                Digitando...
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Peça um planejamento..."
            disabled={loading}
          />
          <Button size="icon" onClick={send} disabled={loading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
