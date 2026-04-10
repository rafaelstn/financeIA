"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Plus, Trash2, Pencil, PiggyBank, Target } from "lucide-react";
import PageHelp from "@/components/PageHelp";
import { helpContent } from "@/lib/help-content";
import api from "@/lib/api";
import { toast } from "sonner";

const CATEGORIES: Record<string, string> = {
  eletronico: "Eletrônico",
  veiculo: "Veículo",
  imovel: "Imóvel",
  viagem: "Viagem",
  educacao: "Educação",
  saude: "Saúde",
  lazer: "Lazer",
  outros: "Outros",
};

const PRIORITIES: Record<string, string> = {
  alta: "Alta",
  media: "Média",
  baixa: "Baixa",
};

const STATUSES: Record<string, string> = {
  ativa: "Ativa",
  pausada: "Pausada",
  concluida: "Concluída",
  cancelada: "Cancelada",
};

interface Goal {
  id: string;
  name: string;
  target_amount: number;
  saved_amount: number;
  priority: string;
  category: string;
  status: string;
  target_date: string | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
}

const defaultForm = {
  name: "",
  target_amount: "",
  saved_amount: "0",
  priority: "media",
  category: "outros",
  status: "ativa",
  target_date: "",
  notes: "",
};

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...defaultForm });
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [savingGoalId, setSavingGoalId] = useState<string | null>(null);
  const [saveAmount, setSaveAmount] = useState("");

  const load = () => {
    const params: Record<string, string> = {};
    if (filterStatus !== "all") params.status = filterStatus;
    if (filterPriority !== "all") params.priority = filterPriority;
    api.get("/goals", { params }).then((res) => setGoals(res.data));
  };

  useEffect(() => {
    load();
  }, [filterStatus, filterPriority]);

  const resetForm = () => {
    setForm({ ...defaultForm });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      name: form.name,
      target_amount: parseFloat(form.target_amount),
      saved_amount: parseFloat(form.saved_amount) || 0,
      priority: form.priority,
      category: form.category,
      status: form.status,
    };
    if (form.target_date) data.target_date = form.target_date;
    if (form.notes) data.notes = form.notes;

    try {
      if (editingId) {
        await api.put(`/goals/${editingId}`, data);
        toast.success("Atualizado com sucesso");
      } else {
        await api.post("/goals", data);
        toast.success("Criado com sucesso");
      }
      setOpen(false);
      resetForm();
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleEdit = (g: Goal) => {
    setForm({
      name: g.name,
      target_amount: String(g.target_amount),
      saved_amount: String(g.saved_amount),
      priority: g.priority,
      category: g.category,
      status: g.status,
      target_date: g.target_date || "",
      notes: g.notes || "",
    });
    setEditingId(g.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Tem certeza que deseja excluir?")) return;
    try {
      await api.delete(`/goals/${id}`);
      toast.success("Removido com sucesso");
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleSave = async (goalId: string, currentSaved: number) => {
    const addAmount = parseFloat(saveAmount);
    if (!addAmount || addAmount <= 0) return;
    try {
      await api.put(`/goals/${goalId}`, {
        saved_amount: currentSaved + addAmount,
      });
      toast.success("Atualizado com sucesso");
      setSavingGoalId(null);
      setSaveAmount("");
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const priorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      alta: "bg-red-100 text-red-700 border-red-300",
      media: "bg-yellow-100 text-yellow-700 border-yellow-300",
      baixa: "bg-green-100 text-green-700 border-green-300",
    };
    return (
      <Badge variant="outline" className={colors[priority] || ""}>
        {PRIORITIES[priority] || priority}
      </Badge>
    );
  };

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      ativa: "bg-blue-100 text-blue-700 border-blue-300",
      pausada: "bg-gray-100 text-gray-600 border-gray-300",
      concluida: "bg-emerald-100 text-emerald-700 border-emerald-300",
      cancelada: "bg-red-100 text-red-700 border-red-300",
    };
    return (
      <Badge variant="outline" className={colors[status] || ""}>
        {STATUSES[status] || status}
      </Badge>
    );
  };

  const progressColor = (pct: number) => {
    if (pct >= 80) return "bg-emerald-500";
    if (pct >= 50) return "bg-blue-500";
    if (pct >= 25) return "bg-yellow-500";
    return "bg-red-400";
  };

  const activeGoals = goals.filter((g) => g.status === "ativa");
  const totalTarget = activeGoals.reduce((s, g) => s + g.target_amount, 0);
  const totalSaved = activeGoals.reduce((s, g) => s + g.saved_amount, 0);
  const overallPct = totalTarget > 0 ? (totalSaved / totalTarget) * 100 : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Objetivos</h2>
          <PageHelp {...helpContent.goals} />
        </div>
        <Dialog
          open={open}
          onOpenChange={(v) => {
            setOpen(v);
            if (!v) resetForm();
          }}
        >
          <DialogTrigger render={<Button />}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Objetivo
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingId ? "Editar" : "Novo"} Objetivo
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
              <div>
                <Label>Nome</Label>
                <Input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Ex: TV 65&quot;, Viagem Europa"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Valor Necessário</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={form.target_amount}
                    onChange={(e) =>
                      setForm({ ...form, target_amount: e.target.value })
                    }
                    placeholder="R$ 0,00"
                  />
                </div>
                <div>
                  <Label>Valor Guardado</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={form.saved_amount}
                    onChange={(e) =>
                      setForm({ ...form, saved_amount: e.target.value })
                    }
                    placeholder="R$ 0,00"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Categoria</Label>
                  <Select
                    value={form.category}
                    onValueChange={(v) =>
                      setForm({ ...form, category: v ?? "" })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(CATEGORIES).map(([k, label]) => (
                        <SelectItem key={k} value={k}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Prioridade</Label>
                  <Select
                    value={form.priority}
                    onValueChange={(v) =>
                      setForm({ ...form, priority: v ?? "" })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(PRIORITIES).map(([k, label]) => (
                        <SelectItem key={k} value={k}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Status</Label>
                  <Select
                    value={form.status}
                    onValueChange={(v) =>
                      setForm({ ...form, status: v ?? "" })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(STATUSES).map(([k, label]) => (
                        <SelectItem key={k} value={k}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Data Alvo</Label>
                  <Input
                    type="date"
                    value={form.target_date}
                    onChange={(e) =>
                      setForm({ ...form, target_date: e.target.value })
                    }
                  />
                </div>
              </div>
              <div>
                <Label>Observações</Label>
                <Input
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Detalhes sobre o objetivo..."
                />
              </div>
              <Button className="w-full" onClick={handleSubmit}>
                {editingId ? "Salvar" : "Criar"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Metas Ativas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-500">
              {activeGoals.length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Valor Total Necessário
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              R${" "}
              {totalTarget.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Total Guardado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-emerald-500">
              R${" "}
              {totalSaved.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Progresso Geral
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-500">
              {overallPct.toFixed(0)}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <Select
          value={filterStatus}
          onValueChange={(v) => setFilterStatus(v ?? "all")}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos</SelectItem>
            {Object.entries(STATUSES).map(([k, label]) => (
              <SelectItem key={k} value={k}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filterPriority}
          onValueChange={(v) => setFilterPriority(v ?? "all")}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Prioridade" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todas</SelectItem>
            {Object.entries(PRIORITIES).map(([k, label]) => (
              <SelectItem key={k} value={k}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Goal Cards */}
      {goals.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Nenhum objetivo cadastrado ainda.</p>
            <p className="text-sm">
              Clique em &quot;Novo Objetivo&quot; para começar!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {goals.map((g) => {
            const pct =
              g.target_amount > 0
                ? (g.saved_amount / g.target_amount) * 100
                : 0;
            const clampedPct = Math.min(pct, 100);

            return (
              <Card key={g.id} className="flex flex-col">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{g.name}</CardTitle>
                      <div className="flex gap-2 flex-wrap">
                        <Badge variant="secondary">
                          {CATEGORIES[g.category] || g.category}
                        </Badge>
                        {priorityBadge(g.priority)}
                        {statusBadge(g.status)}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 space-y-4">
                  {/* Progress */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-muted-foreground">Progresso</span>
                      <span className="font-medium">{pct.toFixed(0)}%</span>
                    </div>
                    <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${progressColor(clampedPct)}`}
                        style={{ width: `${clampedPct}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-muted-foreground">
                        R${" "}
                        {g.saved_amount.toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                        })}
                      </span>
                      <span className="font-medium">
                        R${" "}
                        {g.target_amount.toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                        })}
                      </span>
                    </div>
                  </div>

                  {/* Target date */}
                  {g.target_date && (
                    <p className="text-sm text-muted-foreground">
                      Meta:{" "}
                      {new Date(g.target_date + "T00:00:00").toLocaleDateString(
                        "pt-BR",
                        { month: "long", year: "numeric" }
                      )}
                    </p>
                  )}

                  {/* Notes */}
                  {g.notes && (
                    <p className="text-sm text-muted-foreground italic">
                      {g.notes}
                    </p>
                  )}

                  {/* Save money input */}
                  {savingGoalId === g.id ? (
                    <div className="flex gap-2">
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="R$ 0,00"
                        value={saveAmount}
                        onChange={(e) => setSaveAmount(e.target.value)}
                        className="flex-1"
                      />
                      <Button
                        size="sm"
                        onClick={() => handleSave(g.id, g.saved_amount)}
                      >
                        OK
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSavingGoalId(null);
                          setSaveAmount("");
                        }}
                      >
                        X
                      </Button>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => setSavingGoalId(g.id)}
                      >
                        <PiggyBank className="h-4 w-4 mr-1" />
                        Guardar
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handleEdit(g)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handleDelete(g.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
