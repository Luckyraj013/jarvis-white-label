"""JARVIS — Personal AI Assistant (White-Label Edition)

A standalone, privacy-first personal AI assistant for Windows.
Runs entirely on your PC — no cloud dependencies for core features.
"""

__version__ = "1.0.0"
__author__ = "JARVIS Project"
__license__ = "MIT"

from .config import Config, load_config
from .preferences import Preferences

__all__ = ["Config", "load_config", "Preferences"]