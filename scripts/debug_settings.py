import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Resolve absolute path to project root .env file
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_file_path = os.path.join(base_dir, ".env")

print("Env file path:", env_file_path)
print("File exists:", os.path.exists(env_file_path))

class TestLLM(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    openai_api_key: str = Field(default=None, alias="OPENAI_API_KEY")

t = TestLLM()
print("Loaded key directly:", t.openai_api_key)
