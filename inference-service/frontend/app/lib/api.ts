import { ChatSession, ChatSessionWithMessages, CreateSessionRequest, UpdateSessionRequest } from '../types/chat';

const API_BASE = 'http://localhost:8000/api';

export class ChatAPI {
  static async createSession(request: CreateSessionRequest = {}): Promise<ChatSession> {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create session');
    }
    
    return response.json();
  }

  static async getSessions(): Promise<ChatSession[]> {
    const response = await fetch(`${API_BASE}/sessions`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }
    
    return response.json();
  }

  static async getSession(sessionId: string): Promise<ChatSessionWithMessages> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch session');
    }
    
    return response.json();
  }

  static async updateSession(sessionId: string, request: UpdateSessionRequest): Promise<ChatSession> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update session');
    }
    
    return response.json();
  }

  static async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete session');
    }
  }
}
