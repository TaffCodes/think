import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { projectsApi } from "@/api/projects";
import { CreateProjectData } from "@/types/project";
import { useToast } from "@/hooks/use-toast";

const CreateProject = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CreateProjectData>({
    company_name: "",
    status: "pending",
    date_from: "",
    date_to: "",
    charges: 0,
    services: [],
    description: "",
  });
  const [serviceInput, setServiceInput] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.company_name || !formData.date_from || !formData.date_to) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await projectsApi.createProject(formData);
      toast({
        title: "Success",
        description: "Project created successfully",
      });
      navigate("/projects");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create project",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddService = () => {
    if (serviceInput.trim() && !formData.services.includes(serviceInput.trim())) {
      setFormData({
        ...formData,
        services: [...formData.services, serviceInput.trim()],
      });
      setServiceInput("");
    }
  };

  const handleRemoveService = (service: string) => {
    setFormData({
      ...formData,
      services: formData.services.filter((s) => s !== service),
    });
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <Button
        variant="ghost"
        onClick={() => navigate("/projects")}
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Projects
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Create New Project</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="company_name">Company Name *</Label>
              <Input
                id="company_name"
                value={formData.company_name}
                onChange={(e) =>
                  setFormData({ ...formData, company_name: e.target.value })
                }
                required
              />
            </div>

            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground"
              >
                <option value="pending">Pending</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="date_from">Start Date *</Label>
                <Input
                  id="date_from"
                  type="date"
                  value={formData.date_from}
                  onChange={(e) =>
                    setFormData({ ...formData, date_from: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="date_to">End Date *</Label>
                <Input
                  id="date_to"
                  type="date"
                  value={formData.date_to}
                  onChange={(e) =>
                    setFormData({ ...formData, date_to: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="charges">Charges (KES)</Label>
              <Input
                id="charges"
                type="number"
                value={formData.charges}
                onChange={(e) =>
                  setFormData({ ...formData, charges: Number(e.target.value) })
                }
                min="0"
              />
            </div>

            <div>
              <Label htmlFor="services">Services</Label>
              <div className="flex gap-2 mb-2">
                <Input
                  id="services"
                  value={serviceInput}
                  onChange={(e) => setServiceInput(e.target.value)}
                  placeholder="Enter service name"
                  onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddService())}
                />
                <Button type="button" onClick={handleAddService} variant="outline">
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.services.map((service) => (
                  <span
                    key={service}
                    className="bg-secondary text-secondary-foreground px-3 py-1 rounded-md text-sm flex items-center gap-2"
                  >
                    {service}
                    <button
                      type="button"
                      onClick={() => handleRemoveService(service)}
                      className="text-destructive hover:text-destructive/80"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={4}
              />
            </div>

            <div className="flex gap-4">
              <Button type="submit" variant="accent" disabled={loading} className="flex-1">
                {loading ? "Creating..." : "Create Project"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/projects")}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateProject;
