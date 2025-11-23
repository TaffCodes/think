export interface Project {
  id: number;
  company_name: string;
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  date_from: string;
  date_to: string;
  charges: number;
  services: string[];
  description?: string;
  allocated_team?: TeamMember[];
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: number;
  name: string;
  role: string;
  email: string;
}

export interface CreateProjectData {
  company_name: string;
  status: string;
  date_from: string;
  date_to: string;
  charges: number;
  services: string[];
  description?: string;
}
