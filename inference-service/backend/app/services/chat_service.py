import uuid
from datetime import datetime
from typing import List, Optional, Dict
from app.models.chat import (
    ChatSession, 
    ChatMessage, 
    MessageRole, 
    ChatSessionWithMessages,
    CreateSessionRequest,
    UpdateSessionRequest
)

# 内存存储 - 在实际项目中应该使用数据库
class InMemoryChatStore:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.messages: Dict[str, List[ChatMessage]] = {}
    
    def create_session(self, title: Optional[str] = None) -> ChatSession:
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        if not title:
            title = f"新的聊天 {now.strftime('%m-%d %H:%M')}"
        
        session = ChatSession(
            id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
            message_count=0
        )
        
        self.sessions[session_id] = session
        self.messages[session_id] = []
        return session
    
    def get_sessions(self) -> List[ChatSession]:
        return list(self.sessions.values())
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, title: str) -> Optional[ChatSession]:
        if session_id in self.sessions:
            self.sessions[session_id].title = title
            self.sessions[session_id].updated_at = datetime.now()
            return self.sessions[session_id]
        return None
    
    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.messages:
                del self.messages[session_id]
            return True
        return False
    
    def add_message(self, session_id: str, content: str, role: MessageRole) -> Optional[ChatMessage]:
        if session_id not in self.sessions:
            return None
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            content=content,
            role=role,
            timestamp=datetime.now(),
            session_id=session_id
        )
        
        self.messages[session_id].append(message)
        
        # 更新会话信息
        session = self.sessions[session_id]
        session.message_count = len(self.messages[session_id])
        session.updated_at = datetime.now()
        
        # 更新首条消息预览
        if session.message_count == 1 and role == MessageRole.USER:
            session.first_message_preview = content[:100] + "..." if len(content) > 100 else content
        
        return message
    
    def get_messages(self, session_id: str) -> List[ChatMessage]:
        return self.messages.get(session_id, [])
    
    def get_session_with_messages(self, session_id: str) -> Optional[ChatSessionWithMessages]:
        session = self.get_session(session_id)
        if not session:
            return None
        
        messages = self.get_messages(session_id)
        return ChatSessionWithMessages(session=session, messages=messages)


# 全局聊天存储实例
chat_store = InMemoryChatStore()


class ChatService:
    def __init__(self):
        self.store = chat_store
    
    def create_session(self, request: CreateSessionRequest) -> ChatSession:
        return self.store.create_session(request.title)
    
    def get_sessions(self) -> List[ChatSession]:
        # 按更新时间倒序排列
        sessions = self.store.get_sessions()
        return sorted(sessions, key=lambda x: x.updated_at, reverse=True)
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.store.get_session(session_id)
    
    def update_session(self, session_id: str, request: UpdateSessionRequest) -> Optional[ChatSession]:
        return self.store.update_session(session_id, request.title)
    
    def delete_session(self, session_id: str) -> bool:
        return self.store.delete_session(session_id)
    
    def add_message(self, session_id: str, content: str, role: MessageRole) -> Optional[ChatMessage]:
        return self.store.add_message(session_id, content, role)
    
    def get_messages(self, session_id: str) -> List[ChatMessage]:
        return self.store.get_messages(session_id)
    
    def get_session_with_messages(self, session_id: str) -> Optional[ChatSessionWithMessages]:
        return self.store.get_session_with_messages(session_id)


# 全局聊天服务实例
chat_service = ChatService()