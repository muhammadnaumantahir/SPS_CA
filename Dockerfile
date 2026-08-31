# SPS-CA: Dockerfile for reproducible execution
# Base: Python 3.11 slim image
# Usage: docker build -t sps-ca . && docker run -it sps-ca

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY .gitignore .

# Copy source code
COPY core/ core/
COPY ui/ ui/
COPY capabilities/ capabilities/
COPY sandbox/ sandbox/
COPY governance/ governance/
COPY experience/ experience/
COPY evaluation/ evaluation/
COPY baselines/ baselines/
COPY docs/ docs/

# Create necessary directories
RUN mkdir -p core/tests \
    && mkdir -p capabilities/seeds \
    && mkdir -p capabilities/generated \
    && mkdir -p projects \
    && mkdir -p sandbox \
    && mkdir -p governance/decisions \
    && mkdir -p experience/logs \
    && mkdir -p evaluation/{scenarios,sandbox,regression,rollback,checklists,metrics} \
    && mkdir -p baselines

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Install tree-sitter language bindings for code parsing
# (These are heavy but necessary for language-agnostic analysis)
RUN pip install tree-sitter-python \
    tree-sitter-javascript \
    tree-sitter-java \
    tree-sitter-go \
    tree-sitter-cpp

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check: Test that imports work
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import tree_sitter; import pytest; print('OK')" || exit 1

# Default command: Start Python interactive shell
CMD ["python", "-i", "-c", "from core import *; print('SPS-CA ready. Type help() for info.')"]

# Notes:
# - Ollama server must run on host machine (not in container)
# - Container connects to Ollama via http://host.docker.internal:11434 (Docker Desktop)
# - Or use --network host on Linux
# - For interactive CLI: docker run -it sps-ca python -m ui.cli_interface
# - For tests: docker run sps-ca pytest core/tests/ -v
