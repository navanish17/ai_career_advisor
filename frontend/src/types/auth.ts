// Matches UserResponse from FastAPI
export interface User {
  id: number;
  name: string;
  email: string;
  isOnboarded?: boolean; // Frontend-only flag based on profile existence
}

// Signup response (user only, no token)
export interface SignupResponse {
  id: number;
  name: string;
  email: string;
}

// Login response (token only)
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// Legacy type for backward compatibility
export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

// ProfileResponse from FastAPI
export interface Profile {
  id: number;
  user_id: number;
  class_level: string | null;
  location: string | null;
  stream: string | null;
  language: string | null;
  known_interests: string[] | null;
}

export interface User {
  id: number;
  name: string;
  email: string;
  isOnboarded?: boolean;
  class_level?: string | null;
  stream?: string | null;
  location?: string | null;
  language?: string | null;
}