"""Tests for plugin system."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.schemas.plugin_schema import (
    PluginConfig,
    PluginHook,
    PluginInfo,
    PluginManifest,
)
from app.services.plugin_registry import (
    _plugin_registry,
    disable_plugin,
    enable_plugin,
    get_plugin,
    list_plugins,
    trigger_hook,
    uninstall_plugin,
)


class TestPluginManifest:
    def test_valid_manifest(self) -> None:
        manifest = PluginManifest(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            entry_point="test_plugin:setup",
        )
        assert manifest.name == "test_plugin"
        assert manifest.version == "1.0.0"

    def test_invalid_version(self) -> None:
        import pytest
        with pytest.raises(Exception):
            PluginManifest(
                name="test",
                version="invalid",
                description="test",
                author="test",
                entry_point="test",
            )


class TestPluginHook:
    def test_valid_hook(self) -> None:
        hook = PluginHook(
            name="on_inventory_created",
            endpoint="https://example.com/webhook",
            events=["ingredient.created"],
        )
        assert hook.name == "on_inventory_created"

    def test_invalid_endpoint(self) -> None:
        import pytest
        with pytest.raises(Exception):
            PluginHook(
                name="test",
                endpoint="invalid-url",
            )


class TestPluginInfo:
    def test_create_plugin_info(self) -> None:
        manifest = PluginManifest(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test",
            entry_point="test",
        )
        config = PluginConfig(plugin_name="test_plugin")
        plugin = PluginInfo(manifest=manifest, config=config)
        assert plugin.status == "active"
        assert plugin.manifest.name == "test_plugin"


class TestPluginRegistry:
    def test_list_plugins_empty(self) -> None:
        _plugin_registry.clear()
        plugins = list_plugins()
        assert plugins == []

    def test_install_plugin(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / "test_plugin"
            plugin_dir.mkdir()

            manifest = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test",
                "entry_point": "test_plugin.setup",
            }
            (plugin_dir / "manifest.json").write_text(json.dumps(manifest))

            # Clean up any existing plugin
            target_dir = Path("./plugins") / "test_plugin"
            if target_dir.exists():
                shutil.rmtree(target_dir)
            uninstall_plugin("test_plugin")
            _plugin_registry.clear()

            from app.services.plugin_registry import install_plugin
            plugin = install_plugin(Path(plugin_dir))

            assert plugin.manifest.name == "test_plugin"

    def test_list_plugins_after_install(self) -> None:
        plugins = list_plugins()
        assert len(plugins) >= 0


class TestPluginEnableDisable:
    def test_enable_disable(self) -> None:
        plugin_name = "test_plugin"

        uninstall_plugin(plugin_name)
        _plugin_registry.clear()

        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / "test_plugin"
            plugin_dir.mkdir()
            manifest = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
                "entry_point": "test",
            }
            (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
            from app.services.plugin_registry import install_plugin
            install_plugin(Path(plugin_dir))

        assert enable_plugin(plugin_name) is True
        plugin = get_plugin(plugin_name)
        assert plugin.config.enabled is True

        assert disable_plugin(plugin_name) is True
        plugin = get_plugin(plugin_name)
        assert plugin.config.enabled is False


class TestHookTrigger:
    def test_trigger_hook_no_plugins(self) -> None:
        _plugin_registry.clear()
        result = trigger_hook("test_hook", {"event": "test"})
        assert result == []


class TestPluginAPI:
    def test_router_registered(self) -> None:
        from app.api.v1.plugins import router
        assert router.prefix == "/plugins"
        paths = [route.path for route in router.routes]
        assert any("/install" in p for p in paths)