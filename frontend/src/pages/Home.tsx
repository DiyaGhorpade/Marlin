import Navigation from "@/components/Navigation";
import HeroSection from "@/components/HeroSection";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <HeroSection />
      
      <footer className="bg-ocean-deep text-primary-foreground py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h4 className="font-bold text-lg mb-4">Marlin Platform</h4>
              <p className="text-sm opacity-80">
                AI-driven unified data platform for oceanographic fisheries and marine biodiversity insights.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Features</h4>
              <ul className="space-y-2 text-sm opacity-80">
                <Link to="/chatbot" className="block hover:opacity-100 transition-opacity">
                  AI Chatbot
                </Link>
                <Link to="/dashboards" className="block hover:opacity-100 transition-opacity">
                  Interactive Dashboards
                </Link>
                <Link to="/models" className="block hover:opacity-100 transition-opacity">
                  ML Models
                </Link>
                <li>Real-time Analytics</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Resources</h4>
              <ul className="space-y-2 text-sm opacity-80">
                <a href="https://docs.lovable.dev" target="_blank" rel="noopener noreferrer" className="block hover:opacity-100 transition-opacity">
                  Documentation
                </a>
                <a href="https://docs.lovable.dev/features/cloud" target="_blank" rel="noopener noreferrer" className="block hover:opacity-100 transition-opacity">
                  API Reference
                </a>
                <a href="https://docs.lovable.dev" target="_blank" rel="noopener noreferrer" className="block hover:opacity-100 transition-opacity">
                  Tutorials
                </a>
                <a href="https://docs.lovable.dev" target="_blank" rel="noopener noreferrer" className="block hover:opacity-100 transition-opacity">
                  Research Papers
                </a>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Contact</h4>
              <ul className="space-y-2 text-sm opacity-80">
                <a href="mailto:support@marlin.ai" className="block hover:opacity-100 transition-opacity">
                  support@marlin.ai
                </a>
                <a href="tel:+15551234567" className="block hover:opacity-100 transition-opacity">
                  +1 (555) 123-4567
                </a>
                <a href="mailto:partnerships@marlin.ai" className="block hover:opacity-100 transition-opacity">
                  Research Partnerships
                </a>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-primary-foreground/20 text-center text-sm opacity-80">
            © 2024 Marlin Platform. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
