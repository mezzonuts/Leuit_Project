"""Tests for public menu and receipt endpoints."""
from __future__ import annotations

from unittest.mock import MagicMock


class TestPublicMenu:
    def test_public_menu_endpoint_registered(self) -> None:
        from app.api.v1.public_menu import router
        assert router.prefix == "/public"
        paths = [route.path for route in router.routes]
        assert any("/menu" in p for p in paths)

    def test_public_menu_returns_structure(self) -> None:
        from app.api.v1.public_menu import get_public_menu
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        
        result = get_public_menu(db=db)
        
        assert "items" in result
        assert "total" in result
        assert isinstance(result["items"], list)
        assert result["total"] == 0
