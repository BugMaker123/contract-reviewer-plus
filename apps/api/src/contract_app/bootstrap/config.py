from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    app_name: str = "Contract Reviewer Plus"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    cors_origins: list[str] = ["*"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./contract_app.db"
    # In docker-compose: postgresql+asyncpg://postgres:postgres@postgres:5432/contract_db

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Storage
    storage_dir: Path = Path("./data/storage")

    # ONLYOFFICE Document Server
    onlyoffice_public_url: str = "http://localhost:8080"
    onlyoffice_internal_url: str = "http://localhost:8080"
    onlyoffice_secret: str = "contract_reviewer_secret_jwt"

    # AI Model Gateway & Domestic LLM Providers
    llm_provider: str = "deepseek"  # "deepseek" | "qwen" | "openai" | "custom"
    
    # DeepSeek (支持 DeepSeek 官方或硅基流动等兼容中继)
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"  # 支持 deepseek-v4-flash, deepseek-chat, deepseek-reasoner

    # Qwen (阿里百炼 DashScope / 通义千问)
    dashscope_api_key: str = ""
    qwen_model: str = "qwen-plus"

    # OpenAI / 通用标准兼容网关
    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    mock_ai_pipeline: bool = True  # 当未填写有效 API Key 时自动平滑回退至智能规则/离线降级引擎

    # Review Pipeline limits
    max_review_retries: int = 3
    review_deadline_seconds: int = 180
    worker_lease_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = AppSettings()
