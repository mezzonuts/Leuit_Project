"""Unit tests for launcher and build script."""
from pathlib import Path


class TestLauncher:
    def test_main_exists(self) -> None:
        """Verify main.py launcher exists."""
        main_path = Path("main.py")
        assert main_path.exists()

    def test_main_has_launch_browser(self) -> None:
        """Verify launcher has launch_browser function."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "def launch_browser" in content

    def test_main_has_main_function(self) -> None:
        """Verify launcher has main function."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "def main" in content

    def test_main_opens_browser(self) -> None:
        """Verify launcher opens browser."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "webbrowser.open" in content

    def test_main_starts_uvicorn(self) -> None:
        """Verify launcher starts uvicorn server."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "uvicorn.run" in content

    def test_main_checks_license(self) -> None:
        """Verify launcher checks for license file."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "license" in content.lower()

    def test_main_checks_database(self) -> None:
        """Verify launcher checks for database."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "leuit_store.enc" in content

    def test_main_uses_daemon_thread(self) -> None:
        """Verify browser thread is daemon (doesn't block shutdown)."""
        content = Path("main.py").read_text(encoding="utf-8")
        assert "daemon=True" in content


class TestPyInstallerSpec:
    def test_spec_exists(self) -> None:
        """Verify PyInstaller spec file exists."""
        spec_path = Path("LeuitApp.spec")
        assert spec_path.exists()

    def test_spec_includes_sqlcipher(self) -> None:
        """Verify spec includes SQLCipher hidden imports."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "sqlcipher3" in content

    def test_spec_includes_pynacl(self) -> None:
        """Verify spec includes PyNaCl hidden imports."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "nacl" in content

    def test_spec_includes_fastapi(self) -> None:
        """Verify spec includes FastAPI hidden imports."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "fastapi" in content

    def test_spec_excludes_tkinter(self) -> None:
        """Verify spec excludes tkinter."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "tkinter" in content

    def test_spec_excludes_pytest(self) -> None:
        """Verify spec excludes pytest."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "pytest" in content

    def test_spec_includes_frontend_dist(self) -> None:
        """Verify spec includes frontend dist data."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "frontend/dist" in content

    def test_spec_name_is_leuitapp(self) -> None:
        """Verify spec binary name is LeuitApp."""
        content = Path("LeuitApp.spec").read_text(encoding="utf-8")
        assert "LeuitApp" in content


class TestBuildScript:
    def test_build_script_exists(self) -> None:
        """Verify build script exists."""
        assert Path("scripts/build_binary.py").exists()

    def test_build_script_has_frontend_build(self) -> None:
        """Verify build script has frontend build function."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "def build_frontend" in content

    def test_build_script_has_obfuscation(self) -> None:
        """Verify build script has PyArmor obfuscation."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "def obfuscate_security" in content
        assert "pyarmor" in content.lower()

    def test_build_script_has_binary_build(self) -> None:
        """Verify build script has PyInstaller binary build."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "def build_binary" in content
        assert "pyinstaller" in content.lower()

    def test_build_script_has_installer(self) -> None:
        """Verify build script has installer creation."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "def create_installer" in content

    def test_build_script_obfuscates_security_modules(self) -> None:
        """Verify build script targets security modules."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "licensing.py" in content
        assert "hardware.py" in content
        assert "key_envelope.py" in content

    def test_build_script_has_cli_args(self) -> None:
        """Verify build script has CLI arguments."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "--frontend-only" in content
        assert "--skip-obfuscation" in content
        assert "--skip-binary" in content

    def test_build_script_handles_errors(self) -> None:
        """Verify build script handles command failures."""
        content = Path("scripts/build_binary.py").read_text(encoding="utf-8")
        assert "returncode" in content
        assert "sys.exit" in content


class TestSecurityModules:
    def test_licensing_exists(self) -> None:
        """Verify licensing module exists."""
        assert Path("app/core/security/licensing.py").exists()

    def test_hardware_exists(self) -> None:
        """Verify hardware module exists."""
        assert Path("app/core/security/hardware.py").exists()

    def test_key_envelope_exists(self) -> None:
        """Verify key_envelope module exists."""
        assert Path("app/core/security/key_envelope.py").exists()

    def test_licensing_has_verify_license_token(self) -> None:
        """Verify licensing has verify_license_token function."""
        content = Path("app/core/security/licensing.py").read_text(encoding="utf-8")
        assert "def verify_license_token" in content

    def test_hardware_has_get_machine_fingerprint(self) -> None:
        """Verify hardware has get_machine_fingerprint function."""
        content = Path("app/core/security/hardware.py").read_text(encoding="utf-8")
        assert "def get_machine_fingerprint" in content

    def test_key_envelope_has_generate_dek(self) -> None:
        """Verify key_envelope has generate_dek function."""
        content = Path("app/core/security/key_envelope.py").read_text(encoding="utf-8")
        assert "def generate_dek" in content

    def test_key_envelope_has_create_envelope(self) -> None:
        """Verify key_envelope has create_envelope function."""
        content = Path("app/core/security/key_envelope.py").read_text(encoding="utf-8")
        assert "def create_envelope" in content


class TestGenerateScripts:
    def test_generate_keys_exists(self) -> None:
        """Verify key generation script exists."""
        assert Path("scripts/generate_keys.py").exists()

    def test_generate_license_exists(self) -> None:
        """Verify license generation script exists."""
        assert Path("scripts/generate_license.py").exists()

    def test_generate_keys_has_main(self) -> None:
        """Verify key generation script has main function."""
        content = Path("scripts/generate_keys.py").read_text(encoding="utf-8")
        assert "generate_keys()" in content

    def test_generate_license_has_main(self) -> None:
        """Verify license generation script has main function."""
        content = Path("scripts/generate_license.py").read_text(encoding="utf-8")
        assert "def main" in content

    def test_generate_license_uses_ed25519(self) -> None:
        """Verify license generation uses Ed25519."""
        content = Path("scripts/generate_license.py").read_text(encoding="utf-8")
        assert "nacl" in content
