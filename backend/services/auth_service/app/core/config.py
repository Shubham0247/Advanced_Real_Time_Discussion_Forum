from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "auth_service"
    debug: bool = True
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 30
    password_reset_otp_expire_minutes: int = 10
    password_reset_otp_length: int = 6
    password_reset_otp_max_attempts: int = 5
    smtp_host: str = Field(
        default="",
        validation_alias=AliasChoices("DOCKER_SMTP_HOST", "SMTP_HOST"),
    )
    smtp_port: int = Field(
        default=587,
        validation_alias=AliasChoices("DOCKER_SMTP_PORT", "SMTP_PORT"),
    )
    smtp_username: str = Field(
        default="",
        validation_alias=AliasChoices("DOCKER_SMTP_USERNAME", "SMTP_USERNAME"),
    )
    smtp_password: str = Field(
        default="",
        validation_alias=AliasChoices("DOCKER_SMTP_PASSWORD", "SMTP_PASSWORD"),
    )
    smtp_from_email: str = Field(
        default="no-reply@example.com",
        validation_alias=AliasChoices("DOCKER_SMTP_FROM_EMAIL", "SMTP_FROM_EMAIL"),
    )
    smtp_use_tls: bool = Field(
        default=True,
        validation_alias=AliasChoices("DOCKER_SMTP_USE_TLS", "SMTP_USE_TLS"),
    )
    smtp_use_ssl: bool = Field(
        default=False,
        validation_alias=AliasChoices("DOCKER_SMTP_USE_SSL", "SMTP_USE_SSL"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
