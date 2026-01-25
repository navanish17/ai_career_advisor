export interface QuizQuestion {
  id: number;
  question_text: string;
  options: QuizOption[];
}

export interface QuizOption {
  id: number;
  option_text: string;
}

export interface QuizAnswer {
  question_id: number;
  selected_option_id: number;
}

export interface QuizSubmission {
  answers: QuizAnswer[];
}

export interface QuizResult {
  recommended_stream: string;
  confidence_score: number;
  explanation: string;
}

export interface Degree {
  id: number;
  name: string;
  stream: string;
  short_description: string | null;
  duration_years: number | null;
  eligibility: string | null;
  is_active: boolean;
}

export interface Branch {
  id: number;
  name: string;
  degree_id: number;
}

export interface Career {
  id: number;
  name: string;
  description: string | null;
  market_trend: string | null;
  salary_range: string | null;
}

export interface CareerInsight {
  career_id: number;
  skills: string[];
  internships: string[];
  projects: Record<string, string[]>;
  programs: string[];
}
