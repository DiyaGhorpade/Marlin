import Navigation from "@/components/Navigation";
import MLModelsSection from "@/components/MLModelsSection";

const Models = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="pt-16">
        <MLModelsSection />
      </div>
    </div>
  );
};

export default Models;
