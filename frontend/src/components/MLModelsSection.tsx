import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Sparkles, Zap, Database, MapPin, Thermometer } from "lucide-react";
import { Link } from "react-router-dom";

const models = [
  {
    name: "Species Richness Predictor",
    description: "Random Forest model predicting biodiversity levels across Indian coastal regions with 91.4% accuracy",
    accuracy: "91.4%",
    icon: MapPin,
    gradient: "from-green-500 to-blue-600",
    metrics: [
      { label: "Training Data", value: "Indian biodiversity records" },
      { label: "Coverage", value: "8°-37°N, 68°-97°E" },
      { label: "R² Score", value: "0.914" }
    ],
    link: "/species-richness-predictor" 
  },
  {
    name: "Ocean Parameter Predictor",
    description: "Predicts sea temperature & salinity using Linear Regression",
    icon: Thermometer,
    gradient: "from-cyan-500 to-blue-600",
    metrics: [

      { label: "Algorithm", value: "Linear Regression" },
      { label: "Data Source", value: "Copernicus " },
    ],
    link: "/ocean-predictor"
  },
];

const MLModelsSection = () => {
  return (
    <section id="models" className="py-24 bg-gradient-to-b from-teal-light/5 to-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            <span className="bg-gradient-ocean bg-clip-text text-transparent">
              ML Models
            </span>
          </h2>
          <p className="text-muted-foreground text-lg">
            Cutting-edge machine learning models for marine intelligence
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {models.map((model, index) => {
            const Icon = model.icon;
            return (
              <Card key={index} className="p-6 shadow-card hover:shadow-ocean transition-all hover:-translate-y-1">
                <div className="space-y-6">
                  <div className="flex items-start justify-between">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${model.gradient} flex items-center justify-center`}>
                      <Icon className="w-7 h-7 text-primary-foreground" />
                    </div>
                    <div className="px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-semibold">
                      {model.accuracy}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold mb-2">{model.name}</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      {model.description}
                    </p>
                  </div>

                  <div className="space-y-3 pt-4 border-t border-border">
                    {model.metrics.map((metric, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">{metric.label}</span>
                        <span className="text-sm font-semibold text-foreground">{metric.value}</span>
                      </div>
                    ))}
                  </div>

                  {model.link ? (
                    <Link to={model.link}>
                      <Button className="w-full bg-gradient-ocean hover:opacity-90">
                        Explore Model
                      </Button>
                    </Link>
                  ) : (
                    <Button className="w-full bg-gradient-ocean hover:opacity-90">
                      Explore Model
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>

        <Card className="p-8 bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 border-primary/20">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="w-20 h-20 rounded-2xl bg-gradient-ocean flex items-center justify-center flex-shrink-0">
              <Database className="w-10 h-10 text-primary-foreground" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h3 className="text-2xl font-bold mb-2">Custom Model Training</h3>
              <p className="text-muted-foreground">
                Need a specialized model for your research? Our platform supports custom model training 
                with your data. Contact us to discuss your requirements.
              </p>
            </div>
            <Button size="lg" variant="outline" className="border-primary hover:bg-primary/10">
              Request Training
            </Button>
          </div>
        </Card>
      </div>
    </section>
  );
};

export default MLModelsSection;