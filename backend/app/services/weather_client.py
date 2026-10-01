"""BMKG Weather API client with caching."""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory cache: adm4_code -> (data, timestamp)
_cache: dict[str, tuple[list[dict[str, Any]], datetime]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


async def get_weather_forecast(adm4_code: str | None = None) -> list[dict[str, Any]]:
    """Fetch weather forecast from BMKG API with caching."""
    code = adm4_code or settings.BMKG_DEFAULT_ADM4

    # Check cache
    if code in _cache:
        data, timestamp = _cache[code]
        if (datetime.now(UTC) - timestamp).total_seconds() < CACHE_TTL_SECONDS:
            return data

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                settings.BMKG_API_BASE,
                params={"adm4": code},
            )
            response.raise_for_status()
            raw = response.json()

        forecasts = _parse_bmkg_response(raw)
        _cache[code] = (forecasts, datetime.now(UTC))
        return forecasts

    except (httpx.HTTPError, KeyError, ValueError) as e:
        logger.warning("BMKG API failed: %s — using mock data", e)
        return _mock_forecast()


def _parse_bmkg_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse BMKG API response into normalized format."""
    forecasts = []
    for item in raw.get("data", []):
        forecasts.append({
            "date": item.get("date", datetime.now(UTC).isoformat()),
            "temperature_min": item.get("temp_min", 0.0),
            "temperature_max": item.get("temp_max", 0.0),
            "humidity": item.get("humidity", 0.0),
            "rainfall_probability": item.get("rain_prob", 0.0),
            "weather_description": item.get("weather_desc", ""),
        })
    return forecasts


def _mock_forecast() -> list[dict[str, Any]]:
    """Return mock forecast data when API is unavailable."""
    return [
        {
            "date": (datetime.now(UTC) + timedelta(days=i)).isoformat(),
            "temperature_min": 22.0,
            "temperature_max": 30.0,
            "humidity": 75.0,
            "rainfall_probability": 30.0,
            "weather_description": "Cerah Berawan",
        }
        for i in range(3)
    ]


def clear_cache() -> None:
    """Clear the weather cache (for testing)."""
    _cache.clear()
