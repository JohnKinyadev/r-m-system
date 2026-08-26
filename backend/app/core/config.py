from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import re


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    BACKEND_CORS_ORIGINS: str = ""

    # Play Store TWA — set these in .env after generating your signed APK
    ANDROID_PACKAGE_NAME: str = "com.farmmanagement.app"
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

    model_config = {"env_file": ".env", "extra": "ignore"}


PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


def validate_password_strength(password: str) -> str:
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(
            "Password must be at least 8 characters and include uppercase, lowercase, and a digit."
        )
    return password


settings = Settings()
