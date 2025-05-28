"use client";

import { useEffect, useRef, useState } from "react";
import ChatItem from "./chat-item";

export interface Message {
  id: string;
  content: string;
  role: string;
}

export default function ChatMessages({
  messages,
  isLoading,
  reload,
  stop,
}: {
  messages: Message[];
  isLoading?: boolean;
  stop?: () => void;
  reload?: () => void;
}) {
  const scrollableChatContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const scrollToBottom = () => {
    if (scrollableChatContainerRef.current) {
      scrollableChatContainerRef.current.scrollTop =
        scrollableChatContainerRef.current.scrollHeight;
    }
  };

  const handleScroll = () => {
    if (scrollableChatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollableChatContainerRef.current;
      const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100;
      setShowScrollButton(!isNearBottom);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  useEffect(() => {
    const container = scrollableChatContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  return (
    <div className="h-full flex flex-col relative">
      <div
        className="flex-1 overflow-auto"
        ref={scrollableChatContainerRef}
      >
        <div className="max-w-2xl mx-auto px-6 py-6 space-y-6">
          {messages.length === 0 ? (
            <div className="text-center text-gray-600 pt-32 pb-32">
              <h1 className="text-4xl font-semibold mb-4">Internal RAG System</h1>
              <p className="text-lg text-gray-500">How can I help you today?</p>
            </div>
          ) : (
            messages.map((m: Message) => (
              <ChatItem key={m.id} {...m} />
            ))
          )}
        </div>
      </div>
      
      {/* Back to bottom button - positioned above input area */}
      {showScrollButton && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
          <button
            onClick={scrollToBottom}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-full shadow-lg transition-all duration-200 flex items-center gap-2"
            title="Scroll to bottom"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            <span className="text-sm">Back to bottom</span>
          </button>
        </div>
      )}
    </div>
  );
}
