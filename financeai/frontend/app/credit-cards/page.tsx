"use client";

import { useEffect, useState } from "react";
import { formatDate } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Trash2, ChevronDown, ChevronRight } from "lucide-react";
import PageHelp from "@/components/PageHelp";
import { helpContent } from "@/lib/help-content";
import api from "@/lib/api";
import { toast } from "sonner";

interface CreditCard {
  id: string;
  name: string;
  bank: string;
  limit_amount: number;
  closing_day: number;
  due_day: number;
}

interface Invoice {
  id: string;
  card_id: string;
  month: number;
  year: number;
  total_amount: number;
  status: string;
  due_date: string | null;
}

interface Expense {
  id: string;
  invoice_id: string;
  description: string;
  amount: number;
  category: string;
  expense_date: string;
  installments: number;
  installment_number: number;
}

export default function CreditCardsPage() {
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [openCard, setOpenCard] = useState(false);
  const [cardForm, setCardForm] = useState({ name: "", bank: "", limit_amount: "", closing_day: "", due_day: "" });
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [invoices, setInvoices] = useState<Record<string, Invoice[]>>({});
  const [expandedInvoice, setExpandedInvoice] = useState<string | null>(null);
  const [expenses, setExpenses] = useState<Record<string, Expense[]>>({});
  const [openInvoice, setOpenInvoice] = useState(false);
  const [invoiceForm, setInvoiceForm] = useState({ month: "", year: "", due_date: "" });
  const [invoiceCardId, setInvoiceCardId] = useState("");
  const [openExpense, setOpenExpense] = useState(false);
  const [expenseForm, setExpenseForm] = useState({ description: "", amount: "", category: "Outros", expense_date: "", installments: "1", installment_number: "1" });
  const [expenseInvoice, setExpenseInvoice] = useState({ cardId: "", invoiceId: "" });

  const loadCards = () => api.get("/credit-cards").then((res) => setCards(res.data));
  useEffect(() => { loadCards(); }, []);

  const loadInvoices = async (cardId: string) => {
    const res = await api.get(`/credit-cards/${cardId}/invoices`);
    setInvoices((prev) => ({ ...prev, [cardId]: res.data }));
  };

  const loadExpenses = async (cardId: string, invoiceId: string) => {
    const res = await api.get(`/credit-cards/${cardId}/invoices/${invoiceId}/expenses`);
    setExpenses((prev) => ({ ...prev, [invoiceId]: res.data }));
  };

  const toggleCard = (cardId: string) => {
    if (expandedCard === cardId) {
      setExpandedCard(null);
    } else {
      setExpandedCard(cardId);
      loadInvoices(cardId);
    }
  };

  const toggleInvoice = (cardId: string, invoiceId: string) => {
    if (expandedInvoice === invoiceId) {
      setExpandedInvoice(null);
    } else {
      setExpandedInvoice(invoiceId);
      loadExpenses(cardId, invoiceId);
    }
  };

  const createCard = async () => {
    try {
      await api.post("/credit-cards", {
        name: cardForm.name, bank: cardForm.bank,
        limit_amount: parseFloat(cardForm.limit_amount),
        closing_day: parseInt(cardForm.closing_day),
        due_day: parseInt(cardForm.due_day),
      });
      toast.success("Criado com sucesso");
      setOpenCard(false);
      setCardForm({ name: "", bank: "", limit_amount: "", closing_day: "", due_day: "" });
      loadCards();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const deleteCard = async (id: string) => {
    if (!window.confirm("Tem certeza que deseja excluir este cartão?")) return;
    try {
      await api.delete(`/credit-cards/${id}`);
      toast.success("Removido com sucesso");
      loadCards();
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const createInvoice = async () => {
    try {
      await api.post(`/credit-cards/${invoiceCardId}/invoices`, {
        card_id: invoiceCardId,
        month: parseInt(invoiceForm.month),
        year: parseInt(invoiceForm.year),
        due_date: invoiceForm.due_date || null,
      });
      toast.success("Criado com sucesso");
      setOpenInvoice(false);
      setInvoiceForm({ month: "", year: "", due_date: "" });
      loadInvoices(invoiceCardId);
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const createExpense = async () => {
    const { cardId, invoiceId } = expenseInvoice;
    try {
      await api.post(`/credit-cards/${cardId}/invoices/${invoiceId}/expenses`, {
        invoice_id: invoiceId,
        description: expenseForm.description,
        amount: parseFloat(expenseForm.amount),
        category: expenseForm.category,
        expense_date: expenseForm.expense_date,
        installments: parseInt(expenseForm.installments),
        installment_number: parseInt(expenseForm.installment_number),
      });
      toast.success("Criado com sucesso");
      setOpenExpense(false);
      setExpenseForm({ description: "", amount: "", category: "Outros", expense_date: "", installments: "1", installment_number: "1" });
      loadExpenses(cardId, invoiceId);
      loadInvoices(cardId);
    } catch {
      toast.error("Erro na operacao");
    }
  };

  const invoiceStatus = (status: string) => {
    const map: Record<string, "default" | "secondary" | "destructive"> = { paid: "default", open: "secondary", closed: "destructive" };
    const labels: Record<string, string> = { paid: "Paga", open: "Aberta", closed: "Fechada" };
    return <Badge variant={map[status] || "secondary"}>{labels[status] || status}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Cartões de Crédito</h2>
          <PageHelp {...helpContent["credit-cards"]} />
        </div>
        <Dialog open={openCard} onOpenChange={setOpenCard}>
          <DialogTrigger render={<Button />}><Plus className="h-4 w-4 mr-2" />Novo Cartão</DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Novo Cartão</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div><Label>Nome</Label><Input value={cardForm.name} onChange={(e) => setCardForm({ ...cardForm, name: e.target.value })} /></div>
              <div><Label>Banco</Label><Input value={cardForm.bank} onChange={(e) => setCardForm({ ...cardForm, bank: e.target.value })} /></div>
              <div><Label>Limite</Label><Input type="number" value={cardForm.limit_amount} onChange={(e) => setCardForm({ ...cardForm, limit_amount: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Dia Fechamento</Label><Input type="number" value={cardForm.closing_day} onChange={(e) => setCardForm({ ...cardForm, closing_day: e.target.value })} /></div>
                <div><Label>Dia Vencimento</Label><Input type="number" value={cardForm.due_day} onChange={(e) => setCardForm({ ...cardForm, due_day: e.target.value })} /></div>
              </div>
              <Button className="w-full" onClick={createCard}>Criar</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Dialog open={openInvoice} onOpenChange={setOpenInvoice}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nova Fatura</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Mês</Label><Input type="number" min="1" max="12" value={invoiceForm.month} onChange={(e) => setInvoiceForm({ ...invoiceForm, month: e.target.value })} /></div>
              <div><Label>Ano</Label><Input type="number" value={invoiceForm.year} onChange={(e) => setInvoiceForm({ ...invoiceForm, year: e.target.value })} /></div>
            </div>
            <div><Label>Vencimento</Label><Input type="date" value={invoiceForm.due_date} onChange={(e) => setInvoiceForm({ ...invoiceForm, due_date: e.target.value })} /></div>
            <Button className="w-full" onClick={createInvoice}>Criar</Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={openExpense} onOpenChange={setOpenExpense}>
        <DialogContent>
          <DialogHeader><DialogTitle>Novo Lançamento</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><Label>Descrição</Label><Input value={expenseForm.description} onChange={(e) => setExpenseForm({ ...expenseForm, description: e.target.value })} /></div>
            <div><Label>Valor</Label><Input type="number" step="0.01" value={expenseForm.amount} onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })} /></div>
            <div><Label>Categoria</Label><Input value={expenseForm.category} onChange={(e) => setExpenseForm({ ...expenseForm, category: e.target.value })} /></div>
            <div><Label>Data</Label><Input type="date" value={expenseForm.expense_date} onChange={(e) => setExpenseForm({ ...expenseForm, expense_date: e.target.value })} /></div>
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Parcelas</Label><Input type="number" value={expenseForm.installments} onChange={(e) => setExpenseForm({ ...expenseForm, installments: e.target.value })} /></div>
              <div><Label>Parcela Nº</Label><Input type="number" value={expenseForm.installment_number} onChange={(e) => setExpenseForm({ ...expenseForm, installment_number: e.target.value })} /></div>
            </div>
            <Button className="w-full" onClick={createExpense}>Criar</Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="space-y-4">
        {cards.map((card) => (
          <Card key={card.id}>
            <CardHeader className="cursor-pointer" onClick={() => toggleCard(card.id)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {expandedCard === card.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  <CardTitle className="text-base">{card.name} — {card.bank}</CardTitle>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-muted-foreground">Limite: R$ {card.limit_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</span>
                  <span className="text-sm text-muted-foreground">Fecha dia {card.closing_day} | Vence dia {card.due_day}</span>
                  <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); deleteCard(card.id); }}><Trash2 className="h-4 w-4" /></Button>
                </div>
              </div>
            </CardHeader>
            {expandedCard === card.id && (
              <CardContent>
                <div className="flex justify-end mb-4">
                  <Button size="sm" variant="outline" onClick={() => { setInvoiceCardId(card.id); setOpenInvoice(true); }}>
                    <Plus className="h-4 w-4 mr-1" />Fatura
                  </Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Período</TableHead>
                      <TableHead>Total</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Vencimento</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(invoices[card.id] || []).map((inv) => (
                      <>
                        <TableRow key={inv.id} className="cursor-pointer" onClick={() => toggleInvoice(card.id, inv.id)}>
                          <TableCell className="flex items-center gap-2">
                            {expandedInvoice === inv.id ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                            {inv.month}/{inv.year}
                          </TableCell>
                          <TableCell>R$ {inv.total_amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                          <TableCell>{invoiceStatus(inv.status)}</TableCell>
                          <TableCell>{formatDate(inv.due_date)}</TableCell>
                        </TableRow>
                        {expandedInvoice === inv.id && (
                          <TableRow>
                            <TableCell colSpan={4} className="bg-muted/50 p-4">
                              <div className="flex justify-end mb-2">
                                <Button size="sm" variant="outline" onClick={() => { setExpenseInvoice({ cardId: card.id, invoiceId: inv.id }); setOpenExpense(true); }}>
                                  <Plus className="h-3 w-3 mr-1" />Lançamento
                                </Button>
                              </div>
                              <Table>
                                <TableHeader>
                                  <TableRow>
                                    <TableHead>Descrição</TableHead>
                                    <TableHead>Valor</TableHead>
                                    <TableHead>Categoria</TableHead>
                                    <TableHead>Data</TableHead>
                                    <TableHead>Parcela</TableHead>
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {(expenses[inv.id] || []).map((exp) => (
                                    <TableRow key={exp.id}>
                                      <TableCell>{exp.description}</TableCell>
                                      <TableCell>R$ {exp.amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                                      <TableCell>{exp.category}</TableCell>
                                      <TableCell>{formatDate(exp.expense_date)}</TableCell>
                                      <TableCell>{exp.installment_number}/{exp.installments}</TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </TableCell>
                          </TableRow>
                        )}
                      </>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
