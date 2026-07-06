from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    db_name: str = Field(default="enterprise_ai_ops", alias="POSTGRES_DB")

    @property
    def connection_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class RedisSettings(BaseSettings):
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    @property
    def connection_url(self) -> str:
        pwd = f":{self.password}@" if self.password else ""
        return f"redis://{pwd}{self.host}:{self.port}/{self.db}"


class QdrantSettings(BaseSettings):
    host: str = Field(default="localhost", alias="QDRANT_HOST")
    port: int = Field(default=6333, alias="QDRANT_PORT")
    api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    use_https: bool = Field(default=False, alias="QDRANT_USE_HTTPS")


class LLMModelSettings(BaseSettings):
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    default_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    default_chat_model: str = Field(default="gpt-4o", alias="DEFAULT_CHAT_MODEL")
    default_embedding_model: str = Field(default="text-embedding-3-small", alias="DEFAULT_EMBEDDING_MODEL")


class ObservabilitySettings(BaseSettings):
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    prometheus_metrics_port: int = Field(default=9090, alias="PROMETHEUS_METRICS_PORT")
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317", alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    langsmith_tracing: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langsmith_endpoint: Optional[str] = Field(default=None, alias="LANGCHAIN_ENDPOINT")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    langsmith_project: str = Field(default="enterprise-ai-ops", alias="LANGCHAIN_PROJECT")


class MCPSettings(BaseSettings):
    server_url: str = Field(default="http://localhost:8080/mcp", alias="MCP_SERVER_URL")
    auth_token: Optional[str] = Field(default=None, alias="MCP_AUTH_TOKEN")


class RAGSettings(BaseSettings):
    url: str = Field(default="http://localhost:8001", alias="RAG_SERVICE_URL")


class AppSettings(BaseSettings):
    app_name: str = Field(default="Enterprise AI Operations Platform", alias="APP_NAME")
    env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    jwt_secret_key: str = Field(default="temporary-dev-secret-key-change-in-prod", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    qdrant: QdrantSettings = QdrantSettings()
    llm: LLMModelSettings = LLMModelSettings()
    observability: ObservabilitySettings = ObservabilitySettings()
    mcp: MCPSettings = MCPSettings()
    rag: RAGSettings = RAGSettings()


# Singleton instance of settings to import throughout the project
settings = Settings()
