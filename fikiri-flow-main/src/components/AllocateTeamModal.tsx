import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { projectsApi } from "@/api/projects";
import { Project, TeamMember } from "@/types/project";
import { useToast } from "@/hooks/use-toast";

interface AllocateTeamModalProps {
  project: Project;
  onClose: () => void;
  onSuccess: (updatedProject: Project) => void;
}

const AllocateTeamModal = ({ project, onClose, onSuccess }: AllocateTeamModalProps) => {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [selectedMembers, setSelectedMembers] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchTeamMembers();
    // Pre-select already allocated members
    if (project.allocated_team) {
      setSelectedMembers(project.allocated_team.map((m) => m.id));
    }
  }, []);

  const fetchTeamMembers = async () => {
    try {
      const members = await projectsApi.getTeamMembers();
      setTeamMembers(members);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load team members",
        variant: "destructive",
      });
    }
  };

  const handleToggleMember = (memberId: number) => {
    setSelectedMembers((prev) =>
      prev.includes(memberId)
        ? prev.filter((id) => id !== memberId)
        : [...prev, memberId]
    );
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const updatedProject = await projectsApi.allocateTeam(
        project.id,
        selectedMembers
      );
      onSuccess(updatedProject);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to allocate team members",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-lg shadow-elegant max-w-2xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold">Allocate Team Members</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[50vh]">
          <p className="text-sm text-muted-foreground mb-4">
            Select team members to allocate to <strong>{project.company_name}</strong>
          </p>
          <div className="space-y-3">
            {teamMembers.map((member) => (
              <div
                key={member.id}
                className="flex items-start gap-3 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer"
                onClick={() => handleToggleMember(member.id)}
              >
                <Checkbox
                  checked={selectedMembers.includes(member.id)}
                  onCheckedChange={() => handleToggleMember(member.id)}
                />
                <div className="flex-1">
                  <p className="font-medium">{member.name}</p>
                  <p className="text-sm text-muted-foreground">{member.role}</p>
                  <p className="text-sm text-muted-foreground">{member.email}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="accent" onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Save Allocation"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AllocateTeamModal;
