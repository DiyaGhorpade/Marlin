import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

const MarineBiodiversityDashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background p-10">
      <button
        onClick={() => navigate("/")}
        className="flex items-center text-primary mb-6 hover:underline"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboards
      </button>

      <h1 className="text-3xl font-bold mb-4">🪸 Marine Biodiversity Dashboard</h1>
      <p className="text-muted-foreground mb-6">
        Insights into species richness, coral health, and ecosystem stability.
      </p>

      <div className="rounded-lg overflow-hidden shadow-md border">
        <iframe
          src="http://localhost:8503" // your biodiversity dashboard server
          title="Marine Biodiversity Dashboard"
          width="100%"
          height="800"
        ></iframe>
      </div>
    </div>
  );
};

export default MarineBiodiversityDashboard;
