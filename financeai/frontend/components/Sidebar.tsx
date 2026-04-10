"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, ArrowLeftRight, CreditCard, TrendingUp,
  Receipt, Target, Repeat, PieChart, Sun, Moon, Wallet, ClipboardList,
} from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transações", icon: ArrowLeftRight },
  { href: "/credit-cards", label: "Cartões", icon: CreditCard },
  { href: "/investments", label: "Investimentos", icon: TrendingUp },
  { href: "/debts", label: "Dívidas", icon: Receipt },
  { href: "/goals", label: "Objetivos", icon: Target },
  { href: "/planning", label: "Planejamento", icon: ClipboardList },
  { href: "/recurring", label: "Recorrentes", icon: Repeat },
  { href: "/budgets", label: "Orçamentos", icon: PieChart },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="w-64 min-h-screen bg-card border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6 flex items-center gap-3">
        <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center">
          <Wallet className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">FinanceAI</h1>
          <p className="text-xs text-muted-foreground -mt-0.5">Controle financeiro</p>
        </div>
      </div>

      {/* Separator */}
      <div className="mx-4 border-b border-border" />

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Theme toggle */}
      <div className="p-4 border-t border-border">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-all"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          {theme === "dark" ? "Modo Claro" : "Modo Escuro"}
        </button>
      </div>
    </aside>
  );
}
