import { 
  LayoutDashboard, 
  FolderKanban, 
  Package, 
  ClipboardList, 
  Wallet, 
  User, 
  Settings,
  ChevronRight
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
  SidebarHeader,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Building2 } from "lucide-react";

const mainItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Projects", url: "/projects", icon: FolderKanban },
  { title: "Equipment", url: "/equipment", icon: Package },
  { title: "Requests", url: "/requests", icon: ClipboardList },
  { title: "Finance", url: "/finance", icon: Wallet },
];

const bottomItems = [
  { title: "Profile", url: "/profile", icon: User },
  { title: "Settings", url: "/settings", icon: Settings },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const location = useLocation();
  const isCollapsed = state === "collapsed";
  
  const isActive = (path: string) => location.pathname === path;
  
  const getNavClass = (active: boolean) => {
    return active 
      ? "bg-sidebar-accent text-sidebar-primary font-semibold" 
      : "hover:bg-sidebar-accent/50 text-sidebar-foreground";
  };

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border">
      <SidebarHeader className="border-b border-sidebar-border py-4">
        <div className="flex items-center gap-3 px-3">
          <div className="rounded-lg bg-sidebar-primary p-2">
            <Building2 className="h-5 w-5 text-sidebar-primary-foreground" />
          </div>
          {!isCollapsed && (
            <div>
              <h2 className="text-lg font-bold text-sidebar-foreground">FikiriERP</h2>
              <p className="text-xs text-sidebar-foreground/70">Enterprise System</p>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent className="py-4">
        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 px-3">
            {!isCollapsed && "Main Menu"}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    asChild 
                    tooltip={item.title}
                    className={getNavClass(isActive(item.url))}
                  >
                    <NavLink to={item.url} className="flex items-center gap-3">
                      <item.icon className="h-5 w-5" />
                      <span className="flex-1">{item.title}</span>
                      {!isCollapsed && isActive(item.url) && (
                        <ChevronRight className="h-4 w-4 text-sidebar-primary" />
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border py-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {bottomItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    asChild 
                    tooltip={item.title}
                    className={getNavClass(isActive(item.url))}
                  >
                    <NavLink to={item.url} className="flex items-center gap-3">
                      <item.icon className="h-5 w-5" />
                      <span>{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarFooter>
    </Sidebar>
  );
}
