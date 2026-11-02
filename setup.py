#!/usr/bin/env python3
"""JARVIS White-Label Setup Wizard.

Interactive setup for API keys and user preferences.
Run this once after cloning the repository.
"""

import os
import sys
import getpass
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.config import Config, create_default_config


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str):
    """Print a styled header."""
    width = 60
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
    print()


def print_step(step: int, total: int, title: str):
    """Print a step indicator."""
    print(f"  [{step}/{total}] {title}")
    print("-" * 40)


def get_hidden_input(prompt: str) -> str:
    """Get hidden input (for API keys)."""
    return getpass.getpass(prompt)


def validate_api_key(key: str) -> bool:
    """Basic validation for Gemini API key."""
    key = key.strip()
    return len(key) > 20 and key.startswith("AIza")


def main():
    clear_screen()
    print_header("JARVIS — Personal AI Assistant Setup")
    print("Welcome! This wizard will configure JARVIS for your system.")
    print("Your API keys are stored securely using Windows Credential Manager.")
    print()

    config = create_default_config()

    # Step 1: Gemini API Key
    print_step(1, 4, "Gemini API Key")
    print("Get your free API key from: https://aistudio.google.com/apikey")
    print()

    while True:
        api_key = get_hidden_input("  Enter Gemini API key (hidden): ").strip()
        if not api_key:
            print("  API key is required. Please try again.")
            continue
        if not validate_api_key(api_key):
            print("  Invalid API key format. Should start with 'AIza' and be longer.")
            retry = input("  Continue anyway? (y/N): ").strip().lower()
            if retry != "y":
                continue
        config.gemini_api_key = api_key
        print("  ✓ API key saved securely")
        break

    # Step 2: User Preferences
    print()
    print_step(2, 4, "Personal Preferences")
    print("These help JARVIS personalize responses. All optional.")
    print()

    name = input("  Your name (optional): ").strip()
    if name:
        config.set("user_name", name)

    language = input("  Preferred language [en-IN]: ").strip() or "en-IN"
    config.set("language", language)

    print("  Response style: brief / balanced / detailed")
    style = input("  Response style [balanced]: ").strip() or "balanced"
    if style in ("brief", "balanced", "detailed"):
        config.set("response_style", style)

    # Step 3: Model & Voice
    print()
    print_step(3, 4, "Model & Voice Settings")
    print("Available models: gemini-3.1-flash-live-preview, gemini-3.5-flash-live-preview")
    model = input(f"  Model [{config.get('model')}]: ").strip()
    if model:
        config.set("model", model)

    print("Available voices: Charon, Puck, Kore, Fenrir, Aoede")
    voice = input(f"  Voice [{config.get('voice')}]: ").strip()
    if voice:
        config.set("voice", voice)

    # Step 4: Create Desktop Shortcut
    print()
    print_step(4, 4, "Desktop Shortcut")
    create_shortcut = input("  Create 'Start JARVIS' desktop shortcut? (Y/n): ").strip().lower()
    if create_shortcut != "n":
        try:
            from create_shortcut import create_desktop_shortcut
            create_desktop_shortcut()
            print("  ✓ Desktop shortcut created")
        except Exception as e:
            print(f"  ⚠ Could not create shortcut: {e}")
            print("  You can run JARVIS with: python -m jarvis")

    # Final save
    config.save()

    print()
    print("=" * 60)
    print("  Setup complete! 🎉")
    print("=" * 60)
    print()
    print("  To start JARVIS:")
    print("    • Double-click 'Start JARVIS' on your desktop")
    print("    • Or run: python -m jarvis")
    print()
    print("  Try saying:")
    print("    • \"Jarvis, what's the weather?\"")
    print("    • \"Open YouTube and search for jazz\"")
    print("    • \"Set volume to 50 percent\"")
    print("    • \"Remember my name is Alex\"")
    print()
    input("  Press Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed: {e}")
        sys.exit(1)