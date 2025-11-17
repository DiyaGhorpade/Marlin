import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Waves, Mail, Lock } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

// Store credentials in component state (in real app, this would be in backend/database)
interface UserCredentials {
  email: string;
  password: string;
}

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState("");
  const [loading, setLoading] = useState(false);
  const [registeredUsers, setRegisteredUsers] = useState<UserCredentials[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  const validateEmail = (email: string) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError("");

    if (!validateEmail(email)) {
      setEmailError("Invalid email address");
      return;
    }

    if (password.length < 6) {
      toast({
        title: "Error",
        description: "Password must be at least 6 characters",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    try {
      if (isLogin) {
        // Sign in logic - Check if user exists with matching credentials
        const userExists = registeredUsers.find(
          user => user.email === email && user.password === password
        );

        if (userExists) {
          localStorage.setItem("token", "demo-token");
          localStorage.setItem("userEmail", email);
          toast({
            title: "Welcome back!",
            description: "Successfully logged in.",
          });
          navigate("/");
        } else {
          // Check if email exists but password is wrong
          const emailExists = registeredUsers.find(user => user.email === email);
          if (emailExists) {
            toast({
              title: "Login Failed",
              description: "Incorrect password",
              variant: "destructive",
            });
          } else {
            toast({
              title: "Login Failed",
              description: "No account found with this email",
              variant: "destructive",
            });
          }
        }
      } else {
        // Sign up logic - Check if email already exists
        const emailExists = registeredUsers.find(user => user.email === email);
        
        if (emailExists) {
          toast({
            title: "Signup Failed",
            description: "An account with this email already exists",
            variant: "destructive",
          });
        } else {
          // Register new user
          const newUser: UserCredentials = { email, password };
          setRegisteredUsers(prev => [...prev, newUser]);
          
          toast({
            title: "Account created!",
            description: "Your account has been created successfully.",
          });
          
          // Switch to login after successful signup
          setIsLogin(true);
          // Clear form
          setEmail("");
          setPassword("");
        }
      }
    } catch (error: any) {
      console.error("Auth Error:", error);
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-hero flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 shadow-ocean">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-xl bg-gradient-ocean flex items-center justify-center mb-4">
            <Waves className="w-8 h-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-ocean bg-clip-text text-transparent">
            Marlin
          </h1>
          <p className="text-muted-foreground mt-2">
            {isLogin ? "Welcome back" : "Create your account"}
          </p>
        </div>

        <form onSubmit={handleAuth} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setEmailError("");
                }}
                className="pl-10"
                required
              />
            </div>
            {emailError && <p className="text-destructive text-xs">{emailError}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10"
                required
              />
            </div>
          </div>

          <Button
            type="submit"
            className="w-full bg-gradient-ocean hover:opacity-90"
            disabled={loading}
          >
            {loading ? "Please wait..." : isLogin ? "Sign In" : "Sign Up"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setEmail("");
              setPassword("");
              setEmailError("");
            }}
            className="text-sm text-muted-foreground hover:text-primary transition-colors"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>

        {/* Demo helper - show registered users in development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-2 bg-muted rounded text-xs">
            <p className="font-medium">Demo Users ({registeredUsers.length}):</p>
            {registeredUsers.map((user, index) => (
              <p key={index}>{user.email}</p>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default Auth;