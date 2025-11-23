import { Project, CreateProjectData, TeamMember } from "@/types/project";

// TODO: Replace with your actual Django API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

// Mock data for development
const mockProjects: Project[] = [
  {
    id: 1,
    company_name: "Acme Corporation",
    status: "active",
    date_from: "2025-01-15",
    date_to: "2025-06-30",
    charges: 75000,
    services: ["Equipment Rental", "Maintenance"],
    description: "Large scale equipment rental project",
    allocated_team: [
      { id: 1, name: "John Doe", role: "Project Manager", email: "john@example.com" },
      { id: 2, name: "Jane Smith", role: "Technician", email: "jane@example.com" },
    ],
    created_at: "2025-01-10T10:00:00Z",
    updated_at: "2025-01-10T10:00:00Z",
  },
  {
    id: 2,
    company_name: "Tech Solutions Ltd",
    status: "pending",
    date_from: "2025-02-01",
    date_to: "2025-03-15",
    charges: 45000,
    services: ["Installation", "Training"],
    description: "Equipment installation and staff training",
    allocated_team: [],
    created_at: "2025-01-12T14:30:00Z",
    updated_at: "2025-01-12T14:30:00Z",
  },
  {
    id: 3,
    company_name: "Global Industries",
    status: "completed",
    date_from: "2024-10-01",
    date_to: "2024-12-31",
    charges: 120000,
    services: ["Equipment Rental", "Support", "Maintenance"],
    description: "Completed project with full service package",
    allocated_team: [
      { id: 3, name: "Mike Johnson", role: "Lead Engineer", email: "mike@example.com" },
    ],
    created_at: "2024-09-20T09:00:00Z",
    updated_at: "2025-01-05T16:00:00Z",
  },
];

const mockTeamMembers: TeamMember[] = [
  { id: 1, name: "John Doe", role: "Project Manager", email: "john@example.com" },
  { id: 2, name: "Jane Smith", role: "Technician", email: "jane@example.com" },
  { id: 3, name: "Mike Johnson", role: "Lead Engineer", email: "mike@example.com" },
  { id: 4, name: "Sarah Williams", role: "Equipment Specialist", email: "sarah@example.com" },
  { id: 5, name: "David Brown", role: "Field Supervisor", email: "david@example.com" },
];

// Simulated API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const projectsApi = {
  // Get all projects
  async getProjects(): Promise<Project[]> {
    await delay(500);
    // TODO: Replace with actual API call
    // const response = await fetch(`${API_BASE_URL}/projects/`, {
    //   headers: { Authorization: `Bearer ${token}` }
    // });
    // return response.json();
    return mockProjects;
  },

  // Get single project
  async getProject(id: number): Promise<Project> {
    await delay(500);
    const project = mockProjects.find(p => p.id === id);
    if (!project) throw new Error("Project not found");
    return project;
  },

  // Create project
  async createProject(data: CreateProjectData): Promise<Project> {
    await delay(500);
    // TODO: Replace with actual API call
    // const response = await fetch(`${API_BASE_URL}/projects/`, {
    //   method: 'POST',
    //   headers: { 
    //     'Content-Type': 'application/json',
    //     Authorization: `Bearer ${token}` 
    //   },
    //   body: JSON.stringify(data)
    // });
    // return response.json();
    const newProject: Project = {
      id: mockProjects.length + 1,
      ...data,
      status: data.status as any,
      allocated_team: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    mockProjects.push(newProject);
    return newProject;
  },

  // Get available team members
  async getTeamMembers(): Promise<TeamMember[]> {
    await delay(300);
    return mockTeamMembers;
  },

  // Allocate team members to project
  async allocateTeam(projectId: number, memberIds: number[]): Promise<Project> {
    await delay(500);
    // TODO: Replace with actual API call
    const project = mockProjects.find(p => p.id === projectId);
    if (!project) throw new Error("Project not found");
    
    project.allocated_team = mockTeamMembers.filter(m => memberIds.includes(m.id));
    project.updated_at = new Date().toISOString();
    return project;
  },
};
