export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  first_message_preview?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
  session_id: string;
}

export interface ChatSessionWithMessages {
  session: ChatSession;
  messages: ChatMessage[];
}

export interface CreateSessionRequest {
  title?: string;
}

export interface UpdateSessionRequest {
  title: string;
}
