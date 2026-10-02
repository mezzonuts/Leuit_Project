import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ["DEBUG"] = "true"

_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)


@pytest.fixture(autouse=True)
def _clear_cache_between_tests() -> Iterator[None]:
    from app.core.cache import invalidate_cache

    invalidate_cache()
    yield
    invalidate_cache()
