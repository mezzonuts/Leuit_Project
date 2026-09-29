import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "LEUIT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_PATH: str = "./leuit_store.enc"
    DATABASE_KEY: str | None = None  # Set at runtime after unlock

    # Security
    CLOUD_PUBLIC_KEY_HEX: str = Field(default="", description="Ed25519 public key hex for license verification")
    DEV_PRIVATE_KEY_HEX: str = Field(default="", description="Ed25519 private key hex for developer recovery")
    PUBLIC_KEY_PATH: str = Field(default="backend/dev_public_key.hex", description="Path to developer public key file")
    DEV_PRIVATE_KEY_PATH: str = Field(default="backend/dev_private_key.hex", description="Path to developer private key file")
    DEVICE_FINGERPRINT: str | None = None

    # License
    LICENSE_FILE_PATH: str = os.path.expanduser("~/.leuit/license.key")
    LICENSE_INIT_VALID_DAYS: int = 365
    GRACE_PERIOD_DAYS: int = 3

    # BMKG Weather API
    BMKG_API_BASE: str = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
    BMKG_DEFAULT_ADM4: str = "32.73.08.1001"  # Bandung Dago/Coblong

    # Forecasting
    FORECAST_HORIZON_DAYS: int = 7
    SAFETY_STOCK_MULTIPLIER: float = 1.2

    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
