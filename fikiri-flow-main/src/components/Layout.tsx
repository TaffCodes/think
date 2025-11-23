import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Bell, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        
        <div className="flex-1 flex flex-col">
          {/* Top Header */}
          <header className="sticky top-0 z-10 border-b bg-card shadow-soft">
            <div className="flex h-16 items-center gap-4 px-6">
              <SidebarTrigger className="transition-smooth" />
              
              <div className="flex-1 flex items-center gap-4 max-w-2xl">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search projects, equipment, requests..."
                    className="pl-10 bg-muted/50 border-0 focus-visible:ring-accent"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="h-5 w-5" />
                  <span className="absolute top-1 right-1 h-2 w-2 bg-accent rounded-full"></span>
                </Button>
                
                <div className="flex items-center gap-3 ml-2 pl-2 border-l">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium">Admin User</p>
                    <p className="text-xs text-muted-foreground">Administrator</p>
                  </div>
                  <div className="h-10 w-10 rounded-full bg-gradient-accent flex items-center justify-center text-sm font-bold text-accent-foreground">
                    AU
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Layout;
