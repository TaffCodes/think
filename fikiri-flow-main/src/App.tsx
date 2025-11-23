import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import CreateProject from "./pages/CreateProject";
import ProjectDetail from "./pages/ProjectDetail";
import Layout from "./components/Layout";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
          <Route path="/projects" element={<Layout><Projects /></Layout>} />
          <Route path="/projects/create" element={<Layout><CreateProject /></Layout>} />
          <Route path="/projects/:id" element={<Layout><ProjectDetail /></Layout>} />
          <Route path="/equipment" element={<Layout><div>Equipment Coming Soon</div></Layout>} />
          <Route path="/requests" element={<Layout><div>Requests Coming Soon</div></Layout>} />
          <Route path="/finance" element={<Layout><div>Finance Coming Soon</div></Layout>} />
          <Route path="/profile" element={<Layout><div>Profile Coming Soon</div></Layout>} />
          <Route path="/settings" element={<Layout><div>Settings Coming Soon</div></Layout>} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
