import re
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "rms_admin"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "r-m-system"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    BACKEND_CORS_ORIGINS: str = ""

    ANDROID_PACKAGE_NAME: str = "com.rentalmanagement.app"
    ANDROID_SHA256_CERT: str = "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return ",".join(
                origin.strip() for origin in v.split(",") if origin.strip()
            )
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origins(self) -> List[str]:
        return [o for o in self.BACKEND_CORS_ORIGINS.split(",") if o]

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return URL.create(
            "postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    model_config = {"env_file": ".env", "extra": "ignore"}


PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


def validate_password_strength(password: str) -> str:
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(
            "Password must be at least 8 characters and include uppercase, lowercase, and a digit."
        )
    return password


settings = Settings()
