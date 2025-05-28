"use client";

import { useState, useEffect } from 'react';
import { ChatSession } from '../../../types/chat';
import { ChatAPI } from '../../../lib/api';

interface SessionSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentSessionId?: string;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
}

export default function SessionSidebar({ 
  isOpen, 
  onClose, 
  currentSessionId, 
  onSessionSelect, 
  onNewChat 
}: SessionSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const loadSessions = async () => {
    try {
      setLoading(true);
      const sessionList = await ChatAPI.getSessions();
      setSessions(sessionList);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load sessions list when component mounts
  useEffect(() => {
    loadSessions();
  }, []);

  // Refresh sessions list when sidebar opens
  useEffect(() => {
    if (isOpen) {
      loadSessions();
    }
  }, [isOpen]);

  const handleNewChat = async () => {
    // Simply trigger the parent's onNewChat without creating a session
    // This will clear the current state and show the welcome screen
    onNewChat();
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    // Add confirmation before deletion
    const confirmed = window.confirm("Are you sure you want to delete this chat session?");
    if (!confirmed) return;
    
    try {
      await ChatAPI.deleteSession(sessionId);
      setSessions(sessions.filter(s => s.id !== sessionId));
      
      // If the deleted session is the current one, clear the current state
      // This prevents residual messages from showing up
      if (currentSessionId === sessionId) {
        // Use onNewChat to create a fresh session with no messages
        onNewChat();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const handleEditTitle = async (sessionId: string) => {
    if (!editTitle.trim()) return;
    
    try {
      const updatedSession = await ChatAPI.updateSession(sessionId, { title: editTitle });
      setSessions(sessions.map(s => s.id === sessionId ? updatedSession : s));
      setEditingId(null);
      setEditTitle('');
    } catch (error) {
      console.error('Failed to update session title:', error);
    }
  };

  const startEditing = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditTitle(session.title);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <>
      {/* 遮罩层 */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* 侧边栏 */}
      <div className={`
        fixed left-0 top-0 h-full w-80 bg-gray-900 text-white z-50 transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0 lg:z-auto
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold">Chat History</h2>
          <button
            onClick={onClose}
            className="lg:hidden p-1 hover:bg-gray-700 rounded"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New chat button */}
        <div className="p-4">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Session list */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-400">Loading...</div>
          ) : sessions.length === 0 ? (
            <div className="p-4 text-center text-gray-400">No chat history</div>
          ) : (
            <div className="space-y-1 p-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => onSessionSelect(session.id)}
                  className={`
                    group relative p-3 rounded-lg cursor-pointer transition-colors
                    ${currentSessionId === session.id 
                      ? 'bg-gray-700 border border-gray-600' 
                      : 'hover:bg-gray-800'
                    }
                  `}
                >
                  {editingId === session.id ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onBlur={() => handleEditTitle(session.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleEditTitle(session.id);
                        if (e.key === 'Escape') {
                          setEditingId(null);
                          setEditTitle('');
                        }
                      }}
                      className="w-full bg-gray-600 text-white px-2 py-1 rounded"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-sm truncate">{session.title}</h3>
                          {session.first_message_preview && (
                            <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                              {session.first_message_preview}
                            </p>
                          )}
                          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                            <span>{session.message_count} messages</span>
                            <span>•</span>
                            <span>{formatDate(session.updated_at)}</span>
                          </div>
                        </div>
                        
                        {/* Action buttons */}
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => startEditing(session, e)}
                            className="p-1 hover:bg-gray-600 rounded"
                            title="Rename"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => handleDeleteSession(session.id, e)}
                            className="p-1 hover:bg-red-600 rounded"
                            title="Delete"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
