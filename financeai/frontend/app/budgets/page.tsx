"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Plus, Pencil, Trash2 } from "lucide-react";
import PageHelp from "@/components/PageHelp";
import { helpContent } from "@/lib/help-content";
import api from "@/lib/api";
import { toast } from "sonner";

const CATEGORIES: Record<string, string> = {
  Alimentacao: "Alimentação",
  Moradia: "Moradia",
  Transporte: "Transporte",
  Saude: "Saúde",
  Lazer: "Lazer",
  Educacao: "Educação",
  Outros: "Outros",
};

interface BudgetStatus {
  id: string;
  category: string;
  monthly_limit: number;
  spent: number;
  remaining: number;
  percentage: number;
}

interface Budget {
  id: string;
  category: string;
  monthly_limit: number;
  is_active: boolean;
  created_at: string | null;
}

const defaultForm = {
  category: "Alimentacao",
  monthly_limit: "",
};

function getProgressColor(pct: number): string {
  if (pct > 100) return "bg-red-500";
  if (pct >= 80) return "bg-orange-500";
  if (pct >= 50) return "bg-yellow-500";
  return "bg-emerald-500";
}

function getCardBorder(pct: number): string {
  if (pct > 100) return "border-red-300";
  if (pct >= 80) return "border-orange-300";
  if (pct >= 50) return "border-yellow-300";
  return "border-emerald-300";
}

export default function BudgetsPage() {
  const [statusList, setStatusList] = useState<BudgetStatus[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...defaultForm });

  const load = () => {
    api.get("/budgets/status").then((res) => setStatusList(res.data));
    api.get("/budgets").then((res) => setBudgets(res.data));
  };

  useEffect(() => {
    load();
  }, []);

  const resetForm = () => {
    setForm({ ...defaultForm });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data = {
      category: form.category,
      monthly_limit: parseFloat(form.monthly_limit),
    };

    try {
      if (editingId) {
        await api.put(`/budgets/${editingId}`, data);
        toast.success("Atualizado com sucesso");
      } else {
        await api.post("/budgets", data);
        toast.success("Criado com sucesso");
      }
      setOpen(false);
      resetForm();
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleEdit = (b: Budget) => {
    setForm({
      category: b.category,
      monthly_limit: String(b.monthly_limit),
    });
    setEditingId(b.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/budgets/${id}`);
      toast.success("Removido com sucesso");
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const totalLimit = statusList.reduce((s, b) => s + b.monthly_limit, 0);
  const totalSpent = statusList.reduce((s, b) => s + b.spent, 0);
  const totalPct = totalLimit > 0 ? (totalSpent / totalLimit) * 100 : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Orçamentos por Categoria</h2>
          <PageHelp {...helpContent.budgets} />
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
            Novo Orçamento
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingId ? "Editar" : "Novo"} Orçamento
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Categoria</Label>
                <Select
                  value={form.category}
                  onValueChange={(v) => setForm({ ...form, category: v ?? "" })}
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
                <Label>Limite Mensal (R$)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={form.monthly_limit}
                  onChange={(e) =>
                    setForm({ ...form, monthly_limit: e.target.value })
                  }
                  placeholder="0,00"
                />
              </div>
              <Button className="w-full" onClick={handleSubmit}>
                {editingId ? "Salvar" : "Criar"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Overview Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">
            Resumo Geral
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-2">
            <span className="text-lg font-bold">
              R${" "}
              {totalSpent.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}{" "}
              / R${" "}
              {totalLimit.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </span>
            <span className="text-sm text-muted-foreground">
              {totalPct.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${getProgressColor(totalPct)}`}
              style={{ width: `${Math.min(totalPct, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Budget Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {statusList.map((b) => {
          const budget = budgets.find((bg) => bg.id === b.id);
          return (
            <Card
              key={b.id}
              className={`border-2 ${getCardBorder(b.percentage)}`}
            >
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-base">{b.category}</CardTitle>
                  <div className="flex gap-1">
                    {budget && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => handleEdit(budget)}
                      >
                        <Pencil className="h-3 w-3" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => handleDelete(b.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Gasto</span>
                    <span className="font-medium">
                      R${" "}
                      {b.spent.toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                      })}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all ${getProgressColor(b.percentage)}`}
                      style={{
                        width: `${Math.min(b.percentage, 100)}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">
                      Limite: R${" "}
                      {b.monthly_limit.toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                      })}
                    </span>
                    <span
                      className={`font-bold ${
                        b.percentage > 100
                          ? "text-red-500"
                          : b.percentage >= 80
                            ? "text-orange-500"
                            : "text-muted-foreground"
                      }`}
                    >
                      {b.percentage.toFixed(0)}%
                    </span>
                  </div>
                  <div className="text-sm">
                    {b.remaining >= 0 ? (
                      <span className="text-emerald-600">
                        Restam R${" "}
                        {b.remaining.toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                        })}
                      </span>
                    ) : (
                      <span className="text-red-500 font-medium">
                        Excedido em R${" "}
                        {Math.abs(b.remaining).toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                        })}
                      </span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {statusList.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          Nenhum orçamento definido. Clique em "Novo Orçamento" para começar.
        </div>
      )}
    </div>
  );
}
