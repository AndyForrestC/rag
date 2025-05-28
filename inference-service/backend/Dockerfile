# 使用官方Python基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry

# 配置Poetry - 不使用虚拟环境，直接安装到系统Python
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_CREATE=false

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock ./

# 安装Python依赖
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# 复制应用代码
COPY . .

# 创建非root用户并设置权限
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /usr/local/lib/python3.11/site-packages && \
    chmod -R 755 /usr/local/lib/python3.11/site-packages

USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
