# 数据库架构下一步实施计划

## 🎯 优先级1: 用户管理系统实施

### 1.1 创建用户管理表
```sql
-- 在PostgreSQL中添加用户管理schema
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);
```

### 1.2 更新现有chat_sessions表
```sql
-- 添加user_id到chat_sessions表
ALTER TABLE chat_sessions ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
```

## 🎯 优先级2: 文档元数据管理

### 2.1 文档管理表
```sql
CREATE TABLE document_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_count INTEGER DEFAULT 0
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    collection_id UUID REFERENCES document_collections(id),
    uploaded_by UUID REFERENCES users(id),
    checksum VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false
);
```

## 🎯 优先级3: 分析和监控

### 3.1 查询日志表
```sql
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id UUID REFERENCES chat_sessions(id),
    query_text TEXT NOT NULL,
    response_text TEXT,
    response_time_ms INTEGER,
    source_documents JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 实施步骤

### Step 1: 数据库迁移脚本
创建 `migration_001_user_management.sql` 文件

### Step 2: SQLAlchemy模型更新
更新 `app/models/db_models.py` 添加新的表模型

### Step 3: API认证中间件
实现JWT认证和用户会话管理

### Step 4: 文档权限控制
添加基于用户角色的文档访问控制

## 📈 预期收益

1. **用户隔离**: 每个用户只能访问自己的聊天记录和文档
2. **权限控制**: 基于角色的细粒度权限管理
3. **审计追踪**: 完整的用户活动日志
4. **性能监控**: 查询性能和系统使用情况分析

## 🚀 快速开始

运行以下命令开始实施：

```bash
# 1. 创建数据库迁移脚本
cd /Users/chenbingxu/Documents/Projects/Capstone/rag/inference-service/backend
python db_utils.py create

# 2. 备份现有数据（重要！）
pg_dump chatdb > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. 运行迁移
psql -d chatdb -f migration_001_user_management.sql
```

这个计划将逐步完善你的数据库架构，使其成为真正的企业级RAG系统！
