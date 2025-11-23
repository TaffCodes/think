import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  ClipboardList, 
  Calendar, 
  Package, 
  TrendingUp, 
  Users,
  FolderKanban,
  AlertCircle,
  CheckCircle
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

const Dashboard = () => {
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, Admin!</h1>
          <p className="text-muted-foreground mt-1">
            Here's what's happening with your projects today.
          </p>
        </div>
        <Button variant="accent" size="lg" className="w-fit">
          <ClipboardList className="h-5 w-5 mr-2" />
          Make a Request
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="shadow-soft hover:shadow-medium transition-smooth">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Projects
            </CardTitle>
            <FolderKanban className="h-5 w-5 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">12</div>
            <p className="text-xs text-muted-foreground mt-1">
              <span className="text-accent font-medium">+2</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-soft hover:shadow-medium transition-smooth">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Equipment Available
            </CardTitle>
            <Package className="h-5 w-5 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">342</div>
            <p className="text-xs text-muted-foreground mt-1">
              <span className="text-muted-foreground">67 committed</span>
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-soft hover:shadow-medium transition-smooth">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pending Requests
            </CardTitle>
            <AlertCircle className="h-5 w-5 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">8</div>
            <p className="text-xs text-muted-foreground mt-1">
              Requires your approval
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-soft hover:shadow-medium transition-smooth">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Team Members
            </CardTitle>
            <Users className="h-5 w-5 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">24</div>
            <p className="text-xs text-muted-foreground mt-1">
              Across all projects
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ongoing Assignments */}
        <Card className="shadow-soft">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Ongoing Assignments</CardTitle>
                <CardDescription>Active project deployments</CardDescription>
              </div>
              <Button variant="ghost" size="sm">View All</Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { 
                project: "Safari Lodge Installation", 
                client: "Maasai Mara Resort",
                status: "In Progress",
                progress: 65,
                daysLeft: 5
              },
              { 
                project: "Conference Setup", 
                client: "Nairobi Convention Center",
                status: "Starting Soon",
                progress: 20,
                daysLeft: 2
              },
              { 
                project: "Network Infrastructure", 
                client: "Tech Campus Hub",
                status: "In Progress",
                progress: 80,
                daysLeft: 3
              },
            ].map((assignment, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:bg-muted/50 transition-smooth">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold">{assignment.project}</h4>
                    <p className="text-sm text-muted-foreground">{assignment.client}</p>
                  </div>
                  <Badge variant={assignment.status === "In Progress" ? "default" : "secondary"}>
                    {assignment.status}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">{assignment.progress}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-accent h-2 rounded-full transition-all" 
                      style={{ width: `${assignment.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {assignment.daysLeft} days remaining
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Upcoming Events */}
        <Card className="shadow-soft">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Upcoming Events</CardTitle>
                <CardDescription>Schedule for this week</CardDescription>
              </div>
              <Button variant="ghost" size="sm">View Calendar</Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { 
                title: "Equipment Check-in", 
                project: "Safari Lodge Installation",
                date: "Today",
                time: "2:00 PM",
                type: "check-in"
              },
              { 
                title: "Project Kickoff Meeting", 
                project: "Conference Setup",
                date: "Tomorrow",
                time: "10:00 AM",
                type: "meeting"
              },
              { 
                title: "Client Presentation", 
                project: "Tech Campus Hub",
                date: "Nov 3",
                time: "3:30 PM",
                type: "presentation"
              },
              { 
                title: "Equipment Delivery", 
                project: "Hotel Renovation Project",
                date: "Nov 4",
                time: "9:00 AM",
                type: "delivery"
              },
            ].map((event, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:bg-muted/50 transition-smooth">
                <div className="flex gap-4">
                  <div className="flex flex-col items-center justify-center bg-accent/10 rounded-lg px-3 py-2 min-w-[60px]">
                    <span className="text-xs font-medium text-accent">{event.date}</span>
                    <span className="text-sm font-bold text-accent-foreground">{event.time}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold">{event.title}</h4>
                        <p className="text-sm text-muted-foreground">{event.project}</p>
                      </div>
                      {event.type === "check-in" && (
                        <CheckCircle className="h-5 w-5 text-accent" />
                      )}
                      {event.type === "meeting" && (
                        <Calendar className="h-5 w-5 text-accent" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="shadow-soft">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and operations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <FolderKanban className="h-6 w-6 text-accent" />
              <span className="text-sm">New Project</span>
            </Button>
            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <ClipboardList className="h-6 w-6 text-accent" />
              <span className="text-sm">View Requests</span>
            </Button>
            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <Package className="h-6 w-6 text-accent" />
              <span className="text-sm">Check Inventory</span>
            </Button>
            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <TrendingUp className="h-6 w-6 text-accent" />
              <span className="text-sm">Finance Report</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
