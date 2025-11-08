import Navigation from "@/components/Navigation";
import DashboardsSection from "@/components/DashboardsSection";

const Dashboards = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="pt-16">
        <DashboardsSection />
      </div>
    </div>
  );
};

export default Dashboards;
