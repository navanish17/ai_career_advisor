export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  context?: {
    class_level?: string;
    stream?: string;
    interests?: string[];
  };
}

export interface ChatResponse {
  response: string;
  intent?: string;
  confidence?: number;
}
