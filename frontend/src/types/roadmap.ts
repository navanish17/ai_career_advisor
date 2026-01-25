export interface ForwardRoadmapRequest {
  degree_id: number;
  branch_id: number;
  career_id: number;
}

export interface ForwardRoadmapResponse {
  message: string;
  roadmap_id: number;
}

export interface BackwardRoadmapRequest {
  career_goal: string;
}

export interface BackwardRoadmapData {
  id?: number;
  career_goal_input: string;
  normalized_career: string;
  career_category?: string | null;
  career_description?: string | null;
  required_education?: {
    degree_options?: string[];
    minimum_degree?: string;
    preferred_degree?: string;
    specialization?: string;
  } | null;
  entrance_exams?: Array<{
    exam_name: string;
    for: string;
    difficulty: string;
    when_to_prepare: string;
  }> | null;
  stream_recommendation?: {
    class_11_12: string;
    reason: string;
    alternatives?: string[];
  } | null;
  skills_required?: Array<{
    skill: string;
    level: string;
    description?: string;
    languages?: string[];
  }> | null;
  projects_to_build?: string[] | null;
  internships?: Array<{
    type: string;
    when: string;
    duration: string;
    focus: string;
  }> | null;
  certifications?: Array<{
    name: string;
    provider: string;
  }> | null;
  top_colleges?: Array<{
    name: string;
    nirf_rank_engineering?: number;
    nirf_rank_university?: number;
    type: string;
    admission_via: string;
  }> | null;
  career_prospects?: {
    entry_level_salary_range_lpa?: string;
    mid_level_salary_range_lpa?: string;
    senior_level_salary_range_lpa?: string;
    growth_potential?: string;
    job_market_demand?: string;
    specializations?: string[];
  } | null;
  timeline?: {
    class_10?: TimelinePhase;
    class_11_12?: TimelinePhase;
    bachelor_degree_year_1?: TimelinePhase;
    bachelor_degree_year_2?: TimelinePhase;
    bachelor_degree_year_3?: TimelinePhase;
    bachelor_degree_year_4?: TimelinePhase;
    post_graduation?: TimelinePhase;
  } | null;
  source: string;
  confidence_score?: number | null;
  created_at?: string | null;
}

export interface TimelinePhase {
  focus: string;
  action_items: string[];
  exam_focus?: string;
}

export interface BackwardRoadmapResponse {
  success: boolean;
  source: string;
  roadmap: BackwardRoadmapData;
}

export interface GetRoadmapResponse {
  id: number;
  user_id: number;
  degree_id: number;
  branch_id: number;
  career_id: number;
  created_at: string;

}

export type AvailableTemplatesResponse = string[];
