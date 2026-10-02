"""Plugin management API endpoints."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.schemas.plugin_schema import (
    PluginInfo,
)
from app.services.plugin_registry import (
    disable_plugin,
    enable_plugin,
    get_plugin,
    install_plugin,
    list_plugins,
    trigger_hook,
    uninstall_plugin,
)

router = APIRouter(prefix="/plugins", tags=["Plugins"])


@router.get("", response_model=list[dict])
def list_plugins_endpoint(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> list[PluginInfo]:
    """List all installed plugins."""
    return list_plugins()


@router.get("/{plugin_name}")
def get_plugin_endpoint(
    plugin_name: str,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> PluginInfo:
    """Get plugin info by name."""
    plugin = get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.post("/install", response_model=dict)
def install_plugin_endpoint(
    plugin_path: str,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Install a plugin from a local path."""
    return install_plugin(Path(plugin_path)).model_dump()


@router.delete("/{plugin_name}")
def uninstall_plugin_endpoint(
    plugin_name: str,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Uninstall a plugin."""
    success = uninstall_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"message": "Plugin uninstalled"}


@router.post("/{plugin_name}/enable")
def enable_plugin_endpoint(
    plugin_name: str,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Enable a plugin."""
    success = enable_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"message": "Plugin enabled"}


@router.post("/{plugin_name}/disable")
def disable_plugin_endpoint(
    plugin_name: str,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Disable a plugin."""
    success = disable_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"message": "Plugin disabled"}


@router.post("/trigger-hook/{hook_name}")
def trigger_hook_endpoint(
    hook_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Trigger a hook across all plugins."""
    results = trigger_hook(hook_name, payload)
    return {"results": results}