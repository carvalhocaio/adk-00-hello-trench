from functools import lru_cache
from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    agent_model: str = Field(
        default="gemini-flash-latest", validation_alias="HELLO_TRENCH_MODEL"
    )
    use_enterprise: bool = Field(
        default=False, validation_alias="GOOGLE_GENAI_USE_ENTERPRISE"
    )
    google_api_key: SecretStr | None = Field(
        default=None, validation_alias="GOOGLE_API_KEY"
    )
    google_cloud_project: str | None = Field(
        default=None, validation_alias="GOOGLE_CLOUD_PROJECT"
    )

    @model_validator(mode="after")
    def require_backend_credentials(self) -> Self:
        if self.use_enterprise and not self.google_cloud_project:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT is required when "
                "GOOGLE_GENAI_USE_ENTERPRISE is enabled"
            )
        if not self.use_enterprise and self.google_api_key is None:
            raise ValueError("GOOGLE_API_KEY is required for the Gemini API backend")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
