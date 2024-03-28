import secrets
import string
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
env_file = "../.env"
encoding = "utf-8"


def generate_secret(byte=512):
    return secrets.token_urlsafe(byte)


def generate_aes_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(length))


SECRET_KEY_32 = f"{generate_secret(32)}"
SECRET_KEY_64 = f"{generate_secret(64)}"
SECRET_KEY_32_AES = f"{generate_aes_key(32)}"


class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="DB Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )
    POSTGRES_PRIMARY_DSN: str = Field(alias="WALLE_DATABASE_URL",
                                      default="postgresql+asyncpg://postgres:postgres@postgres-service:5432/test")
    POSTGRES_REPLICATION_DSN: str = Field(alias="WALLE_REPLICATION_DATABASE_URL",
                                          default="postgresql+asyncpg://postgres:postgres@postgres-service:5432/test")


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="API Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: str = Field(default=f"{SECRET_KEY_32}")
    API_SECRET: str = Field(default=f"{SECRET_KEY_32}")


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(
        title="S3 Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    AWS_ACCESS_KEY: str = Field(default="")
    AWS_SECRET_KEY: str = Field(default="")
    AWS_REGION: str = Field(default="")
    AWS_BUCKET_NAME: str = Field(default="")


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="JWT Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    JWT_ACCESS_SECRET: str = Field(default=f"{SECRET_KEY_64}")
    JWT_ALGORITHM: str = Field(default="HS256")
    VERIFICATION_MINUTES: int = Field(default=30)


class WidgetSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="Widget Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    ENCRYPTION_KEY: str = Field(default=f"{SECRET_KEY_32_AES}")


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="OpenAI Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    OPENAI_API_KEY: str = Field(default=f"{SECRET_KEY_32}")


class RabbitMQSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="RabbitMQ Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    RABBITMQ_HOST: str = Field(default="rabbitmq-service", alias="rabbitMq__hostnames__0")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str = Field(default="guest", alias="rabbitMq__username")
    RABBITMQ_PASSWORD: str = Field(default="guest", alias="rabbitMq__password")
    PUBLISH_QUEUE: str = Field(
        default="payment-service/walle.message_sent", alias="RABBIT_MQ_PUBLISH_QUEUE"
    )
    EXCHANGE: str = Field(default="walle", alias="RABBIT_MQ_EXCHANGE")
    CONSUME_QUEUE: str = Field(
        default="walle-service/payment.tokens_count", alias="RABBIT_MQ_CONSUME_QUEUE"
    )
    ROUTING_KEY: str = Field(default="message_sent", alias="RABBIT_MQ_ROUTING_KEY")


class ApiCallSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="API Call Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    ORGANIZATION: str = Field(
        default="https://dev.simulacrumai.com/organization",
        alias="httpClient__services__oganization",
    )


RABBITMQ_SETTINGS = RabbitMQSettings()


class CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="Celery Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    CELERY_BROKER_URL: str = Field(default="amqp:/rabbitmq-service:5672")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis-service:6379")

    @field_validator("CELERY_BROKER_URL", mode="after")
    def validate_broker_url(cls, v):
        return (
            f"amqp://{RABBITMQ_SETTINGS.RABBITMQ_USER}:"
            f"{RABBITMQ_SETTINGS.RABBITMQ_PASSWORD}@{RABBITMQ_SETTINGS.RABBITMQ_HOST}"
            f":{RABBITMQ_SETTINGS.RABBITMQ_PORT}"
        )


class MailSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="Mail Settings",
        env_file=env_file,
        env_file_encoding=encoding,
    )

    MAIL_USERNAME: str = Field(
        default="no-reply@simulacrumai.com",
        alias="IntegrationConfiguration__SmtpClientConfiguration__MailUser",
    )
    MAIL_PASSWORD: str = Field(
        default="Yyv0Hx6UYu",
        alias="IntegrationConfiguration__SmtpClientConfiguration__MailPassword",
    )
    MAIL_FROM: str = Field(
        default="noreply@simulacrumai.com",
        alias="IntegrationConfiguration__SmtpClientConfiguration__MailUser",
    )
    MAIL_SERVER: str = Field(
        default="smtp.simulacrumai.com",
        alias="IntegrationConfiguration__SmtpClientConfiguration__MailSmtpHost",
    )
    MAIL_PORT: int = Field(default=465)
    MAIL_SSL_TLS: bool = Field(default=True)
    MAIL_STARTTLS: bool = Field(default=False)
    VALIDATE_CERTS: bool = Field(default=False)
    USE_CREDENTIALS: bool = Field(default=True)


class Settings(BaseSettings):
    DATABASE: DbSettings = DbSettings()
    API_V1: ApiSettings = ApiSettings()
    S3: S3Settings = S3Settings()
    JWT: JWTSettings = JWTSettings()
    WIDGET: WidgetSettings = WidgetSettings()
    OPENAI: OpenAISettings = OpenAISettings()
    RABBITMQ: RabbitMQSettings = RABBITMQ_SETTINGS
    API_CALL: ApiCallSettings = ApiCallSettings()
    CELERY: CelerySettings = CelerySettings()
    MAIL: MailSettings = MailSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


APP_SETTINGS = get_settings()
