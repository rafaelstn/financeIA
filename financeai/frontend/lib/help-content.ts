export const helpContent: Record<string, {
  title: string;
  description: string;
  steps: string[];
  tips?: string[];
}> = {
  transactions: {
    title: "Transações",
    description: "Gerencie todas as suas receitas e despesas. Aqui você registra cada movimentação financeira com data de vencimento, categoria e status de pagamento.",
    steps: [
      "Clique em 'Adicionar' para criar uma nova transação",
      "Preencha descrição, valor, tipo (receita ou despesa) e categoria",
      "Defina a data de vencimento e o status (pendente, pago ou vencido)",
      "Use os filtros para encontrar transações específicas",
      "Exporte tudo para CSV clicando em 'Exportar CSV'",
    ],
    tips: [
      "Marque como 'Pago' assim que efetuar o pagamento",
      "Use categorias consistentes para ter relatórios melhores no dashboard",
    ],
  },
  "credit-cards": {
    title: "Cartões de Crédito",
    description: "Controle seus cartões, faturas e lançamentos. Organize cada compra dentro da fatura do mês correspondente.",
    steps: [
      "Cadastre seus cartões com nome, banco, limite e dias de fechamento/vencimento",
      "Clique no cartão para expandir e ver as faturas",
      "Crie faturas mensais e adicione os lançamentos de cada mês",
      "Acompanhe o total de cada fatura e o status (aberta, fechada, paga)",
    ],
    tips: [
      "Registre compras parceladas informando o número de parcelas",
      "Crie a fatura do mês assim que o cartão fechar",
    ],
  },
  investments: {
    title: "Investimentos",
    description: "Acompanhe sua carteira de investimentos. Registre cada aplicação com valor investido e valor atual para ver o retorno.",
    steps: [
      "Clique em 'Adicionar' para registrar um investimento",
      "Informe o tipo (CDB, Ações, FII, etc.), instituição e valores",
      "Atualize o valor atual periodicamente para acompanhar o rendimento",
      "Veja o retorno total e percentual nos cards de resumo",
    ],
    tips: [
      "Atualize os valores pelo menos uma vez por mês",
      "Use nomes descritivos para identificar cada investimento facilmente",
    ],
  },
  debts: {
    title: "Dívidas",
    description: "Controle suas dívidas e negociações. Registre cada dívida com valor original, valor atual e acompanhe o progresso de pagamento.",
    steps: [
      "Cadastre cada dívida com credor, valores e categoria",
      "Atualize o status conforme a situação (ativa, negociando, em acordo, quitada)",
      "Se estiver pagando, informe a parcela mensal e o dia de pagamento",
      "Use os filtros para ver dívidas por status ou categoria",
    ],
    tips: [
      "Priorize as dívidas com juros mais altos",
      "Atualize o valor atual conforme os pagamentos são feitos",
    ],
  },
  goals: {
    title: "Objetivos",
    description: "Defina metas financeiras e acompanhe o progresso. Guarde dinheiro aos poucos até atingir o valor necessário.",
    steps: [
      "Crie um objetivo com nome, valor necessário e prazo",
      "Use o botão 'Guardar' para adicionar valores ao objetivo",
      "Acompanhe o progresso pela barra e percentual",
      "Defina prioridade (alta, média, baixa) para organizar suas metas",
    ],
    tips: [
      "Defina uma data alvo para manter o foco",
      "Objetivos concluídos ficam registrados como conquistas",
    ],
  },
  recurring: {
    title: "Transações Recorrentes",
    description: "Cadastre contas fixas que se repetem todo mês (aluguel, luz, internet, salário). O sistema gera as transações automaticamente quando você clicar em 'Gerar Pendentes'.",
    steps: [
      "Cadastre a conta recorrente com valor, tipo e frequência",
      "Defina o dia do mês ou use dia útil para o vencimento",
      "Ative ou desative cada recorrência pelo botão de toggle",
      "Clique em 'Gerar Pendentes' para criar as transações do período",
    ],
    tips: [
      "Use 'dia útil' para contas que vencem em dias úteis (ex: salário no 5º dia útil)",
      "Desative temporariamente ao invés de excluir se a conta for pausada",
    ],
  },
  budgets: {
    title: "Orçamentos por Categoria",
    description: "Defina limites de gastos por categoria e acompanhe quanto já foi gasto no mês. Ajuda a controlar seus gastos e evitar excessos.",
    steps: [
      "Clique em 'Novo Orçamento' e escolha uma categoria",
      "Defina o limite mensal em reais",
      "Acompanhe a barra de progresso — verde é bom, vermelho é alerta",
      "Edite ou remova orçamentos conforme sua necessidade muda",
    ],
    tips: [
      "Comece pelas categorias onde você mais gasta",
      "O orçamento considera apenas despesas do mês atual",
      "Amarelo (50-80%) é um aviso para reduzir gastos na categoria",
    ],
  },
};
