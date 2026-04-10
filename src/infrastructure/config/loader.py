import os
import yaml
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseModel):
    name: str = "Browser-Testing"
    env: str = "development"
    debug: bool = True

class StorageConfig(BaseModel):
    type: str = "s3"
    endpoint_url: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket_name: str = "automation-evidence"
    region: str = "us-east-1"
    public_url_prefix: Optional[str] = None

class MessagingConfig(BaseModel):
    type: str = "redis"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    stream_ttl_hours: int = 5

class WorkerConfig(BaseModel):
    concurrency: int = 5
    queue_name: str = "automation_tasks"
    redis_url: str = "redis://localhost:6379/0"

class AgentConfig(BaseModel):
    default_model: str = "gpt-4o-mini"
    max_steps: int = 10
    use_vision: bool = True

class RootConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    messaging: MessagingConfig = Field(default_factory=MessagingConfig)
    worker: WorkerConfig = Field(default_factory=WorkerConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

def _load_yaml_with_env(path: str) -> Dict[str, Any]:
    """Loads YAML and replaces ${VAR} or ${VAR:-default} with env variables."""
    import re
    # Pattern to match ${VAR} or ${VAR:-default}
    pattern = re.compile(r'\${(\w+)(?::-(.*?))?}')

    with open(path, 'r') as f:
        content = f.read()

    def replace_env(match):
        var_name = match.group(1)
        default_value = match.group(2)
        return os.environ.get(var_name, default_value or match.group(0))

    content = pattern.sub(replace_env, content)
    return yaml.safe_load(content)

class Settings(BaseSettings):
    """Main Settings Class that loads from YAML and allows .env overrides."""
    model_config = SettingsConfigDict(env_file='.env', env_nested_delimiter='__', extra='ignore')
    
# Global cache for settings
_settings_cache: Optional[RootConfig] = None

class Settings(BaseSettings):
    """Main Settings Class that loads from YAML and allows .env overrides."""
    model_config = SettingsConfigDict(env_file='.env', env_nested_delimiter='__', extra='ignore')

    @classmethod
    def load(cls, config_path: str = "config/config.yaml") -> RootConfig:
        global _settings_cache
        if _settings_cache is None:
            # Load YAML first
            raw_data = _load_yaml_with_env(config_path)
            _settings_cache = RootConfig(**raw_data)
        return _settings_cache

# Global settings instance
settings = Settings.load()
