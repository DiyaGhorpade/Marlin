import Navigation from "@/components/Navigation";
import DashboardsSection from "@/components/DashboardsSection";

const Dashboards = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Top navigation bar */}
      <Navigation />

      {/* Main dashboard selector section */}
      <main className="pt-24 px-6">
        <DashboardsSection />
      </main>
    </div>
  );
};

export default Dashboards;
