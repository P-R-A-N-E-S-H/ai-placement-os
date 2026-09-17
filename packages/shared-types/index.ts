/**
 * AI PlacementOS - Shared TypeScript Interfaces & Enums
 */

export type UserRole = "student" | "mentor" | "admin";

export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  institution?: string;
  degree?: string;
  branch?: string;
  cgpa?: number;
  graduationYear?: number;
  targetRoles: string[];
  skills: string[];
  createdAt: string;
  updatedAt: string;
}

export interface ResumeAnalysisResult {
  resumeId: string;
  atsScore: number;
  skillsExtracted: string[];
  experienceYears: number;
  sectionScores: {
    contactInfo: number;
    education: number;
    skills: number;
    experience: number;
    projects: number;
  };
  suggestedImprovements: string[];
}

export interface JobMatchBreakdown {
  overallScore: number;
  semanticSimilarity: number;
  requiredSkillMatch: number;
  preferredSkillMatch: number;
  experienceMatch: number;
  projectMatch: number;
  educationMatch: number;
  matchedSkills: string[];
  missingSkills: string[];
  explanation: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
    requestId: string;
  };
}
