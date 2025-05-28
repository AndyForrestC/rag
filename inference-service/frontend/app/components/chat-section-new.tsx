"use client";

import { useChat } from "ai/react";
import { useMemo, useState, useEffect } from "react";
import { insertDataIntoMessages } from "./transform";
import { ChatInput, ChatMessages } from "./ui/chat";
import SessionSidebar from "./ui/chat/session-sidebar";
import MenuButton from "./ui/chat/menu-button";
import { ChatAPI } from "../lib/api";
import { ChatSession, ChatMessage } from "../types/chat";

export default function ChatSection() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);

  const {
    messages,
    input,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
    data,
    setMessages,
  } = useChat({
    api: "http://localhost:8000/api/chat",
    headers: {
      "Content-Type": "application/json",
    },
    body: {
      session_id: currentSessionId,
    },
  });

  const transformedMessages = useMemo(() => {
    return insertDataIntoMessages(messages, data);
  }, [messages, data]);

  // 当选择会话时加载消息
  const handleSessionSelect = async (sessionId: string) => {
    try {
      const sessionWithMessages = await ChatAPI.getSession(sessionId);
      setCurrentSessionId(sessionId);
      setCurrentSession(sessionWithMessages.session);
      
      // 转换消息格式以兼容 useChat
      const formattedMessages = sessionWithMessages.messages.map((msg: ChatMessage) => ({
        id: msg.id,
        content: msg.content,
        role: msg.role,
        createdAt: new Date(msg.timestamp),
      }));
      
      setMessages(formattedMessages);
      setIsSidebarOpen(false); // 选择会话后关闭侧边栏
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  // 创建新聊天
  const handleNewChat = async () => {
    try {
      const newSession = await ChatAPI.createSession();
      setCurrentSessionId(newSession.id);
      setCurrentSession(newSession);
      setMessages([]);
      setIsSidebarOpen(false);
    } catch (error) {
      console.error('Failed to create new session:', error);
      // 如果创建失败，至少清空当前聊天
      setCurrentSessionId(null);
      setCurrentSession(null);
      setMessages([]);
      setIsSidebarOpen(false);
    }
  };

  // 如果没有当前会话且有消息，自动创建会话
  useEffect(() => {
    if (!currentSessionId && messages.length > 0) {
      handleNewChat();
    }
  }, [messages.length, currentSessionId]);

  // 重写 handleSubmit 以确保有会话ID
  const handleSubmitWithSession = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // 如果没有当前会话，先创建一个
    if (!currentSessionId) {
      try {
        const newSession = await ChatAPI.createSession();
        setCurrentSessionId(newSession.id);
        setCurrentSession(newSession);
      } catch (error) {
        console.error('Failed to create session:', error);
      }
    }
    
    // 调用原始的 handleSubmit
    handleSubmit(e);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 菜单按钮 */}
      <MenuButton 
        onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
        isOpen={isSidebarOpen}
      />

      {/* 会话侧边栏 */}
      <SessionSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentSessionId={currentSessionId || undefined}
        onSessionSelect={handleSessionSelect}
        onNewChat={handleNewChat}
      />

      {/* 主聊天区域 */}
      <div className={`
        flex-1 flex flex-col transition-all duration-300
        ${isSidebarOpen ? 'lg:ml-80' : 'ml-0'}
      `}>
        {/* 头部标题 */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 ml-16 lg:ml-0">
          <div className="max-w-2xl mx-auto">
            <h1 className="text-lg font-semibold text-gray-800">
              {currentSession?.title || "Internal RAG System"}
            </h1>
            {currentSession && (
              <p className="text-sm text-gray-500 mt-1">
                {currentSession.message_count} 条消息 • 最后更新: {new Date(currentSession.updated_at).toLocaleString()}
              </p>
            )}
          </div>
        </div>

        {/* 聊天消息区域 */}
        <div className="flex-1 overflow-hidden">
          <ChatMessages
            messages={transformedMessages}
            isLoading={isLoading}
            reload={reload}
            stop={stop}
          />
        </div>
        
        {/* 输入区域 */}
        <div className="flex-shrink-0 bg-white border-t border-gray-200 px-6 py-4">
          <div className="max-w-2xl mx-auto">
            <ChatInput
              input={input}
              handleSubmit={handleSubmitWithSession}
              handleInputChange={handleInputChange}
              isLoading={isLoading}
              multiModal={process.env.NEXT_PUBLIC_MODEL === "gpt-4-vision-preview"}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
