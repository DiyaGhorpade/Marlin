import { Card } from "@/components/ui/card";
import { BarChart3, TrendingUp, Activity, Fish } from "lucide-react";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const fishPopulationData = [
  { month: "Jan", tuna: 4200, salmon: 3800, cod: 2900 },
  { month: "Feb", tuna: 4500, salmon: 3600, cod: 3100 },
  { month: "Mar", tuna: 4800, salmon: 4100, cod: 3300 },
  { month: "Apr", tuna: 5100, salmon: 4400, cod: 3500 },
  { month: "May", tuna: 5400, salmon: 4700, cod: 3800 },
  { month: "Jun", tuna: 5800, salmon: 5000, cod: 4100 },
];

const temperatureData = [
  { month: "Jan", temp: 15.2 },
  { month: "Feb", temp: 15.8 },
  { month: "Mar", temp: 16.5 },
  { month: "Apr", temp: 17.2 },
  { month: "May", temp: 18.1 },
  { month: "Jun", temp: 19.3 },
];

const biodiversityData = [
  { species: "Coral", count: 340 },
  { species: "Fish", count: 520 },
  { species: "Mammals", count: 180 },
  { species: "Mollusks", count: 280 },
];

const DashboardsSection = () => {
  return (
    <section id="dashboards" className="py-24 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            <span className="bg-gradient-ocean bg-clip-text text-transparent">
              Interactive Dashboards
            </span>
          </h2>
          <p className="text-muted-foreground text-lg">
            Real-time visualization of marine data and analytics
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <Card className="p-6 shadow-card hover:shadow-ocean transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold mb-1">Fish Population Trends</h3>
                <p className="text-sm text-muted-foreground">Monthly population data by species</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-ocean flex items-center justify-center">
                <Fish className="w-6 h-6 text-primary-foreground" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={fishPopulationData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Line type="monotone" dataKey="tuna" stroke="hsl(var(--primary))" strokeWidth={2} />
                <Line type="monotone" dataKey="salmon" stroke="hsl(var(--secondary))" strokeWidth={2} />
                <Line type="monotone" dataKey="cod" stroke="hsl(var(--accent))" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card className="p-6 shadow-card hover:shadow-ocean transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold mb-1">Ocean Temperature</h3>
                <p className="text-sm text-muted-foreground">Average surface temperature (°C)</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-teal flex items-center justify-center">
                <Activity className="w-6 h-6 text-primary-foreground" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={temperatureData}>
                <defs>
                  <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--secondary))" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="hsl(var(--secondary))" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Area type="monotone" dataKey="temp" stroke="hsl(var(--secondary))" fillOpacity={1} fill="url(#tempGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6 shadow-card hover:shadow-ocean transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold mb-1">Biodiversity Index</h3>
                <p className="text-sm text-muted-foreground">Species count by category</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-primary" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={biodiversityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="species" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="count" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card className="p-6 shadow-card hover:shadow-ocean transition-shadow">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold mb-1">Key Metrics</h3>
                  <p className="text-sm text-muted-foreground">Live platform statistics</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-accent" />
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-gradient-to-r from-primary/10 to-primary/5">
                  <div className="text-sm text-muted-foreground mb-1">Total Species Monitored</div>
                  <div className="text-3xl font-bold text-primary">1,320</div>
                  <div className="text-xs text-accent mt-1">↑ 12% from last month</div>
                </div>

                <div className="p-4 rounded-lg bg-gradient-to-r from-secondary/10 to-secondary/5">
                  <div className="text-sm text-muted-foreground mb-1">Active Research Sites</div>
                  <div className="text-3xl font-bold text-secondary">87</div>
                  <div className="text-xs text-accent mt-1">↑ 5% from last month</div>
                </div>

                <div className="p-4 rounded-lg bg-gradient-to-r from-accent/10 to-accent/5">
                  <div className="text-sm text-muted-foreground mb-1">Data Points Collected</div>
                  <div className="text-3xl font-bold text-accent">524.8K</div>
                  <div className="text-xs text-accent mt-1">↑ 23% from last month</div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default DashboardsSection;
