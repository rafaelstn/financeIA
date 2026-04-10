"use client";

import { useEffect, useState } from "react";
import { formatDate } from "@/lib/utils";
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
  Salario: "Salário",
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
  use_business_day: boolean;
  business_day_number: number | null;
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
  use_business_day: false,
  business_day_number: "",
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
      use_business_day: form.use_business_day,
    };
    if (form.use_business_day && form.business_day_number) {
      data.business_day_number = parseInt(form.business_day_number);
      // Backend auto-calculates next_due_date for business day mode
    } else {
      data.next_due_date = form.next_due_date;
    }
    if (form.day_of_month) data.day_of_month = parseInt(form.day_of_month);
    if (form.notes) data.notes = form.notes;

    try {
      if (editingId) {
        await api.put(`/recurring/${editingId}`, data);
        toast.success("Atualizado com sucesso");
      } else {
        await api.post("/recurring", data);
        toast.success("Criado com sucesso");
      }
      setOpen(false);
      resetForm();
      load();
    } catch {
      toast.error("Erro na operacao");
    }
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
      use_business_day: item.use_business_day || false,
      business_day_number: item.business_day_number ? String(item.business_day_number) : "",
      notes: item.notes || "",
    });
    setEditingId(item.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/recurring/${id}`);
      toast.success("Removido com sucesso");
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleToggleActive = async (item: RecurringTransaction) => {
    try {
      await api.put(`/recurring/${item.id}`, { is_active: !item.is_active });
      toast.success("Atualizado com sucesso");
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setGeneratedCount(null);
    try {
      const res = await api.post("/recurring/generate");
      setGeneratedCount(res.data.generated);
      toast.success("Pendentes gerados com sucesso");
    } catch {
      toast.error("Erro na operacao");
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
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Transações Recorrentes</h2>
          <PageHelp {...helpContent.recurring} />
        </div>
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
                  {editingId ? "Editar" : "Nova"} Transação Recorrente
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                <div>
                  <Label>Descrição</Label>
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
                          <SelectItem key={k} value={k} label={label}>
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
                          <SelectItem key={k} value={k} label={label}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Frequência</Label>
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
                          <SelectItem key={k} value={k} label={label}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex items-center gap-3 py-1">
                  <button
                    type="button"
                    onClick={() =>
                      setForm({ ...form, use_business_day: !form.use_business_day })
                    }
                    className={`w-10 h-5 rounded-full relative transition-colors ${
                      form.use_business_day ? "bg-emerald-500" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`block w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${
                        form.use_business_day ? "translate-x-5" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                  <Label className="cursor-pointer" onClick={() =>
                    setForm({ ...form, use_business_day: !form.use_business_day })
                  }>
                    Usar dia útil do mês
                  </Label>
                </div>
                {form.use_business_day ? (
                  <div>
                    <Label>Qual dia útil? (ex: 5 = 5º dia útil)</Label>
                    <Input
                      type="number"
                      min="1"
                      max="23"
                      value={form.business_day_number}
                      onChange={(e) =>
                        setForm({ ...form, business_day_number: e.target.value })
                      }
                      placeholder="Ex: 5"
                    />
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Dia do Mês</Label>
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
                      <Label>Próximo Vencimento</Label>
                      <Input
                        type="date"
                        value={form.next_due_date}
                        onChange={(e) =>
                          setForm({ ...form, next_due_date: e.target.value })
                        }
                      />
                    </div>
                  </div>
                )}
                <div>
                  <Label>Observações</Label>
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
            ? `${generatedCount} transação(ões) pendente(s) gerada(s) com sucesso!`
            : "Nenhuma transação pendente para gerar no momento."}
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
                <TableHead>Descrição</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Frequência</TableHead>
                <TableHead>Próximo Vencimento</TableHead>
                <TableHead>Ativo?</TableHead>
                <TableHead className="w-20">Ações</TableHead>
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
                  <TableCell>
                    {item.use_business_day && item.business_day_number ? (
                      <span>
                        {item.business_day_number}º dia útil
                        <span className="text-muted-foreground text-xs ml-1">
                          ({formatDate(item.next_due_date)})
                        </span>
                      </span>
                    ) : (
                      formatDate(item.next_due_date)
                    )}
                  </TableCell>
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
