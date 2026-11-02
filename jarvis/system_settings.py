"""Windows system settings control for JARVIS.

Provides volume, brightness, and settings page access using WMI and Windows APIs.
"""

import subprocess
import ctypes
from typing import Dict, Any, Optional, List
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import wmi


class SystemSettings:
    """Controls Windows system settings."""

    # Allowlisted settings pages
    SETTINGS_PAGES = {
        "display": "ms-settings:display",
        "sound": "ms-settings:sound",
        "volume mixer": "ms-settings:appsvolume",
        "audio devices": "ms-settings:sound-devices",
        "bluetooth": "ms-settings:bluetooth",
        "wifi": "ms-settings:network-wifi",
        "network": "ms-settings:network",
        "camera privacy": "ms-settings:privacy-webcam",
        "microphone privacy": "ms-settings:privacy-microphone",
        "default apps": "ms-settings:defaultapps",
        "personalization": "ms-settings:personalization",
        "windows update": "ms-settings:windowsupdate",
        "battery": "ms-settings:batterysaver",
        "storage": "ms-settings:storagesense",
        "notifications": "ms-settings:notifications",
        "time and language": "ms-settings:dateandtime",
        "accessibility": "ms-settings:easeofaccess",
    }

    def __init__(self):
        self._c = wmi.WMI()

    def execute(self, action: str, value: str = "") -> Dict[str, Any]:
        """Execute a system settings action.

        Args:
            action: One of get_status, get_volume, set_volume, volume_up, volume_down,
                    system_mute, system_unmute, get_brightness, set_brightness,
                    brightness_up, brightness_down, open_settings
            value: Numeric value for set actions, or settings page name for open_settings

        Returns:
            Dict with result
        """
        action = action.lower().strip()

        if action == "get_status":
            return self._get_status()

        elif action in ("get_volume", "set_volume", "volume_up", "volume_down", "system_mute", "system_unmute"):
            return self._volume_control(action, value)

        elif action in ("get_brightness", "set_brightness", "brightness_up", "brightness_down"):
            return self._brightness_control(action, value)

        elif action == "open_settings":
            return self._open_settings(value)

        else:
            raise ValueError(f"Unsupported system action: {action}")

    def _get_status(self) -> Dict[str, Any]:
        """Get current volume and brightness status."""
        vol = self._get_volume_internal()
        bright = self._get_brightness_internal()
        return {
            "volume": vol,
            "brightness": bright,
            "muted": vol.get("muted", False) if vol else None,
        }

    # --- Volume Control ---

    def _get_volume_internal(self) -> Dict[str, Any]:
        """Get current master volume."""
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            # New pycaw API uses EndpointVolume property
            volume = devices.EndpointVolume
            level = volume.GetMasterVolumeLevelScalar()
            muted = volume.GetMute()
            return {"level": round(level * 100), "muted": bool(muted)}
        except Exception as e:
            return {"error": f"Could not get volume: {e}"}

    def _set_volume_internal(self, level: int) -> Dict[str, Any]:
        """Set master volume (0-100)."""
        if not 0 <= level <= 100:
            raise ValueError("Volume must be between 0 and 100.")
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return {"level": level, "muted": False}
        except Exception as e:
            raise ValueError(f"Could not set volume: {e}")

    def _volume_control(self, action: str, value: str) -> Dict[str, Any]:
        current = self._get_volume_internal()
        if "error" in current:
            return current

        if action == "get_volume":
            return current

        elif action == "set_volume":
            if not value:
                raise ValueError("Provide a volume level (0-100).")
            level = int(value)
            return self._set_volume_internal(level)

        elif action == "volume_up":
            step = int(value) if value else 10
            new_level = min(100, current["level"] + step)
            return self._set_volume_internal(new_level)

        elif action == "volume_down":
            step = int(value) if value else 10
            new_level = max(0, current["level"] - step)
            return self._set_volume_internal(new_level)

        elif action == "system_mute":
            try:
                from pycaw.pycaw import AudioUtilities
                devices = AudioUtilities.GetSpeakers()
                volume = devices.EndpointVolume
                volume.SetMute(1, None)
                return {"muted": True, "level": current["level"]}
            except Exception as e:
                raise ValueError(f"Could not mute: {e}")

        elif action == "system_unmute":
            try:
                from pycaw.pycaw import AudioUtilities
                devices = AudioUtilities.GetSpeakers()
                volume = devices.EndpointVolume
                volume.SetMute(0, None)
                return {"muted": False, "level": current["level"]}
            except Exception as e:
                raise ValueError(f"Could not unmute: {e}")

    # --- Brightness Control ---

    def _get_brightness_internal(self) -> Dict[str, Any]:
        """Get current display brightness."""
        try:
            # WMI brightness (works for internal laptop displays)
            monitors = self._c.WmiMonitorBrightness()
            if monitors:
                return {"level": monitors[0].CurrentBrightness}
            return {"error": "No supported internal display found."}
        except Exception as e:
            return {"error": f"Could not get brightness: {e}"}

    def _set_brightness_internal(self, level: int) -> Dict[str, Any]:
        """Set display brightness (10-100)."""
        if not 10 <= level <= 100:
            raise ValueError("Brightness must be between 10 and 100.")
        try:
            methods = self._c.WmiMonitorBrightnessMethods()
            if methods:
                methods[0].WmiSetBrightness(level, 0)
                return {"level": level}
            raise ValueError("No supported internal display found.")
        except Exception as e:
            raise ValueError(f"Could not set brightness: {e}")

    def _brightness_control(self, action: str, value: str) -> Dict[str, Any]:
        current = self._get_brightness_internal()
        if "error" in current:
            return current

        if action == "get_brightness":
            return current

        elif action == "set_brightness":
            if not value:
                raise ValueError("Provide a brightness level (10-100).")
            level = int(value)
            return self._set_brightness_internal(level)

        elif action == "brightness_up":
            step = int(value) if value else 10
            new_level = min(100, current["level"] + step)
            return self._set_brightness_internal(new_level)

        elif action == "brightness_down":
            step = int(value) if value else 10
            new_level = max(10, current["level"] - step)
            return self._set_brightness_internal(new_level)

    # --- Settings Pages ---

    def _open_settings(self, page: str) -> Dict[str, Any]:
        """Open a Windows Settings page."""
        page = page.lower().strip()
        if page not in self.SETTINGS_PAGES:
            available = ", ".join(sorted(self.SETTINGS_PAGES.keys()))
            raise ValueError(f"Unknown settings page: {page}. Available: {available}")

        uri = self.SETTINGS_PAGES[page]
        try:
            subprocess.Popen(["start", "", uri], shell=True)
            return {"result": f"Opened {page} settings."}
        except Exception as e:
            raise ValueError(f"Could not open settings: {e}")

    def list_settings_pages(self) -> List[str]:
        """Get list of available settings pages."""
        return sorted(self.SETTINGS_PAGES.keys())


# Singleton instance
_system_settings = None


def get_system_settings() -> SystemSettings:
    """Get the singleton SystemSettings instance."""
    global _system_settings
    if _system_settings is None:
        _system_settings = SystemSettings()
    return _system_settings


def execute_system_setting(action: str, value: str = "") -> Dict[str, Any]:
    """Execute a system setting action (standalone function for tools)."""
    return get_system_settings().execute(action, value)