import { Button } from "@/components/ui/button";
import { Menu, Waves, MessageSquare, BarChart3, Brain, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/components/ui/use-toast";
import type { User } from "@supabase/supabase-js";

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );

    // Check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast({
      title: "Logged out",
      description: "Successfully logged out of your account.",
    });
    navigate("/auth");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-card/80 backdrop-blur-lg border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-ocean flex items-center justify-center">
              <Waves className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold bg-gradient-ocean bg-clip-text text-transparent">
              Marlin
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link to="/" className="text-foreground hover:text-primary transition-colors">
              Home
            </Link>
            <Link to="/chatbot" className="text-foreground hover:text-primary transition-colors flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              AI Chatbot
            </Link>
            <Link to="/dashboards" className="text-foreground hover:text-primary transition-colors flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Dashboards
            </Link>
            <Link to="/models" className="text-foreground hover:text-primary transition-colors flex items-center gap-2">
              <Brain className="w-4 h-4" />
              ML Models
            </Link>
            {user ? (
              <Button onClick={handleLogout} variant="outline" className="flex items-center gap-2">
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            ) : (
              <Button onClick={() => navigate("/auth")} className="bg-gradient-ocean hover:opacity-90">
                Sign In
              </Button>
            )}
          </div>

          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>

          {isOpen && (
          <div className="md:hidden py-4 space-y-3">
            <Link to="/" className="block text-foreground hover:text-primary transition-colors">
              Home
            </Link>
            <Link to="/chatbot" className="block text-foreground hover:text-primary transition-colors">
              AI Chatbot
            </Link>
            <Link to="/dashboards" className="block text-foreground hover:text-primary transition-colors">
              Dashboards
            </Link>
            <Link to="/models" className="block text-foreground hover:text-primary transition-colors">
              ML Models
            </Link>
            {user ? (
              <Button onClick={handleLogout} variant="outline" className="w-full flex items-center gap-2">
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            ) : (
              <Button onClick={() => navigate("/auth")} className="w-full bg-gradient-ocean hover:opacity-90">
                Sign In
              </Button>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
