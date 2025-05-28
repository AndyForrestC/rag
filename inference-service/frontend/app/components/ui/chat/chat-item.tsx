"use client";

import ChatAvatar from "./chat-avatar";
import { Message } from "./chat-messages";

export default function ChatItem(message: Message) {
  const isUser = message.role === "user";
  
  if (isUser) {
    // User message aligned to the right
    return (
      <div className="flex items-start gap-4 py-8 justify-end">
        <div className="flex-1 min-w-0 max-w-3xl">
          <div className="text-gray-900 leading-7 whitespace-pre-wrap text-right">
            {message.content}
          </div>
        </div>
        <div className="flex-shrink-0">
          <ChatAvatar {...message} />
        </div>
      </div>
    );
  }
  
  // Assistant message aligned to the left
  return (
    <div className="flex items-start gap-4 py-8">
      <div className="flex-shrink-0">
        <ChatAvatar {...message} />
      </div>
      <div className="flex-1 min-w-0 max-w-3xl">
        <div className="text-gray-900 leading-7 whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    </div>
  );
}
