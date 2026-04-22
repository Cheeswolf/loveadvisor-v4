"""
LoveAdvisor V3 - Configuration Settings
Phase 1: Engineering Skeleton Initialization

This module contains configuration settings for the LoveAdvisor V3 application.
Settings are organized by component and environment.
"""

import os
from pathlib import Path

# ============================================================================
# V2.5 Legacy Configuration (for backward compatibility)
# ============================================================================
COZE_API = "https://api.coze.cn/v1/workflow/run"
TOKEN = os.environ.get("COZE_API_TOKEN", "")

# 工作流1：S1 -> S2 -> S3
EXTRACT_WORKFLOW_ID = "7623810752218497034"

# 工作流2：S5
S5_WORKFLOW_ID = "7624197219024994330"

# 请求超时
REQUEST_TIMEOUT = 90


# ============================================================================
# V3 Core Configuration
# ============================================================================

# Load environment variables from .env file if present
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment variables from {env_path}")
    except ImportError:
        print("python-dotenv not installed, skipping .env loading")
    except Exception as e:
        print(f"Error loading .env file: {e}")
else:
    print(f"No .env file found at {env_path}, using system environment variables")

# Application Settings
APP_NAME = "LoveAdvisor V4"
APP_VERSION = "4.0.0"
API_PREFIX = "/api/v1"
ENVIRONMENT = "development"  # development, staging, production
DEBUG = True

# Server Settings
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 1

# Pipeline Configuration
PIPELINE_VERSION = "v3"
ENABLE_GUARDRAILS = True
ENABLE_HISTORY_LOGGING = True
ENABLE_CACHING = False

# LLM Provider Configuration
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "deepseek")  # mock, openai, deepseek, anthropic, coze
LLM_DEFAULT_MODEL = os.environ.get("LLM_DEFAULT_MODEL", "deepseek-chat")
LLM_DEFAULT_TEMPERATURE = float(os.environ.get("LLM_DEFAULT_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "2000"))

# Provider API Keys (load from environment variables)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# I1 Image-to-Text Vision Model Configuration
# Now using OCR.space as the single provider for OCR capabilities
I1_VISION_API_KEY = os.environ.get("I1_VISION_API_KEY", "")  # OCR.space API key
I1_VISION_MODEL = os.environ.get("I1_VISION_MODEL", "2")  # OCR.space OCREngine parameter (1, 2, 3)
I1_VISION_LANGUAGE = os.environ.get("I1_VISION_LANGUAGE", "chs")  # OCR.space language parameter (e.g., chs for Chinese Simplified)
I1_VISION_BASE_URL = os.environ.get("I1_VISION_BASE_URL", "https://api.ocr.space")  # OCR.space API base URL

# Qwen-OCR Configuration (DashScope) for V3.6
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")  # DashScope API key for Qwen-OCR
QWEN_OCR_MODEL = os.environ.get("QWEN_OCR_MODEL", "qwen-vl-ocr")  # Qwen-OCR model name
QWEN_OCR_BASE_URL = os.environ.get("QWEN_OCR_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")  # DashScope compatible mode endpoint

# Rate Limiting
RATE_LIMIT_ENABLED = False
RATE_LIMIT_REQUESTS_PER_MINUTE = 60

# Security
CORS_ALLOW_ORIGINS = ["*"]  # TODO: Restrict in production
API_KEY_REQUIRED = False

# Database (Placeholder)
DATABASE_URL = "sqlite:///./data/loveadvisor.db"
DATABASE_POOL_SIZE = 5

# Cache (Placeholder)
CACHE_TYPE = "memory"  # memory, redis
CACHE_TTL_SECONDS = 300

# Monitoring
ENABLE_METRICS = True
METRICS_PORT = 9090

# Feature Flags (Placeholder)
FEATURE_ADVANCED_ANALYSIS = False
FEATURE_REAL_TIME_UPDATES = False
FEATURE_MULTI_LANGUAGE = False