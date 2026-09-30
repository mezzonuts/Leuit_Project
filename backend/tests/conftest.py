import os
import sys
from pathlib import Path

os.environ["DEBUG"] = "true"

_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
