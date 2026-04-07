"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Pencil, Download } from "lucide-react";
import api from "@/lib/api";

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

export default function TransactionsPage() {
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

  const load = () => {
    const params: Record<string, string | number> = { page, per_page: perPage };
    if (filterType !== "all") params.type = filterType;
    if (filterCategory !== "all") params.category = filterCategory;
    api.get("/transactions", { params }).then((res) => {
      setTransactions(res.data.data || res.data);
      setTotal(res.data.total ?? 0);
    });
  };

  useEffect(() => { load(); }, [filterType, filterCategory, page]);

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

    if (editingId) {
      await api.put(`/transactions/${editingId}`, data);
    } else {
      await api.post("/transactions", data);
    }
    setOpen(false);
    resetForm();
    load();
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
    await api.delete(`/transactions/${id}`);
    load();
  };

  const handleExport = async () => {
    const res = await api.get("/transactions", { params: { per_page: 10000 } });
    const data = res.data.data || res.data;
    const headers = ["Descricao", "Valor", "Tipo", "Categoria", "Status", "Vencimento", "Pagamento"];
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
        <h2 className="text-2xl font-bold">Transacoes</h2>
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
                <DialogTitle>{editingId ? "Editar" : "Nova"} Transacao</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div><Label>Descricao</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
                <div><Label>Valor</Label><Input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} /></div>
                <div className="grid grid-cols-2 gap-4">
                  <div><Label>Tipo</Label>
                    <Select value={form.type} onValueChange={(v) => setForm({ ...form, type: v ?? "" })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent><SelectItem value="income">Receita</SelectItem><SelectItem value="expense">Despesa</SelectItem></SelectContent>
                    </Select>
                  </div>
                  <div><Label>Categoria</Label>
                    <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v ?? "" })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>{CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><Label>Status</Label>
                    <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v ?? "" })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent><SelectItem value="pending">Pendente</SelectItem><SelectItem value="paid">Pago</SelectItem><SelectItem value="overdue">Vencido</SelectItem></SelectContent>
                    </Select>
                  </div>
                  <div><Label>Vencimento</Label><Input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></div>
                </div>
                <div><Label>Data Pagamento</Label><Input type="date" value={form.paid_date} onChange={(e) => setForm({ ...form, paid_date: e.target.value })} /></div>
                <div><Label>Observacoes</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
                <Button className="w-full" onClick={handleSubmit}>{editingId ? "Salvar" : "Criar"}</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="flex gap-4">
        <Input
          placeholder="Buscar por descricao..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-64"
        />
        <Select value={filterType} onValueChange={(v) => { setFilterType(v ?? "all"); setPage(1); }}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Tipo" /></SelectTrigger>
          <SelectContent><SelectItem value="all">Todos</SelectItem><SelectItem value="income">Receitas</SelectItem><SelectItem value="expense">Despesas</SelectItem></SelectContent>
        </Select>
        <Select value={filterCategory} onValueChange={(v) => { setFilterCategory(v ?? "all"); setPage(1); }}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Categoria" /></SelectTrigger>
          <SelectContent><SelectItem value="all">Todas</SelectItem>{CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Descricao</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Vencimento</TableHead>
                <TableHead className="w-20">Acoes</TableHead>
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
                  <TableCell>{t.due_date || "-"}</TableCell>
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
            <p className="text-sm text-muted-foreground">{total} transacoes</p>
            <div className="flex gap-2 items-center">
              <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Anterior</Button>
              <span className="text-sm py-1">Pagina {page} de {totalPages || 1}</span>
              <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Proximo</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
