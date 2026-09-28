from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "LEUIT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_PATH: str = "./leuit_store.enc"
    DATABASE_KEY: Optional[str] = None  # Set at runtime after unlock

    # Security
    CLOUD_PUBLIC_KEY_HEX: str = Field(default="b12064c14d537f0369b82f09028553df659c536e9871564189bc7669114b15f2", description="Ed25519 public key for license verification")
    DEVICE_FINGERPRINT: Optional[str] = None

    # License
    LICENSE_FILE_PATH: str = os.path.expanduser("~/.leuit/license.key")
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