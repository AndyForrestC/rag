"use client";

import { useState } from "react";
import { Bars3Icon, ChatBubbleLeftIcon, PlusIcon } from "@heroicons/react/24/outline";

interface ChatMenuButtonProps {
  onToggleSidebar: () => void;
  onNewChat: () => void;
}

export default function ChatMenuButton({ onToggleSidebar, onNewChat }: ChatMenuButtonProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleMenuClick = () => {
    setIsExpanded(!isExpanded);
  };

  const handleSidebarToggle = () => {
    onToggleSidebar();
    setIsExpanded(false);
  };

  const handleNewChatClick = () => {
    onNewChat();
    setIsExpanded(false);
  };

  return (
    <div className="relative">
      {/* 主按钮 */}
      <button
        onClick={handleMenuClick}
        className={`
          fixed top-4 left-4 z-30 p-3 bg-gray-800 hover:bg-gray-700 text-white rounded-full shadow-lg
          transition-all duration-300 ease-in-out transform
          ${isExpanded ? 'rotate-90 scale-110' : 'hover:scale-105'}
        `}
        title="菜单"
      >
        <Bars3Icon className="w-6 h-6" />
      </button>

      {/* 展开的菜单项 */}
      <div className={`
        fixed top-4 left-4 z-20 transition-all duration-300 ease-in-out
        ${isExpanded ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'}
      `}>
        {/* 背景遮罩 */}
        {isExpanded && (
          <div 
            className="fixed inset-0 bg-transparent"
            onClick={() => setIsExpanded(false)}
          />
        )}
        
        {/* 菜单项容器 */}
        <div className="relative">
          {/* 聊天记录按钮 */}
          <button
            onClick={handleSidebarToggle}
            className={`
              absolute top-16 left-0 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg
              transition-all duration-300 ease-in-out transform
              ${isExpanded ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'}
              hover:scale-105
            `}
            style={{ transitionDelay: isExpanded ? '100ms' : '0ms' }}
            title="聊天记录"
          >
            <ChatBubbleLeftIcon className="w-5 h-5" />
          </button>

          {/* 新建聊天按钮 */}
          <button
            onClick={handleNewChatClick}
            className={`
              absolute top-28 left-0 p-3 bg-green-600 hover:bg-green-700 text-white rounded-full shadow-lg
              transition-all duration-300 ease-in-out transform
              ${isExpanded ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}
              hover:scale-105
            `}
            style={{ transitionDelay: isExpanded ? '200ms' : '0ms' }}
            title="新建聊天"
          >
            <PlusIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* 提示标签 */}
      {isExpanded && (
        <div className="fixed top-4 left-20 z-10 flex flex-col gap-1">
          <div className={`
            bg-gray-900 text-white text-sm px-3 py-2 rounded-lg shadow-lg
            transition-all duration-300 ease-in-out transform
            ${isExpanded ? 'translate-x-0 opacity-100' : '-translate-x-2 opacity-0'}
          `} style={{ transitionDelay: '100ms' }}>
            <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-2">
              <div className="w-0 h-0 border-t-4 border-b-4 border-r-4 border-transparent border-r-gray-900"></div>
            </div>
            聊天记录
          </div>
          
          <div className={`
            bg-gray-900 text-white text-sm px-3 py-2 rounded-lg shadow-lg mt-12
            transition-all duration-300 ease-in-out transform
            ${isExpanded ? 'translate-x-0 opacity-100' : '-translate-x-2 opacity-0'}
          `} style={{ transitionDelay: '200ms' }}>
            <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-2">
              <div className="w-0 h-0 border-t-4 border-b-4 border-r-4 border-transparent border-r-gray-900"></div>
            </div>
            新建聊天
          </div>
        </div>
      )}
    </div>
  );
}
