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
import { Plus, Trash2, Pencil } from "lucide-react";
import api from "@/lib/api";

const CATEGORIES: Record<string, string> = {
  cartao: "Cartao",
  emprestimo: "Emprestimo",
  financiamento: "Financiamento",
  cheque_especial: "Cheque Especial",
  conta_consumo: "Conta de Consumo",
  outros: "Outros",
};

const STATUSES: Record<string, string> = {
  ativa: "Ativa",
  negociando: "Negociando",
  acordo: "Em Acordo",
  quitada: "Quitada",
  prescrita: "Prescrita",
};

interface Debt {
  id: string;
  creditor: string;
  original_amount: number;
  current_amount: number;
  category: string;
  status: string;
  origin_date: string;
  is_paying: boolean;
  monthly_payment: number | null;
  payment_day: number | null;
  total_installments: number | null;
  paid_installments: number;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
}

const defaultForm = {
  creditor: "",
  original_amount: "",
  current_amount: "",
  category: "cartao",
  status: "ativa",
  origin_date: "",
  is_paying: false,
  monthly_payment: "",
  payment_day: "",
  total_installments: "",
  paid_installments: "0",
  notes: "",
};

export default function DebtsPage() {
  const [debts, setDebts] = useState<Debt[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...defaultForm });
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const load = () => {
    const params: Record<string, string> = {};
    if (filterStatus !== "all") params.status = filterStatus;
    if (filterCategory !== "all") params.category = filterCategory;
    api.get("/debts", { params }).then((res) => setDebts(res.data.data || res.data));
  };

  useEffect(() => {
    load();
  }, [filterStatus, filterCategory]);

  const resetForm = () => {
    setForm({ ...defaultForm });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      creditor: form.creditor,
      original_amount: parseFloat(form.original_amount),
      current_amount: parseFloat(form.current_amount),
      category: form.category,
      status: form.status,
      origin_date: form.origin_date,
      is_paying: form.is_paying,
      paid_installments: parseInt(form.paid_installments) || 0,
    };
    if (form.monthly_payment) data.monthly_payment = parseFloat(form.monthly_payment);
    if (form.payment_day) data.payment_day = parseInt(form.payment_day);
    if (form.total_installments)
      data.total_installments = parseInt(form.total_installments);
    if (form.notes) data.notes = form.notes;

    if (editingId) {
      await api.put(`/debts/${editingId}`, data);
    } else {
      await api.post("/debts", data);
    }
    setOpen(false);
    resetForm();
    load();
  };

  const handleEdit = (d: Debt) => {
    setForm({
      creditor: d.creditor,
      original_amount: String(d.original_amount),
      current_amount: String(d.current_amount),
      category: d.category,
      status: d.status,
      origin_date: d.origin_date || "",
      is_paying: d.is_paying,
      monthly_payment: d.monthly_payment ? String(d.monthly_payment) : "",
      payment_day: d.payment_day ? String(d.payment_day) : "",
      total_installments: d.total_installments ? String(d.total_installments) : "",
      paid_installments: String(d.paid_installments),
      notes: d.notes || "",
    });
    setEditingId(d.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Tem certeza que deseja excluir?")) return;
    await api.delete(`/debts/${id}`);
    load();
  };

  const statusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      ativa: "destructive",
      negociando: "outline",
      acordo: "secondary",
      quitada: "default",
      prescrita: "secondary",
    };
    const colors: Record<string, string> = {
      ativa: "",
      negociando: "border-yellow-500 text-yellow-600",
      acordo: "border-blue-500 text-blue-600 bg-blue-50",
      quitada: "bg-emerald-600",
      prescrita: "border-gray-400 text-gray-500",
    };
    return (
      <Badge variant={variants[status] || "secondary"} className={colors[status] || ""}>
        {STATUSES[status] || status}
      </Badge>
    );
  };

  const activeDebts = debts.filter((d) =>
    ["ativa", "negociando"].includes(d.status)
  );
  const activeTotal = activeDebts.reduce((s, d) => s + d.current_amount, 0);
  const agreementDebts = debts.filter((d) => d.status === "acordo");
  const settledDebts = debts.filter((d) => d.status === "quitada");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Dividas</h2>
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
              <DialogTitle>{editingId ? "Editar" : "Nova"} Divida</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
              <div>
                <Label>Credor</Label>
                <Input
                  value={form.creditor}
                  onChange={(e) => setForm({ ...form, creditor: e.target.value })}
                  placeholder="Ex: Nubank, Casas Bahia"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Valor Original</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={form.original_amount}
                    onChange={(e) =>
                      setForm({ ...form, original_amount: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label>Valor Atual</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={form.current_amount}
                    onChange={(e) =>
                      setForm({ ...form, current_amount: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
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
                  <Label>Status</Label>
                  <Select
                    value={form.status}
                    onValueChange={(v) => setForm({ ...form, status: v ?? "" })}
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
              </div>
              <div>
                <Label>Data de Origem</Label>
                <Input
                  type="date"
                  value={form.origin_date}
                  onChange={(e) =>
                    setForm({ ...form, origin_date: e.target.value })
                  }
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_paying"
                  checked={form.is_paying}
                  onChange={(e) =>
                    setForm({ ...form, is_paying: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="is_paying">Estou pagando atualmente</Label>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Parcela Mensal</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={form.monthly_payment}
                    onChange={(e) =>
                      setForm({ ...form, monthly_payment: e.target.value })
                    }
                    placeholder="R$ 0,00"
                  />
                </div>
                <div>
                  <Label>Dia do Pagamento</Label>
                  <Input
                    type="number"
                    min="1"
                    max="31"
                    value={form.payment_day}
                    onChange={(e) =>
                      setForm({ ...form, payment_day: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Total de Parcelas</Label>
                  <Input
                    type="number"
                    value={form.total_installments}
                    onChange={(e) =>
                      setForm({ ...form, total_installments: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label>Parcelas Pagas</Label>
                  <Input
                    type="number"
                    value={form.paid_installments}
                    onChange={(e) =>
                      setForm({ ...form, paid_installments: e.target.value })
                    }
                  />
                </div>
              </div>
              <div>
                <Label>Observacoes</Label>
                <Input
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
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
              Dividas Ativas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-500">{activeDebts.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Valor Total
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-500">
              R${" "}
              {activeTotal.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Em Acordo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-500">
              {agreementDebts.length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Quitadas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-emerald-500">
              {settledDebts.length}
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
          value={filterCategory}
          onValueChange={(v) => setFilterCategory(v ?? "all")}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Categoria" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todas</SelectItem>
            {Object.entries(CATEGORIES).map(([k, label]) => (
              <SelectItem key={k} value={k}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Credor</TableHead>
                <TableHead>Valor Original</TableHead>
                <TableHead>Valor Atual</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Origem</TableHead>
                <TableHead>Pagando?</TableHead>
                <TableHead>Parcela</TableHead>
                <TableHead className="w-20">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {debts.map((d) => (
                <TableRow key={d.id}>
                  <TableCell className="font-medium">{d.creditor}</TableCell>
                  <TableCell>
                    R${" "}
                    {d.original_amount.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                    })}
                  </TableCell>
                  <TableCell className="text-red-500 font-medium">
                    R${" "}
                    {d.current_amount.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                    })}
                  </TableCell>
                  <TableCell>{CATEGORIES[d.category] || d.category}</TableCell>
                  <TableCell>{statusBadge(d.status)}</TableCell>
                  <TableCell>{d.origin_date || "-"}</TableCell>
                  <TableCell>{d.is_paying ? "Sim" : "Nao"}</TableCell>
                  <TableCell>
                    {d.monthly_payment
                      ? `R$ ${d.monthly_payment.toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                        })}`
                      : "-"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEdit(d)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(d.id)}
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
