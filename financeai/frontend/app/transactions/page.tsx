"use client";

import { useEffect, useState } from "react";
import { formatDate } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Pencil, Download } from "lucide-react";
import PageHelp from "@/components/PageHelp";
import { helpContent } from "@/lib/help-content";
import api from "@/lib/api";
import { toast } from "sonner";

const CATEGORIES = [
  "Alimentacao", "Moradia", "Transporte", "Saude", "Lazer",
  "Educacao", "Salario", "Freelance", "Investimento", "Outros",
];

interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: string;
  category: string;
  status: string;
  due_date: string | null;
  paid_date: string | null;
  notes: string | null;
}

const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function TransactionsPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    description: "", amount: "", type: "expense", category: "Outros",
    status: "pending", due_date: "", paid_date: "", notes: "",
  });
  const [filterType, setFilterType] = useState<string>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  function prevMonth() {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
    setPage(1);
  }

  function nextMonth() {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
    setPage(1);
  }

  const load = () => {
    const params: Record<string, string | number> = { page, per_page: perPage, month, year };
    if (filterType !== "all") params.type = filterType;
    if (filterCategory !== "all") params.category = filterCategory;
    api.get("/transactions", { params }).then((res) => {
      setTransactions(res.data.data || res.data);
      setTotal(res.data.total ?? 0);
    });
  };

  useEffect(() => { load(); }, [filterType, filterCategory, page, month, year]);

  const resetForm = () => {
    setForm({ description: "", amount: "", type: "expense", category: "Outros", status: "pending", due_date: "", paid_date: "", notes: "" });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      description: form.description,
      amount: parseFloat(form.amount),
      type: form.type,
      category: form.category,
      status: form.status,
    };
    if (form.due_date) data.due_date = form.due_date;
    if (form.paid_date) data.paid_date = form.paid_date;
    if (form.notes) data.notes = form.notes;

    try {
      if (editingId) {
        await api.put(`/transactions/${editingId}`, data);
        toast.success("Atualizado com sucesso");
      } else {
        await api.post("/transactions", data);
        toast.success("Criado com sucesso");
      }
      setOpen(false);
      resetForm();
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleEdit = (t: Transaction) => {
    setForm({
      description: t.description, amount: String(t.amount), type: t.type,
      category: t.category, status: t.status, due_date: t.due_date || "",
      paid_date: t.paid_date || "", notes: t.notes || "",
    });
    setEditingId(t.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Tem certeza que deseja excluir?")) return;
    try {
      await api.delete(`/transactions/${id}`);
      toast.success("Removido com sucesso");
      load();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const handleExport = async () => {
    const res = await api.get("/transactions", { params: { per_page: 10000 } });
    const data = res.data.data || res.data;
    const headers = ["Descrição", "Valor", "Tipo", "Categoria", "Status", "Vencimento", "Pagamento"];
    const rows = data.map((t: Transaction) => [
      t.description, t.amount, t.type === "income" ? "Receita" : "Despesa",
      t.category, t.status, t.due_date || "", t.paid_date || "",
    ]);
    const csv = [headers.join(","), ...rows.map((r: string[]) => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transacoes-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  };

  const statusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive"> = {
      paid: "default", pending: "secondary", overdue: "destructive",
    };
    const labels: Record<string, string> = { paid: "Pago", pending: "Pendente", overdue: "Vencido" };
    return <Badge variant={variants[status] || "secondary"}>{labels[status] || status}</Badge>;
  };

  const filtered = transactions.filter(t =>
    !search || t.description.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Transações</h2>
          <PageHelp {...helpContent.transactions} />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />Exportar CSV
          </Button>
          <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) resetForm(); }}>
            <DialogTrigger render={<Button />}>
              <Plus className="h-4 w-4 mr-2" />Adicionar
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingId ? "Editar" : "Nova"} Transação</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div><Label>Descrição</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
                <div><Label>Valor</Label><Input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} /></div>
                <div className="grid grid-cols-2 gap-4">
                  <div><Label>Tipo</Label>
                    <Select value={form.type} onValueChange={(v) => setForm({ ...form, type: v ?? "" })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent><SelectItem value="income" label="Receita">Receita</SelectItem><SelectItem value="expense" label="Despesa">Despesa</SelectItem></SelectContent>
                    </Select>
                  </div>
                  <div><Label>Categoria</Label>
                    <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v ?? "" })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>{CATEGORIES.map((c) => <SelectItem key={c} value={c} label={c}>{c}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><Label>Status</Label>
                    <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v ?? "" })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent><SelectItem value="pending" label="Pendente">Pendente</SelectItem><SelectItem value="paid" label="Pago">Pago</SelectItem><SelectItem value="overdue" label="Vencido">Vencido</SelectItem></SelectContent>
                    </Select>
                  </div>
                  <div><Label>Vencimento</Label><Input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></div>
                </div>
                <div><Label>Data Pagamento</Label><Input type="date" value={form.paid_date} onChange={(e) => setForm({ ...form, paid_date: e.target.value })} /></div>
                <div><Label>Observações</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
                <Button className="w-full" onClick={handleSubmit}>{editingId ? "Salvar" : "Criar"}</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        {/* Month selector */}
        <div className="flex gap-px bg-secondary rounded-md overflow-hidden border border-border">
          <button onClick={prevMonth} className="px-2.5 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
            &#8249;
          </button>
          <div className="px-3 py-1.5 text-sm font-semibold bg-accent min-w-[130px] text-center">
            {MONTH_NAMES[month - 1]} {year}
          </div>
          <button onClick={nextMonth} className="px-2.5 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
            &#8250;
          </button>
        </div>

        <Input
          placeholder="Buscar por descrição..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-64"
        />
        <select
          value={filterType}
          onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
          className="h-8 w-40 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none"
        >
          <option value="all">Todos</option>
          <option value="income">Receitas</option>
          <option value="expense">Despesas</option>
        </select>
        <select
          value={filterCategory}
          onChange={(e) => { setFilterCategory(e.target.value); setPage(1); }}
          className="h-8 w-40 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none"
        >
          <option value="all">Todas</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Descrição</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Vencimento</TableHead>
                <TableHead className="w-20">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.description}</TableCell>
                  <TableCell className={t.type === "income" ? "text-emerald-500" : "text-red-500"}>
                    R$ {t.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell>{t.type === "income" ? "Receita" : "Despesa"}</TableCell>
                  <TableCell>{t.category}</TableCell>
                  <TableCell>{statusBadge(t.status)}</TableCell>
                  <TableCell>{formatDate(t.due_date)}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEdit(t)}><Pencil className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(t.id)}><Trash2 className="h-4 w-4" /></Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <div className="flex items-center justify-between p-4">
            <p className="text-sm text-muted-foreground">{total} transações</p>
            <div className="flex gap-2 items-center">
              <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Anterior</Button>
              <span className="text-sm py-1">Página {page} de {totalPages || 1}</span>
              <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Próximo</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
