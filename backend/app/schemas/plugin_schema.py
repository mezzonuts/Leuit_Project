"""Plugin system schemas for 3rd party extensions."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    """Plugin manifest schema for 3rd party extensions."""
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str = Field(..., max_length=500)
    author: str = Field(..., max_length=100)
    license: str = Field(default="MIT", max_length=50)
    entry_point: str = Field(..., max_length=200)
    permissions: list[str] = Field(default_factory=list)
    config_schema: dict[str, Any] = Field(default_factory=dict)
    min_core_version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    homepage: str | None = Field(None, max_length=200)
    repository: str | None = Field(None, max_length=200)


class PluginConfig(BaseModel):
    """Runtime plugin configuration."""
    plugin_name: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    installed_at: str | None = None
    updated_at: str | None = None


class PluginHook(BaseModel):
    """Plugin hook definition."""
    name: str = Field(..., pattern=r"^[a-z_]+$")
    endpoint: str = Field(..., pattern=r"^https?://")
    secret: str | None = None
    events: list[str] = Field(default_factory=list)
    retry_count: int = 3
    timeout_seconds: int = 30


class PluginInfo(BaseModel):
    """Installed plugin info for listing."""
    manifest: PluginManifest
    config: PluginConfig | None = None
    hooks: list[PluginHook] = Field(default_factory=list)
    status: str = "active"
    error_message: str | None = None