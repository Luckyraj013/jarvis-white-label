"""User preferences for JARVIS.

Manages user-specific preferences like name, language, response style.
Stored as plain JSON (non-sensitive data).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import load_config


class Preferences:
    """User preferences manager."""

    FIELDS = {
        "name",
        "language",
        "response_style",
        "timezone",
        "time_format",
        "date_format",
        "units",
        "response_length",
        "currency",
        "home_city",
    }

    BLOCKED_WORDS = {
        "password", "passwd", "secret", "token", "api_key", "credential",
        "pin", "otp", "card_number", "cvv", "private_key",
    }

    CHOICES = {
        "time_format": {"12h", "24h"},
        "date_format": {"dmy", "mdy", "iso"},
        "units": {"metric", "imperial"},
        "response_length": {"brief", "balanced", "detailed"},
    }

    def __init__(self, config: Optional["Config"] = None):
        self.config = config or load_config()
        self.prefs_path = self.config.data_dir / "preferences.json"
        self._prefs: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        """Load preferences from disk."""
        if self.prefs_path.exists():
            try:
                with open(self.prefs_path, "r", encoding="utf-8") as f:
                    self._prefs = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._prefs = {}
        else:
            self._prefs = {}

    def save(self) -> None:
        """Save preferences to disk."""
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.prefs_path, "w", encoding="utf-8") as f:
            json.dump(self._prefs, f, indent=2)

    def get(self, key: str, default: str = "") -> str:
        """Get a preference value."""
        return self._prefs.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set a preference value with validation."""
        validated = self.validate({key: value})
        self._prefs.update(validated)
        self.save()

    def delete(self, key: str) -> None:
        """Delete a preference."""
        if key in self._prefs:
            del self._prefs[key]
            self.save()

    def clear(self) -> None:
        """Clear all preferences."""
        self._prefs = {}
        self.save()

    def all(self) -> Dict[str, str]:
        """Get all preferences."""
        return dict(self._prefs)

    def validate(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Validate preference data."""
        if not isinstance(data, dict) or len(data) > 50:
            raise ValueError("Preferences must be an object with no more than 50 fields.")

        result = {}
        for field, value in data.items():
            if not isinstance(field, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", field):
                raise ValueError("Preference names must be safe short identifiers.")
            if any(word in field.lower() for word in self.BLOCKED_WORDS):
                raise ValueError("Preference names cannot describe secrets.")

            if not isinstance(value, str) or not 1 <= len(value.strip()) <= 300:
                raise ValueError("Preference values must be short text (1-300 chars).")
            if any(ord(c) < 32 for c in value):
                raise ValueError("Preference values cannot contain control characters.")

            value = value.strip()

            if field == "timezone":
                try:
                    ZoneInfo(value)
                except ZoneInfoNotFoundError as error:
                    raise ValueError("Use a valid IANA time zone.") from error

            if field in self.CHOICES and value not in self.CHOICES[field]:
                raise ValueError(f"Invalid {field} value. Choose from: {', '.join(self.CHOICES[field])}")

            if field == "currency" and (len(value) != 3 or not value.isalpha() or not value.isupper()):
                raise ValueError("Currency must be a three-letter code (e.g., USD).")

            result[field] = value

        return result

    def update_multiple(self, data: Dict[str, str]) -> Dict[str, str]:
        """Update multiple preferences at once."""
        validated = self.validate(data)
        self._prefs.update(validated)
        self.save()
        return validated

    def instruction_data(self) -> str:
        """Generate instruction text for the AI model."""
        if not self._prefs:
            return ""

        lines = ["\nSaved user preferences (apply these in conversation):"]
        for key, value in self._prefs.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


def change_preference(config: Config, field: str, value: str = "") -> Dict[str, str]:
    """Change a single preference (standalone function for tools)."""
    prefs = Preferences(config)
    if value:
        prefs.set(field, value)
    else:
        prefs.delete(field)
    return prefs.all()


def read_preferences(config: Config) -> Dict[str, str]:
    """Read all preferences (standalone function for tools)."""
    prefs = Preferences(config)
    return prefs.all()