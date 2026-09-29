#!/usr/bin/env python3
"""
LEUIT Desktop Launcher
Starts FastAPI backend and opens browser to frontend.
"""
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def launch_browser(port: int = 8000, delay: float = 1.5):
    """Open browser after server starts."""
    time.sleep(delay)
    url = f"http://127.0.0.1:{port}"
    print(f"🌐 Opening browser at {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")
        print(f"   Please manually open: {url}")

def main():
    """Main entry point."""
    print("=" * 50)
    print("  LEUIT - Lumbung Digital & Prediksi Stok Kafe")
    print("  Local-First F&B Demand & Inventory Forecasting")
    print("=" * 50)
    print()

    # Check for license file
    license_path = Path.home() / ".leuit" / "license.key"
    if not license_path.exists():
        print("⚠️  License file not found!")
        print(f"   Expected at: {license_path}")
        print("   Run: python scripts/generate_license.py")
        print()
        # Continue anyway for development

    # Check database
    db_path = Path(__file__).parent / "leuit_store.enc"
    if not db_path.exists():
        print("ℹ️  Database not found, will be created on first unlock")
        print()

    # Start browser in background thread
    browser_thread = threading.Thread(target=launch_browser, daemon=True)
    browser_thread.start()

    # Start FastAPI server
    print("🚀 Starting LEUIT Backend Server...")
    print("   Press Ctrl+C to stop")
    print()

    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="warning",
            access_log=False,
            reload=False,
        )
    except KeyboardInterrupt:
        print("\n👋 LEUIT stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()