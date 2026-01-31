// College Finder Types
export interface CollegeFinderRequest {
  state: string;
  degree: string;
  branch: string;
}

export interface CollegeBasic {
  id: number;
  name: string;
  location?: string;
  established?: number;
  nirf_rank?: number;
  status?: string;
  offers_program?: boolean | null;
  message?: string;
  reason?: string;
  fees?: string;
  avg_package?: string;
  highest_package?: string;
  entrance_exam?: string;
  cutoff?: string;
}

export interface CollegeDetail extends CollegeBasic {
  duration?: string;
  seats?: number;
  top_recruiters?: string[];
  official_website?: string;
  // Include extracted text for robustness
  fees_source?: string;
  avg_package_source?: string;
  highest_package_source?: string;
  entrance_exam_source?: string;
  cutoff_source?: string;
}

export interface CollegeFinderResponse {
  message: string;
  total_colleges: number;
  colleges: CollegeBasic[];
}

export interface CollegeDetailRequest {
  college_id: number;
  degree: string;
  branch: string;
}

// Entrance Exam Types
export interface EntranceExam {
  id: number;
  exam_name: string;
  exam_full_name?: string;
  conducting_body?: string;
  exam_date?: string;
  registration_start_date?: string;
  registration_end_date?: string;
  exam_pattern?: string;
  official_website?: string;
  syllabus_link?: string;
  academic_year?: string;
  is_active: boolean;
}

export interface EntranceExamSearchRequest {
  college_name: string;
  degree: string;
  branch?: string;
}

// Admission Alert Types
export interface CreateAlertRequest {
  user_email: string;
  college_name: string;
  degree: string;
  branch?: string;
  alert_types?: string[];
}

export interface Alert {
  id: number;
  user_email: string;
  entrance_exam_id: number;
  alert_type: string;
  alert_date: string;
  is_sent: boolean;
  college_name?: string;
  degree?: string;
  branch?: string;
  created_at: string;
}

export interface AlertResponse {
  success: boolean;
  message: string;
  exam: EntranceExam;
  alert?: Alert;
}

// Alert type options
export const ALERT_TYPES = [
  { value: 'registration_start', label: 'Registration Opens' },
  { value: 'registration_3days', label: '3 Days Before Deadline' },
  { value: 'registration_last', label: 'Last Day Reminder' },
  { value: 'exam_1day', label: '1 Day Before Exam' },
] as const;

export type AlertType = typeof ALERT_TYPES[number]['value'];
