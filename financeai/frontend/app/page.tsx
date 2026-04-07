import SummaryCards from "@/components/SummaryCards";
import SpendingChart from "@/components/SpendingChart";
import GoalsProgress from "@/components/GoalsProgress";
import DebtsOverview from "@/components/DebtsOverview";
import AlertsPanel from "@/components/AlertsPanel";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <SummaryCards />
      <SpendingChart />
      <GoalsProgress />
      <DebtsOverview />
      <AlertsPanel />
    </div>
  );
}
