from __future__ import annotations

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator


class ServerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    public_base_url: AnyHttpUrl | None = None


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = "sqlite+aiosqlite:///./var/steward.db"


class UpstreamConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: AnyHttpUrl = "http://127.0.0.1:1234/v1"
    timeout_seconds: int = Field(default=120, ge=1, le=3600)


class ModelsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: list[str] = Field(default_factory=list)

    @field_validator("allowed")
    @classmethod
    def validate_allowed_models(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("At least one model must be configured.")
        return value


class QueueConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_length: int = Field(default=64, ge=1, le=10000)
    short_job_max_input_chars: int = Field(default=4000, ge=1)
    short_job_max_output_tokens: int = Field(default=1200, ge=1)


class AuthConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner_user_id: str = "owner"
    bootstrap_admin_enabled: bool = True


class BatteryConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    minimum_percent: int = Field(default=25, ge=0, le=100)
    reject_when_unplugged: bool = False


class StewardConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config_version: int = 1
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    upstream: UpstreamConfig = Field(default_factory=UpstreamConfig)
    models: ModelsConfig = Field(
        default_factory=lambda: ModelsConfig(allowed=["qwen/qwen3-coder-next"])
    )
    queue: QueueConfig = Field(default_factory=QueueConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    battery: BatteryConfig = Field(default_factory=BatteryConfig)

    @model_validator(mode="after")
    def validate_version(self) -> StewardConfig:
        if self.config_version != 1:
            raise ValueError("Unsupported config_version. Steward currently supports version 1.")
        return self
