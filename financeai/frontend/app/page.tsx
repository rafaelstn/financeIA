import SummaryCards from "@/components/SummaryCards";
import SpendingChart from "@/components/SpendingChart";
import AlertsPanel from "@/components/AlertsPanel";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <SummaryCards />
      <SpendingChart />
      <AlertsPanel />
    </div>
  );
}
