"""Configuration management for JARVIS White-Label.

Handles secure storage of API keys, user preferences, and application settings.
Uses Windows Credential Manager (DPAPI) for secrets.
"""

import json
import os
import getpass
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
import ctypes
import ctypes.wintypes

# Windows DPAPI constants
CRYPTPROTECT_UI_FORBIDDEN = 0x01
CRYPTPROTECT_LOCAL_MACHINE = 0x04


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _dpapi_encrypt(data: bytes) -> bytes:
    """Encrypt data using Windows DPAPI (user scope)."""
    blob_in = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte)))
    blob_out = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(blob_in), None, None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(blob_out)
    ):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


def _dpapi_decrypt(encrypted: bytes) -> bytes:
    """Decrypt data using Windows DPAPI (user scope)."""
    blob_in = DATA_BLOB(len(encrypted), ctypes.cast(encrypted, ctypes.POINTER(ctypes.c_byte)))
    blob_out = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(blob_out)
    ):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


class Config:
    """Main configuration class for JARVIS."""

    DEFAULT_CONFIG_DIR = Path.home() / ".jarvis"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
    DEFAULT_PREFS_FILE = DEFAULT_CONFIG_DIR / "preferences.json"

    # Default values
    DEFAULTS = {
        "model": "gemini-3.1-flash-live-preview",
        "voice": "Charon",
        "language": "en-IN",
        "response_style": "balanced",
        "user_name": "",
        "data_dir": str(DEFAULT_CONFIG_DIR),
        "allowed_folders": [
            "Desktop",
            "Documents",
            "Downloads",
            "Pictures",
            "Music",
            "Videos",
        ],
        "protected_folders": ["Codex", ".jarvis"],
        "approval_timeout_seconds": 120,
        "browser_headless": False,
        "browser_timeout_seconds": 30,
        "search_max_results": 10,
        "voice_sensitivity": "low",
        "silence_duration_ms": 750,
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self.config_dir = self.config_path.parent
        self._config: Dict[str, Any] = {}
        self._secrets: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load main config
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        else:
            self._config = {}

        # Merge with defaults
        for key, value in self.DEFAULTS.items():
            if key not in self._config:
                self._config[key] = value

        # Load secrets from DPAPI
        secrets_path = self.config_dir / "secrets.bin"
        if secrets_path.exists():
            try:
                encrypted = secrets_path.read_bytes()
                decrypted = _dpapi_decrypt(encrypted)
                self._secrets = json.loads(decrypted.decode("utf-8"))
            except Exception:
                self._secrets = {}

    def save(self) -> None:
        """Save configuration to disk."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)

        # Save secrets encrypted
        if self._secrets:
            encrypted = _dpapi_encrypt(json.dumps(self._secrets).encode("utf-8"))
            secrets_path = self.config_dir / "secrets.bin"
            secrets_path.write_bytes(encrypted)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        self.save()

    def get_secret(self, key: str) -> Optional[str]:
        """Get a secret value (API key, etc.)."""
        return self._secrets.get(key)

    def set_secret(self, key: str, value: str) -> None:
        """Set a secret value (encrypted)."""
        self._secrets[key] = value
        self.save()

    def delete_secret(self, key: str) -> None:
        """Delete a secret value."""
        if key in self._secrets:
            del self._secrets[key]
            self.save()

    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get the Gemini API key."""
        return self.get_secret("gemini_api_key")

    @gemini_api_key.setter
    def gemini_api_key(self, value: str) -> None:
        self.set_secret("gemini_api_key", value)

    @property
    def is_configured(self) -> bool:
        """Check if JARVIS is fully configured."""
        return bool(self.gemini_api_key)

    @property
    def data_dir(self) -> Path:
        """Get the data directory."""
        return Path(self.get("data_dir", str(self.DEFAULT_CONFIG_DIR)))

    @property
    def allowed_roots(self) -> list[Path]:
        """Get allowed folder roots for file operations."""
        roots = []
        home = Path.home()
        for folder in self.get("allowed_folders", []):
            path = home / folder
            if path.exists():
                roots.append(path.resolve())
        return roots

    @property
    def protected_roots(self) -> list[Path]:
        """Get protected folder roots."""
        roots = []
        home = Path.home()
        for folder in self.get("protected_folders", []):
            path = home / folder
            if path.exists():
                roots.append(path.resolve())
        # Always protect the JARVIS data dir and project folder
        roots.append(self.data_dir.resolve())
        project_root = Path(__file__).resolve().parent.parent
        if project_root != home:
            roots.append(project_root.resolve())
        return roots


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from the default or specified path."""
    return Config(config_path)


def create_default_config() -> Config:
    """Create a new default configuration."""
    config = Config()
    config.save()
    return config