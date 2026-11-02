#!/usr/bin/env python3
"""Create desktop shortcut for JARVIS."""

import os
import sys
from pathlib import Path
import subprocess


def get_desktop_path() -> Path:
    """Get the actual desktop path, handling OneDrive redirection."""
    # Check common desktop locations
    user_profile = Path(os.environ.get("USERPROFILE", ""))
    
    # OneDrive desktop (common on Windows 10/11)
    onedrive = os.environ.get("OneDrive", "")
    if onedrive:
        od_desktop = Path(onedrive) / "Desktop"
        if od_desktop.exists():
            return od_desktop
    
    # Standard desktop
    std_desktop = user_profile / "Desktop"
    if std_desktop.exists():
        return std_desktop
    
    # Fallback to user profile
    return user_profile


def create_desktop_shortcut():
    """Create a 'Start JARVIS' shortcut on the desktop."""
    # Get paths
    project_dir = Path(__file__).parent.resolve()
    python_exe = Path(sys.executable).resolve()
    desktop = get_desktop_path()
    shortcut_path = desktop / "Start JARVIS.lnk"

    # Create a VBS script to make the shortcut (more reliable than COM)
    vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{python_exe}"
oLink.Arguments = "-m jarvis"
oLink.WorkingDirectory = "{project_dir}"
oLink.Description = "Start JARVIS Personal AI Assistant"
oLink.IconLocation = "{project_dir / 'jarvis.ico'}"
oLink.Save
'''

    vbs_path = project_dir / "create_shortcut.vbs"
    vbs_path.write_text(vbs_script.strip())

    try:
        subprocess.run(["wscript", str(vbs_path)], check=True, capture_output=True)
        print(f"Created shortcut: {shortcut_path}")
    finally:
        if vbs_path.exists():
            vbs_path.unlink()


def create_startup_shortcut():
    """Create a startup shortcut for auto-launch (optional)."""
    project_dir = Path(__file__).parent.resolve()
    python_exe = Path(sys.executable).resolve()
    startup = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup / "Start JARVIS (Hidden).lnk"

    vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{python_exe}"
oLink.Arguments = "-m jarvis"
oLink.WorkingDirectory = "{project_dir}"
oLink.Description = "Start JARVIS at login (hidden)"
oLink.WindowStyle = 7  ' Minimized
oLink.Save
'''

    vbs_path = project_dir / "create_startup.vbs"
    vbs_path.write_text(vbs_script.strip())

    try:
        subprocess.run(["wscript", str(vbs_path)], check=True, capture_output=True)
        print(f"Created startup shortcut: {shortcut_path}")
    finally:
        if vbs_path.exists():
            vbs_path.unlink()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--startup":
        create_startup_shortcut()
    else:
        create_desktop_shortcut()