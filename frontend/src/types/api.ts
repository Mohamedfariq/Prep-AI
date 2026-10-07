export interface User {
  id: string;
  name: string;
  email: string;
  graduation_year: number;
  branch: string;
}

export interface CandidateProfile {
  target_company?: string | null;
  overall_mastery: number;
  accuracy: number;
  average_time: number;
  questions_attempted: number;
  questions_solved: number;
  current_streak: number;
  resume_filename?: string | null;
  resume_signed_url?: string | null;
  parsed_skills?: string[];
  parsed_projects?: any[];
  parsed_education?: any[];
}

export interface SkillRow {
  topic: string;
  mastery_probability: number;
  attempts: number;
  correct: number;
  incorrect: number;
}

export interface Company {
  id?: string;
  company_id: string;
  name: string;
  logo: string;
  description: string;
  tier?: string;
  total_questions?: number;
  unique_questions?: number;
}

export interface Question {
  id?: string;
  question_id: string;
  question_key: string;
  title: string;
  leetcode_url: string;
  difficulty: string;
  topics: string[];
  frequency_percent: number;
  acceptance_rate_percent: number;
  companies: string[];
  status?: string;
}

export interface Recommendation {
  _id: string;
  question_id: string;
  question_key: string;
  title: string;
  topic: string;
  difficulty: string;
  company: string;
  company_relevance: number;
  score: number;
  reason: string;
  status: string;
}
