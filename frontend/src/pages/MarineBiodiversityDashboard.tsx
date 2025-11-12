import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation"; // keep consistent topbar if used globally

const MarineBiodiversityDashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Optional global nav bar (remove if not needed) */}
      <Navigation />

      <div className="p-10 pt-24">
        <button
          onClick={() => navigate("/dashboards")}
          className="flex items-center text-primary mb-6 hover:underline"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboards
        </button>

        <h1 className="text-3xl font-bold mb-4">🪸 Marine Biodiversity Dashboard</h1>
        <p className="text-muted-foreground mb-6">
          Insights into species richness, coral health, and ecosystem stability.
        </p>

        {/* Embedded Streamlit Dashboard */}
        <div className="rounded-lg overflow-hidden shadow-lg border border-border">
          <iframe
            src="http://localhost:8501" // ✅ running Streamlit or FastAPI+Streamlit server
            title="Marine Biodiversity Dashboard"
            width="100%"
            height="850"
            className="rounded-lg"
            style={{
              border: "none",
            }}
          ></iframe>
        </div>
      </div>
    </div>
  );
};

export default MarineBiodiversityDashboard;
