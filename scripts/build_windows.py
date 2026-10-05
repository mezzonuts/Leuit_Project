#!/usr/bin/env python3
"""
LEUIT Windows Packager
Builds a standalone Windows executable with all dependencies bundled.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DIST_DIR = BACKEND_DIR / "dist"
BUILD_DIR = BACKEND_DIR / "build"

def run_cmd(cmd, cwd=None, check=True):
    """Run command and return result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result

def clean_build_dirs():
    """Clean previous build artifacts."""
    print("=== Cleaning build directories ===")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"Removed: {d}")

def check_frontend_build():
    """Ensure frontend is built."""
    dist_dir = FRONTEND_DIR / "dist"
    if not dist_dir.exists():
        print("=== Building frontend ===")
        run_cmd("pnpm install", cwd=FRONTEND_DIR)
        run_cmd("pnpm build", cwd=FRONTEND_DIR)
    else:
        print("Frontend already built")

def find_sqlcipher_dll():
    """Find SQLCipher DLL for bundling."""
    # Common locations
    possible_paths = [
        Path(os.environ.get("CONDA_PREFIX", "")) / "Library" / "bin" / "sqlcipher.dll",
        Path(os.environ.get("CONDA_PREFIX", "")) / "Library" / "bin" / "libsqlcipher-0.dll",
        Path(sys.prefix) / "Library" / "bin" / "sqlcipher.dll",
        Path(sys.prefix) / "Library" / "bin" / "libsqlcipher-0.dll",
        Path("C:/Program Files/SQLCipher") / "sqlcipher.dll",
        Path("C:/Program Files/SQLCipher") / "libsqlcipher-0.dll",
    ]
    for p in possible_paths:
        if p.exists():
            print(f"Found SQLCipher DLL: {p}")
            return p
    return None

def build_executable():
    """Build the Windows executable with PyInstaller."""
    print("=== Building executable with PyInstaller ===")
    
    # Find SQLCipher DLL
    sqlcipher_dll = find_sqlcipher_dll()
    
    # Prepare PyInstaller command
    cmd_parts = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "LeuitApp",
        "--icon", str(FRONTEND_DIR / "public" / "favicon.ico") if (FRONTEND_DIR / "public" / "favicon.ico").exists() else "NONE",
        "--add-data", f"{FRONTEND_DIR / 'dist'};dist",
        "--hidden-import", "sqlcipher3",
        "--hidden-import", "pynacl",
        "--hidden-import", "cryptography",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off",
        "--collect-all", "sqlalchemy",
        "--collect-all", "pydantic",
        "--collect-all", "fastapi",
        "--collect-all", "pydantic_core",
        "--collect-all", "pydantic_settings",
        "--collect-all", "cryptography",
        "--collect-all", "pynacl",
        "--noconsole",
    ]
    
    # Add SQLCipher DLL if found
    if sqlcipher_dll:
        dll_name = sqlcipher_dll.name
        cmd_parts.extend(["--add-binary", f"{sqlcipher_dll};."])
        print(f"Bundling SQLCipher DLL: {dll_name}")
    
    # Add main.py as entry point
    cmd_parts.append(str(BACKEND_DIR / "main.py"))
    
    cmd = " ".join(cmd_parts)
    run_cmd(cmd, cwd=BACKEND_DIR)

def create_portable_package():
    """Create a portable zip package for distribution."""
    print("=== Creating portable package ===")
    
    app_dir = DIST_DIR / "LeuitApp"
    if not app_dir.exists():
        raise RuntimeError(f"App directory not found: {app_dir}")
    
    # Create a clean package directory
    package_dir = DIST_DIR / "LeuitApp_Portable"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy app files
    shutil.copytree(app_dir, package_dir / "LeuitApp", dirs_exist_ok=True)
    
    # Create README
    readme_content = """LEUIT - Lumbung Digital & Prediksi Stok Kafe
===============================================

CARA MENJALANKAN:
1. Ekstrak file ZIP ini ke folder pilihan Anda
2. Jalankan LeuitApp.exe
3. Aplikasi akan otomatis membuka browser ke http://localhost:8000

SYARAT SISTEM:
- Windows 10/11 (64-bit)
- RAM minimal 4 GB
- Ruang disk minimal 500 MB

PENGELOLAAN DATA:
- Database tersimpan di folder yang sama dengan executable (leuit_store.enc)
- Backup: copy file leuit_store.enc ke lokasi aman
- Restore: copy file backup ke folder aplikasi

DUKUNGAN:
- Email: support@leuit.app
- Docs: https://docs.leuit.app

Version: 1.9.0
Build: Sprint 2 Complete (28 Days)
"""
    (package_dir / "README.txt").write_text(readme_content, encoding="utf-8")
    
    # Create zip
    zip_path = DIST_DIR / "LeuitApp_Windows_Portable.zip"
    print(f"Creating zip: {zip_path}")
    shutil.make_archive(str(DIST_DIR / "LeuitApp_Windows_Portable"), 'zip', package_dir)
    print(f"Package created: {zip_path}")
    
    return zip_path

def main():
    print("=" * 60)
    print("LEUIT Windows Packager")
    print("=" * 60)
    
    try:
        clean_build_dirs()
        check_frontend_build()
        build_executable()
        zip_path = create_portable_package()
        
        print("=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"Executable: {BACKEND_DIR / 'dist' / 'LeuitApp' / 'LeuitApp.exe'}")
        print(f"Portable Package: {BACKEND_DIR / 'dist' / 'LeuitApp_Windows_Portable.zip'}")
        print()
        print("To test: Run the executable and verify it opens browser to localhost:8000")
        
    except Exception as e:
        print(f"BUILD FAILED: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()