"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, Pencil } from "lucide-react";
import api from "@/lib/api";

interface Investment {
  id: string;
  name: string;
  type: string;
  institution: string;
  invested_amount: number;
  current_amount: number;
  start_date: string;
  maturity_date: string | null;
  notes: string | null;
}

export default function InvestmentsPage() {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "", type: "", institution: "", invested_amount: "",
    current_amount: "", start_date: "", maturity_date: "", notes: "",
  });

  const load = () => api.get("/investments").then((res) => setInvestments(res.data));
  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setForm({ name: "", type: "", institution: "", invested_amount: "", current_amount: "", start_date: "", maturity_date: "", notes: "" });
    setEditingId(null);
  };

  const handleSubmit = async () => {
    const data: Record<string, unknown> = {
      name: form.name, type: form.type, institution: form.institution,
      invested_amount: parseFloat(form.invested_amount),
      current_amount: parseFloat(form.current_amount),
      start_date: form.start_date,
    };
    if (form.maturity_date) data.maturity_date = form.maturity_date;
    if (form.notes) data.notes = form.notes;

    if (editingId) {
      await api.put(`/investments/${editingId}`, data);
    } else {
      await api.post("/investments", data);
    }
    setOpen(false);
    resetForm();
    load();
  };

  const handleEdit = (inv: Investment) => {
    setForm({
      name: inv.name, type: inv.type, institution: inv.institution,
      invested_amount: String(inv.invested_amount), current_amount: String(inv.current_amount),
      start_date: inv.start_date, maturity_date: inv.maturity_date || "", notes: inv.notes || "",
    });
    setEditingId(inv.id);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    await api.delete(`/investments/${id}`);
    load();
  };

  const totalInvested = investments.reduce((s, i) => s + i.invested_amount, 0);
  const totalCurrent = investments.reduce((s, i) => s + i.current_amount, 0);
  const totalReturn = totalCurrent - totalInvested;
  const returnPct = totalInvested > 0 ? ((totalReturn / totalInvested) * 100).toFixed(2) : "0.00";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Investimentos</h2>
        <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) resetForm(); }}>
          <DialogTrigger asChild><Button><Plus className="h-4 w-4 mr-2" />Adicionar</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>{editingId ? "Editar" : "Novo"} Investimento</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div><Label>Nome</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Tipo</Label><Input value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} placeholder="CDB, Acoes, FII..." /></div>
                <div><Label>Instituicao</Label><Input value={form.institution} onChange={(e) => setForm({ ...form, institution: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Valor Investido</Label><Input type="number" step="0.01" value={form.invested_amount} onChange={(e) => setForm({ ...form, invested_amount: e.target.value })} /></div>
                <div><Label>Valor Atual</Label><Input type="number" step="0.01" value={form.current_amount} onChange={(e) => setForm({ ...form, current_amount: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Data Inicio</Label><Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></div>
                <div><Label>Vencimento</Label><Input type="date" value={form.maturity_date} onChange={(e) => setForm({ ...form, maturity_date: e.target.value })} /></div>
              </div>
              <div><Label>Observacoes</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
              <Button className="w-full" onClick={handleSubmit}>{editingId ? "Salvar" : "Criar"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Total Investido</p><p className="text-2xl font-bold text-blue-500">R$ {totalInvested.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</p></CardContent></Card>
        <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Valor Atual</p><p className="text-2xl font-bold text-blue-500">R$ {totalCurrent.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</p></CardContent></Card>
        <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Retorno</p><p className={`text-2xl font-bold ${totalReturn >= 0 ? "text-emerald-500" : "text-red-500"}`}>R$ {totalReturn.toLocaleString("pt-BR", { minimumFractionDigits: 2 })} ({returnPct}%)</p></CardContent></Card>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Instituicao</TableHead>
                <TableHead>Investido</TableHead>
                <TableHead>Atual</TableHead>
                <TableHead>Retorno</TableHead>
                <TableHead>Inicio</TableHead>
                <TableHead className="w-20">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {investments.map((inv) => {
                const ret = inv.current_amount - inv.invested_amount;
                return (
                  <TableRow key={inv.id}>
                    <TableCell>{inv.name}</TableCell>
                    <TableCell>{inv.type}</TableCell>
                    <TableCell>{inv.institution}</TableCell>
                    <TableCell>R$ {inv.invested_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell>R$ {inv.current_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell className={ret >= 0 ? "text-emerald-500" : "text-red-500"}>
                      R$ {ret.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell>{inv.start_date}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleEdit(inv)}><Pencil className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(inv.id)}><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
