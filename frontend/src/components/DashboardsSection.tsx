import { Card } from "@/components/ui/card";
import { Waves, Fish, Leaf } from "lucide-react";
import { useNavigate } from "react-router-dom";

const DashboardsSection = () => {
  const navigate = useNavigate();

  const dashboards = [
    {
      title: "Oceanographic Dashboard",
      desc: "Visualize ocean temperature, salinity, and currents",
      icon: <Waves className="w-8 h-8 text-primary-foreground" />,
      color: "bg-gradient-ocean",
      type: "internal",
      path: "/dashboards/oceanographic",
    },
    {
      title: "Fisheries Dashboard",
      desc: "Monitor fish population, catch rates, and yield trends",
      icon: <Fish className="w-8 h-8 text-primary-foreground" />,
      color: "bg-gradient-teal",
      type: "external",
      path: "https://www.perplexity.ai/apps/5a9a501c-07b3-4ea5-9aba-6891df832638",
    },
    {
      title: "Marine Biodiversity Dashboard",
      desc: "Track species diversity and ecosystem health indicators",
      icon: <Leaf className="w-8 h-8 text-primary-foreground" />,
      color: "bg-cyan-600",
      type: "internal",
      path: "/dashboards/biodiversity",
    },
  ];

  const handleCardClick = (item: any) => {
    if (item.type === "external") {
      window.open(item.path, "_blank"); // opens in a new tab
    } else {
      navigate(item.path);
    }
  };

  return (
    <section id="dashboards" className="py-24 bg-background">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-4xl font-bold mb-6 bg-gradient-ocean bg-clip-text text-transparent">
          Explore Our Dashboards
        </h2>
        <p className="text-muted-foreground mb-12 text-lg">
          Choose a dashboard to view detailed analytics
        </p>

        <div className="grid md:grid-cols-3 gap-6">
          {dashboards.map((item) => (
            <Card
              key={item.title}
              onClick={() => handleCardClick(item)}
              className={`p-8 cursor-pointer shadow-card hover:shadow-ocean transition-transform hover:scale-105`}
            >
              <div
                className={`w-16 h-16 mx-auto mb-6 rounded-2xl ${item.color} flex items-center justify-center`}
              >
                {item.icon}
              </div>
              <h3 className="text-2xl font-semibold mb-2">{item.title}</h3>
              <p className="text-muted-foreground">{item.desc}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default DashboardsSection;
