import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute path to project root .env file
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_file_path = os.path.join(base_dir, ".env")


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    db_name: str = Field(default="enterprise_ai_ops", alias="POSTGRES_DB")

    @property
    def connection_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    @property
    def connection_url(self) -> str:
        pwd = f":{self.password}@" if self.password else ""
        return f"redis://{pwd}{self.host}:{self.port}/{self.db}"


class PineconeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    environment: Optional[str] = Field(default=None, alias="PINECONE_ENVIRONMENT")
    index_name: str = Field(default="nova-policies", alias="PINECONE_INDEX_NAME")


class LLMModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    default_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    default_chat_model: str = Field(default="gpt-4o", alias="DEFAULT_CHAT_MODEL")
    default_embedding_model: str = Field(default="text-embedding-3-small", alias="DEFAULT_EMBEDDING_MODEL")


class ObservabilitySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    prometheus_metrics_port: int = Field(default=9090, alias="PROMETHEUS_METRICS_PORT")
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317", alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    langsmith_tracing: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langsmith_endpoint: Optional[str] = Field(default=None, alias="LANGCHAIN_ENDPOINT")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    langsmith_project: str = Field(default="enterprise-ai-ops", alias="LANGCHAIN_PROJECT")


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    server_url: str = Field(default="http://localhost:8080/mcp", alias="MCP_SERVER_URL")
    auth_token: Optional[str] = Field(default=None, alias="MCP_AUTH_TOKEN")


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    url: str = Field(default="http://localhost:8001", alias="RAG_SERVICE_URL")
    enable_cch: bool = Field(default=True, alias="RAG_ENABLE_CCH")
    enable_hype: bool = Field(default=True, alias="RAG_ENABLE_HYPE")
    enable_rse: bool = Field(default=True, alias="RAG_ENABLE_RSE")
    enable_dartboard: bool = Field(default=True, alias="RAG_ENABLE_DARTBOARD")
    enable_crag: bool = Field(default=True, alias="RAG_ENABLE_CRAG")
    crag_threshold: float = Field(default=0.6, alias="RAG_CRAG_THRESHOLD")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
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
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    pinecone: PineconeSettings = PineconeSettings()
    llm: LLMModelSettings = LLMModelSettings()
    observability: ObservabilitySettings = ObservabilitySettings()
    mcp: MCPSettings = MCPSettings()
    rag: RAGSettings = RAGSettings()


# Singleton instance of settings to import throughout the project
settings = Settings()
