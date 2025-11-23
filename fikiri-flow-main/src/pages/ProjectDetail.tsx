import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { projectsApi } from "@/api/projects";
import { Project } from "@/types/project";
import { useToast } from "@/hooks/use-toast";
import AllocateTeamModal from "@/components/AllocateTeamModal";

const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAllocateModal, setShowAllocateModal] = useState(false);

  useEffect(() => {
    if (id) {
      fetchProject();
    }
  }, [id]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const data = await projectsApi.getProject(Number(id));
      setProject(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load project details",
        variant: "destructive",
      });
      navigate("/projects");
    } finally {
      setLoading(false);
    }
  };

  const handleTeamAllocated = (updatedProject: Project) => {
    setProject(updatedProject);
    setShowAllocateModal(false);
    toast({
      title: "Success",
      description: "Team members allocated successfully",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-primary text-primary-foreground";
      case "pending":
        return "bg-accent text-accent-foreground";
      case "completed":
        return "bg-secondary text-secondary-foreground";
      case "cancelled":
        return "bg-destructive text-destructive-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <p className="text-center text-muted-foreground">Loading project...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container mx-auto py-8 px-4">
        <p className="text-center text-muted-foreground">Project not found</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <Button
        variant="ghost"
        onClick={() => navigate("/projects")}
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Projects
      </Button>

      {/* Project Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            {project.company_name}
          </h1>
          <Badge className={getStatusColor(project.status)}>
            {project.status}
          </Badge>
        </div>
        <Button variant="accent" onClick={() => setShowAllocateModal(true)}>
          <Users className="mr-2 h-4 w-4" />
          Allocate Team
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Project Information */}
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Company Name</p>
              <p className="font-medium">{project.company_name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Project Duration</p>
              <p className="font-medium">
                {new Date(project.date_from).toLocaleDateString()} -{" "}
                {new Date(project.date_to).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Charges</p>
              <p className="text-2xl font-bold text-accent">
                KES {project.charges.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-2">Services</p>
              <div className="flex flex-wrap gap-2">
                {project.services.map((service, idx) => (
                  <Badge key={idx} variant="outline">
                    {service}
                  </Badge>
                ))}
              </div>
            </div>
            {project.description && (
              <div>
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="text-sm mt-1">{project.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Allocated Team */}
        <Card>
          <CardHeader>
            <CardTitle>Allocated Team</CardTitle>
          </CardHeader>
          <CardContent>
            {project.allocated_team && project.allocated_team.length > 0 ? (
              <div className="space-y-3">
                {project.allocated_team.map((member) => (
                  <div
                    key={member.id}
                    className="p-3 border rounded-lg bg-muted/50"
                  >
                    <p className="font-medium">{member.name}</p>
                    <p className="text-sm text-muted-foreground">{member.role}</p>
                    <p className="text-sm text-muted-foreground">{member.email}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">No team members allocated yet</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => setShowAllocateModal(true)}
                >
                  Allocate Team Members
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Metadata */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <div className="flex gap-8 text-sm text-muted-foreground">
            <div>
              <span>Created: </span>
              <span className="font-medium">
                {new Date(project.created_at).toLocaleString()}
              </span>
            </div>
            <div>
              <span>Last Updated: </span>
              <span className="font-medium">
                {new Date(project.updated_at).toLocaleString()}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Allocate Team Modal */}
      {showAllocateModal && (
        <AllocateTeamModal
          project={project}
          onClose={() => setShowAllocateModal(false)}
          onSuccess={handleTeamAllocated}
        />
      )}
    </div>
  );
};

export default ProjectDetail;
