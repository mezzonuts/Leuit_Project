"""Plugin registry and lifecycle management."""
from __future__ import annotations

import hashlib
import importlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.plugin_schema import (
    PluginConfig,
    PluginHook,
    PluginInfo,
    PluginManifest,
)

logger = logging.getLogger(__name__)

PLUGIN_DIR = Path("./plugins")
PLUGIN_DIR.mkdir(parents=True, exist_ok=True)

_plugin_registry: dict[str, PluginInfo] = {}


def discover_plugins() -> list[PluginInfo]:
    """Discover installed plugins from plugin directory."""
    plugins = []
    for plugin_dir in PLUGIN_DIR.iterdir():
        if not plugin_dir.is_dir():
            continue

        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            with open(manifest_path) as f:
                manifest_data = json.load(f)
            manifest = PluginManifest(**manifest_data)

            config_path = plugin_dir / "config.json"
            config = PluginConfig(plugin_name=manifest.name)
            if config_path.exists():
                with open(config_path) as f:
                    config_data = json.load(f)
                    config = PluginConfig(plugin_name=manifest.name, **config_data)

            hooks_path = plugin_dir / "hooks.json"
            hooks = []
            if hooks_path.exists():
                with open(hooks_path) as f:
                    hooks_data = json.load(f)
                    hooks = [PluginHook(**h) for h in hooks_data]

            plugin_info = PluginInfo(
                manifest=manifest,
                config=config,
                hooks=hooks,
                status="active",
            )
            _plugin_registry[manifest.name] = plugin_info
            plugins.append(plugin_info)

        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_dir}: {e}")

    return plugins


def load_plugin(plugin_name: str) -> bool:
    """Load a plugin by importing its entry point."""
    plugin_info = _plugin_registry.get(plugin_name)
    if not plugin_info:
        return False

    try:
        module = importlib.import_module(plugin_info.manifest.entry_point)

        if hasattr(module, "setup"):
            module.setup()

        logger.info(f"Plugin loaded: {plugin_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_name}: {e}")
        _plugin_registry[plugin_name].status = "error"
        _plugin_registry[plugin_name].error_message = str(e)
        return False


def install_plugin(plugin_path: Path) -> PluginInfo:
    """Install a plugin from a directory."""
    manifest_path = plugin_path / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("Plugin must have manifest.json")

    with open(manifest_path) as f:
        manifest_data = json.load(f)
    manifest = PluginManifest(**manifest_data)

    target_dir = PLUGIN_DIR / manifest.name
    if target_dir.exists():
        raise ValueError(f"Plugin {manifest.name} already installed")

    import shutil
    shutil.copytree(plugin_path, target_dir)

    config = PluginConfig(plugin_name=manifest.name)
    plugin_info = PluginInfo(manifest=manifest, config=config)
    _plugin_registry[manifest.name] = plugin_info

    return plugin_info


def uninstall_plugin(plugin_name: str) -> bool:
    """Uninstall a plugin."""
    import shutil

    plugin_info = _plugin_registry.get(plugin_name)
    if not plugin_info:
        return False

    plugin_dir = PLUGIN_DIR / plugin_name
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)

    del _plugin_registry[plugin_name]
    return True


def get_plugin(plugin_name: str) -> PluginInfo | None:
    """Get plugin info by name."""
    return _plugin_registry.get(plugin_name)


def list_plugins() -> list[PluginInfo]:
    """List all installed plugins."""
    return list(_plugin_registry.values())


def enable_plugin(plugin_name: str) -> bool:
    """Enable a plugin."""
    plugin = _plugin_registry.get(plugin_name)
    if not plugin:
        return False
    plugin.config.enabled = True
    plugin.config.updated_at = datetime.now(UTC).isoformat()
    plugin.status = "active"
    return True


def disable_plugin(plugin_name: str) -> bool:
    """Disable a plugin."""
    plugin = _plugin_registry.get(plugin_name)
    if not plugin:
        return False
    plugin.config.enabled = False
    plugin.config.updated_at = datetime.now(UTC).isoformat()
    plugin.status = "disabled"
    return True


def trigger_hook(hook_name: str, payload: dict) -> list[dict]:
    """Trigger a hook across all plugins with that hook."""
    import hmac

    import httpx

    results = []
    for plugin_info in _plugin_registry.values():
        if not plugin_info.config.enabled:
            continue

        hook = next((h for h in plugin_info.hooks if h.name == hook_name), None)
        if not hook:
            continue

        event_match = any(e in hook.events for e in payload.get("event", ""))
        if not event_match and hook.events:
            continue

        payload_bytes = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}

        if hook.secret:
            signature = hmac.new(
                hook.secret.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            headers["X-Signature"] = signature

        try:
            with httpx.Client(timeout=hook.timeout_seconds) as client:
                for attempt in range(hook.retry_count):
                    try:
                        response = client.post(hook.endpoint, json=payload, headers=headers)
                        response.raise_for_status()
                        results.append({
                            "plugin": plugin_info.manifest.name,
                            "hook": hook_name,
                            "status": "success",
                            "status_code": response.status_code,
                        })
                        break
                    except Exception as e:
                        if attempt == hook.retry_count - 1:
                            results.append({
                                "plugin": plugin_info.manifest.name,
                                "hook": hook_name,
                                "status": "failed",
                                "error": str(e),
                            })
        except Exception as e:
            logger.error(f"Hook {hook_name} failed for plugin {plugin_info.manifest.name}: {e}")
            results.append({
                "plugin": plugin_info.manifest.name,
                "hook": hook_name,
                "status": "failed",
                "error": str(e),
            })

    return results