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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Plus, Trash2, Pencil, Play } from "lucide-react";
import api from "@/lib/api";

const CATEGORIES: Record<string, string> = {
  Alimentacao: "Alimentacao",
  Moradia: "Moradia",
  Transporte: "Transporte",
  Saude: "Saude",
  Lazer: "Lazer",
  Educacao: "Educacao",
  Salario: "Salario",
  Freelance: "Freelance",
  Investimento: "Investimento",
  Outros: "Outros",
};

const FREQUENCIES: Record<string, string> = {
  monthly: "Mensal",
  weekly: "Semanal",
  yearly: "Anual",
};

const TYPES: Record<string, string> = {
  income: "Receita",
  expense: "Despesa",
};

interface RecurringTransaction {
  id: string;
  description: string;
  amount: number;
  type: string;
  category: string;
  frequency: string;
  day_of_month: number | null;
  is_active: boolean;
  next_due_date: string;
  notes: string | null;
  created_at: string | null;
}

const defaultForm = {
  description: "",
  amount: "",
  type: "expense",
  category: "Moradia",
  frequency: "monthly",
  day_of_month: "",
  next_due_date: "",
  notes: "",
};

export default function RecurringPage() {
  const [items, setItems] = useState<RecurringTransaction[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...defaultForm });
  const [generating, setGenerating] = useState(false);
  const [generatedCount, setGeneratedCount] = useState<number | null>(null);

  const load = () => {
    api.get("/recurring").then((res) => setItems(res.data));
  };

  useEffect(() => {
    load();
  }, []);

  const resetForm = () => {
    setForm({ ...defaultForm });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      description: form.description,
      amount: parseFloat(form.amount),
      type: form.type,
      category: form.category,
      frequency: form.frequency,
      next_due_date: form.next_due_date,
    };
    if (form.day_of_month) data.day_of_month = parseInt(form.day_of_month);
    if (form.notes) data.notes = form.notes;

    if (editingId) {
      await api.put(`/recurring/${editingId}`, data);
    } else {
      await api.post("/recurring", data);
    }
    setOpen(false);
    resetForm();
    load();
  };

  const handleEdit = (item: RecurringTransaction) => {
    setForm({
      description: item.description,
      amount: String(item.amount),
      type: item.type,
      category: item.category,
      frequency: item.frequency,
      day_of_month: item.day_of_month ? String(item.day_of_month) : "",
      next_due_date: item.next_due_date || "",
      notes: item.notes || "",
    });
    setEditingId(item.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    await api.delete(`/recurring/${id}`);
    load();
  };

  const handleToggleActive = async (item: RecurringTransaction) => {
    await api.put(`/recurring/${item.id}`, { is_active: !item.is_active });
    load();
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setGeneratedCount(null);
    try {
      const res = await api.post("/recurring/generate");
      setGeneratedCount(res.data.generated);
    } finally {
      setGenerating(false);
    }
  };

  const activeItems = items.filter((i) => i.is_active);
  const totalExpense = activeItems
    .filter((i) => i.type === "expense")
    .reduce((s, i) => s + i.amount, 0);
  const totalIncome = activeItems
    .filter((i) => i.type === "income")
    .reduce((s, i) => s + i.amount, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Transacoes Recorrentes</h2>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleGenerate} disabled={generating}>
            <Play className="h-4 w-4 mr-2" />
            {generating ? "Gerando..." : "Gerar Pendentes"}
          </Button>
          <Dialog
            open={open}
            onOpenChange={(v) => {
              setOpen(v);
              if (!v) resetForm();
            }}
          >
            <DialogTrigger render={<Button />}>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingId ? "Editar" : "Nova"} Transacao Recorrente
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                <div>
                  <Label>Descricao</Label>
                  <Input
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
                    }
                    placeholder="Ex: Aluguel, Luz, Internet"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Valor</Label>
                    <Input
                      type="number"
                      step="0.01"
                      value={form.amount}
                      onChange={(e) =>
                        setForm({ ...form, amount: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label>Tipo</Label>
                    <Select
                      value={form.type}
                      onValueChange={(v) => setForm({ ...form, type: v ?? "" })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(TYPES).map(([k, label]) => (
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
                    <Label>Frequencia</Label>
                    <Select
                      value={form.frequency}
                      onValueChange={(v) =>
                        setForm({ ...form, frequency: v ?? "" })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(FREQUENCIES).map(([k, label]) => (
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
                    <Label>Dia do Mes</Label>
                    <Input
                      type="number"
                      min="1"
                      max="31"
                      value={form.day_of_month}
                      onChange={(e) =>
                        setForm({ ...form, day_of_month: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label>Proximo Vencimento</Label>
                    <Input
                      type="date"
                      value={form.next_due_date}
                      onChange={(e) =>
                        setForm({ ...form, next_due_date: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div>
                  <Label>Observacoes</Label>
                  <Input
                    value={form.notes}
                    onChange={(e) =>
                      setForm({ ...form, notes: e.target.value })
                    }
                  />
                </div>
                <Button className="w-full" onClick={handleSubmit}>
                  {editingId ? "Salvar" : "Criar"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {generatedCount !== null && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md text-emerald-700 text-sm">
          {generatedCount > 0
            ? `${generatedCount} transacao(oes) pendente(s) gerada(s) com sucesso!`
            : "Nenhuma transacao pendente para gerar no momento."}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Recorrentes Ativas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{activeItems.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Total Despesas Fixas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-500">
              R${" "}
              {totalExpense.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Total Receitas Fixas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-emerald-500">
              R${" "}
              {totalIncome.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Descricao</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Frequencia</TableHead>
                <TableHead>Proximo Vencimento</TableHead>
                <TableHead>Ativo?</TableHead>
                <TableHead className="w-20">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">
                    {item.description}
                  </TableCell>
                  <TableCell
                    className={
                      item.type === "expense"
                        ? "text-red-500 font-medium"
                        : "text-emerald-500 font-medium"
                    }
                  >
                    R${" "}
                    {item.amount.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                    })}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        item.type === "income" ? "default" : "destructive"
                      }
                    >
                      {TYPES[item.type] || item.type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {CATEGORIES[item.category] || item.category}
                  </TableCell>
                  <TableCell>
                    {FREQUENCIES[item.frequency] || item.frequency}
                  </TableCell>
                  <TableCell>{item.next_due_date || "-"}</TableCell>
                  <TableCell>
                    <button
                      onClick={() => handleToggleActive(item)}
                      className={`w-10 h-5 rounded-full relative transition-colors ${
                        item.is_active ? "bg-emerald-500" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`block w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${
                          item.is_active ? "translate-x-5" : "translate-x-0.5"
                        }`}
                      />
                    </button>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEdit(item)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(item.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
