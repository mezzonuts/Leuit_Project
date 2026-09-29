#!/usr/bin/env python3
"""
Build script for LEUIT Desktop App.
Handles PyArmor obfuscation and PyInstaller packaging.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, env=None):
    """Run command and return success status."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        return False
    print("✅ Command completed successfully")
    return True

def build_frontend():
    """Build frontend with Vite."""
    print("\n📦 Building Frontend...")
    frontend_dir = Path(__file__).parent.parent / "frontend"
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        if not run_command("pnpm install", cwd=frontend_dir):
            return False

    # Build
    if not run_command("pnpm build", cwd=frontend_dir):
        return False

    print("✅ Frontend built successfully")
    return True

def obfuscate_security():
    """Obfuscate security modules with PyArmor."""
    print("\n🔒 Obfuscating security modules with PyArmor...")

    security_files = [
        "app/core/security/licensing.py",
        "app/core/security/hardware.py",
        "app/core/security/key_envelope.py",
    ]

    for f in security_files:
        if not Path(f).exists():
            print(f"⚠️  File not found: {f}")

    # Run PyArmor
    cmd = "pyarmor gen --exact " + " ".join(security_files)
    if not run_command(cmd):
        print("⚠️  PyArmor failed, continuing without obfuscation...")
        return False

    print("✅ Security modules obfuscated")
    return True

def build_binary():
    """Build binary with PyInstaller."""
    print("\n🏗️  Building binary with PyInstaller...")

    spec_file = "LeuitApp.spec"
    if not Path(spec_file).exists():
        print(f"❌ Spec file not found: {spec_file}")
        return False

    # Clean previous builds
    for dir_name in ["build", "dist", "__pycache__"]:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)

    # Run PyInstaller
    cmd = f"pyinstaller --noconfirm {spec_file}"
    if not run_command(cmd):
        return False

    print("✅ Binary built successfully")
    return True

def create_installer():
    """Create installer package (Windows NSIS or macOS DMG)."""
    print("\n📦 Creating installer package...")

    if sys.platform == "win32":
        # Windows: Could use NSIS or Inno Setup
        print("⚠️  Windows installer creation not implemented yet")
        print("   Binary available at: dist/LeuitApp/LeuitApp.exe")
    elif sys.platform == "darwin":
        # macOS: Create DMG
        print("⚠️  macOS DMG creation not implemented yet")
        print("   Binary available at: dist/LeuitApp/LeuitApp.app")
    else:
        print("⚠️  Linux packaging not implemented yet")

    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build LEUIT Desktop App")
    parser.add_argument("--frontend-only", action="store_true", help="Only build frontend")
    parser.add_argument("--skip-obfuscation", action="store_true", help="Skip PyArmor obfuscation")
    parser.add_argument("--skip-binary", action="store_true", help="Skip PyInstaller binary build")

    args = parser.parse_args()

    print("🚀 LEUIT Build Script")
    print("=" * 50)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    success = True

    if not args.frontend_only:
        if not build_frontend():
            success = False

    if success and not args.skip_obfuscation:
        obfuscate_security()

    if success and not args.skip_binary:
        if not build_binary():
            success = False

    if success:
        create_installer()

    if success:
        print("\n🎉 Build completed successfully!")
        if sys.platform == "win32":
            print(f"   Binary: {backend_dir}/dist/LeuitApp/LeuitApp.exe")
        elif sys.platform == "darwin":
            print(f"   App: {backend_dir}/dist/LeuitApp/LeuitApp.app")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()