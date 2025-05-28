"use client";

import { useState, useEffect } from "react";
import { ChevronDownIcon, ChevronRightIcon, PlusIcon, TrashIcon, PencilIcon } from "@heroicons/react/24/outline";

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  first_message_preview?: string;
}

interface ChatSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
  currentSessionId?: string;
}

const API_BASE_URL = "http://localhost:8000";

export default function ChatSidebar({ 
  isOpen, 
  onToggle, 
  onSessionSelect, 
  onNewChat,
  currentSessionId 
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  // 获取会话列表
  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/sessions`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      }
    } catch (error) {
      console.error("Failed to fetch sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  // 创建新会话
  const handleNewChat = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: `新聊天 ${new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`
        }),
      });
      
      if (response.ok) {
        const newSession = await response.json();
        setSessions(prev => [newSession, ...prev]);
        onSessionSelect(newSession.id);
        onNewChat();
      }
    } catch (error) {
      console.error("Failed to create new session:", error);
    }
  };

  // 删除会话
  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("确定要删除这个聊天吗？")) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
        method: "DELETE",
      });
      
      if (response.ok) {
        setSessions(prev => prev.filter(s => s.id !== sessionId));
        if (currentSessionId === sessionId) {
          onNewChat(); // 如果删除的是当前会话，创建新会话
        }
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  // 开始编辑标题
  const startEditing = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
  };

  // 保存编辑的标题
  const saveTitle = async () => {
    if (!editingSessionId || !editingTitle.trim()) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/${editingSessionId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: editingTitle.trim()
        }),
      });
      
      if (response.ok) {
        const updatedSession = await response.json();
        setSessions(prev => prev.map(s => s.id === editingSessionId ? updatedSession : s));
      }
    } catch (error) {
      console.error("Failed to update session:", error);
    } finally {
      setEditingSessionId(null);
      setEditingTitle("");
    }
  };

  // 取消编辑
  const cancelEditing = () => {
    setEditingSessionId(null);
    setEditingTitle("");
  };

  useEffect(() => {
    if (isOpen) {
      fetchSessions();
    }
  }, [isOpen]);

  return (
    <>
      {/* 背景遮罩 */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* 侧边栏 */}
      <div className={`
        fixed top-0 left-0 h-full bg-gray-900 text-white z-50 transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        w-80 lg:w-72
      `}>
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold">聊天记录</h2>
          <button
            onClick={onToggle}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <ChevronRightIcon className="w-5 h-5" />
          </button>
        </div>

        {/* 新建聊天按钮 */}
        <div className="p-4 border-b border-gray-700">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-3 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <PlusIcon className="w-5 h-5" />
            <span>新建聊天</span>
          </button>
        </div>

        {/* 会话列表 */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-400">
              <div className="animate-spin w-6 h-6 border-2 border-white border-t-transparent rounded-full mx-auto"></div>
              <p className="mt-2">加载中...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <p>暂无聊天记录</p>
              <p className="text-sm mt-1">创建新聊天开始对话</p>
            </div>
          ) : (
            <div className="p-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`
                    group relative p-3 mb-2 rounded-lg cursor-pointer transition-all
                    ${currentSessionId === session.id 
                      ? 'bg-blue-600 text-white' 
                      : 'hover:bg-gray-700 text-gray-300'
                    }
                  `}
                  onClick={() => onSessionSelect(session.id)}
                >
                  {editingSessionId === session.id ? (
                    <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onBlur={saveTitle}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') saveTitle();
                          if (e.key === 'Escape') cancelEditing();
                        }}
                        className="flex-1 bg-gray-800 text-white px-2 py-1 rounded text-sm"
                        autoFocus
                      />
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-sm truncate pr-2">
                          {session.title}
                        </h3>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => startEditing(session, e)}
                            className="p-1 hover:bg-gray-600 rounded"
                          >
                            <PencilIcon className="w-3 h-3" />
                          </button>
                          <button
                            onClick={(e) => handleDeleteSession(session.id, e)}
                            className="p-1 hover:bg-red-600 rounded"
                          >
                            <TrashIcon className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      
                      {session.first_message_preview && (
                        <p className="text-xs text-gray-400 mt-1 truncate">
                          {session.first_message_preview}
                        </p>
                      )}
                      
                      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                        <span>{session.message_count} 条消息</span>
                        <span>
                          {new Date(session.updated_at).toLocaleDateString('zh-CN', {
                            month: 'numeric',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
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
