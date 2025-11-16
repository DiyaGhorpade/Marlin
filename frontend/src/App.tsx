import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Chatbot from "./pages/Chatbot";
import Dashboards from "./pages/Dashboards";
import Models from "./pages/Models";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";
import SpeciesRichnessPredictor from './pages/SpeciesRichnessPredictor';

// ✅ Import new dashboard pages
import OceanographicDashboard from "./pages/OceanographicDashboard";
import FisheriesDashboard from "./pages/FisheriesDashboard";
import MarineBiodiversityDashboard from "./pages/MarineBiodiversityDashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Main routes */}
          <Route path="/" element={<Home />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="/dashboards" element={<Dashboards />} />
          <Route path="/models" element={<Models />} />
          <Route path="/auth" element={<Auth />} />

          {/* ✅ Custom Dashboard Pages */}
          <Route path="/dashboards/oceanographic" element={<OceanographicDashboard />} />
          <Route path="/dashboards/fisheries" element={<FisheriesDashboard />} />
          <Route path="/dashboards/biodiversity" element={<MarineBiodiversityDashboard />} />
          <Route path="/species-richness-predictor" element={<SpeciesRichnessPredictor />} />
          {/* Catch-all route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
