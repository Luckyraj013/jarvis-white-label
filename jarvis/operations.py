"""Local Windows operations for JARVIS.

Provides bounded file operations, app launching, and system control
with approval required for destructive actions.
"""

import os
import secrets
import subprocess
import time
import ctypes
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .config import load_config


@dataclass
class ApprovalRequest:
    """A pending approval request."""
    action: str
    path: str
    destination: str
    fingerprint: Optional[tuple]
    code: str
    summary: str
    expires: float
    state: str  # pending, approved, rejected, executing, completed, failed, expired
    result: Optional[str] = None


class Operations:
    """Manages local Windows operations with approval system."""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.pending: Dict[str, ApprovalRequest] = {}  # room -> request
        self._approvals_file = self.config.data_dir / "approvals.json"
        self._load_approvals()

        # Supported apps
        self.APPS = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "file explorer": "explorer.exe",
        }

        # Power action delay
        self.POWER_DELAY_SECONDS = 30

    def _load_approvals(self) -> None:
        """Load pending approvals from disk."""
        if self._approvals_file.exists():
            try:
                with open(self._approvals_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for room, item in data.items():
                    if item.get("state") == "pending" and time.time() < item.get("expires", 0):
                        item["fingerprint"] = tuple(item["fingerprint"]) if item.get("fingerprint") else None
                        self.pending[room] = ApprovalRequest(**item)
            except Exception:
                pass

    def _save_approvals(self) -> None:
        """Save pending approvals to disk."""
        data = {}
        for room, req in self.pending.items():
            item = asdict(req)
            if item["fingerprint"]:
                item["fingerprint"] = list(item["fingerprint"])
            data[room] = item
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self._approvals_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _cleanup_expired(self) -> None:
        """Remove expired approvals."""
        now = time.time()
        expired = [room for room, req in self.pending.items() if req.state == "pending" and now > req.expires]
        for room in expired:
            self.pending[room].state = "expired"
        self._save_approvals()

    def request(self, room: str, action: str, path: str = "", destination: str = "") -> Dict[str, Any]:
        """Request a local operation. Returns status dict."""
        self._cleanup_expired()

        # Handle simple actions that don't need approval
        if action == "open_app":
            return self._open_app(path)
        if action == "cancel_shutdown":
            return self._cancel_shutdown()
        if action == "status":
            return self.status(room)

        # Validate action
        if action not in ("list_folder", "open_folder", "create_folder", "rename", "move", "delete", "shutdown", "restart", "lock"):
            raise ValueError(f"Unsupported local operation: {action}")

        # Check for existing pending request
        existing = self.pending.get(room)
        if existing and existing.state == "pending":
            raise ValueError("Approve or reject the current operation before requesting another.")

        # Validate path for file operations
        source = None
        if action not in ("shutdown", "restart", "lock"):
            source = self._validate_path(path)

        # Execute read-only operations immediately
        if action == "list_folder":
            return self._list_folder(source)
        if action == "open_folder":
            return self._open_folder(source)
        if action == "create_folder":
            return self._create_folder(source)

        # For destructive actions, create approval request
        target = None
        if action in ("rename", "move"):
            target = self._validate_path(destination)
            if target.exists() or not target.parent.is_dir():
                raise ValueError("Destination must not exist and its parent folder must exist.")
            if action == "rename" and target.parent != source.parent:
                raise ValueError("Rename must stay in the same folder. Use move for a different folder.")
            if target.is_relative_to(source):
                raise ValueError("Cannot move an item inside itself.")

        if source is not None and not source.exists():
            raise ValueError("Source does not exist.")

        # Create approval request
        code = str(secrets.randbelow(900000) + 100000)  # 6-digit code

        if source is None:
            summary = (
                "Lock this PC. You will need to sign in again."
                if action == "lock"
                else f"{action.title()} this PC in {self.POWER_DELAY_SECONDS} seconds. Unsaved work may be lost."
            )
        else:
            summary = f"{action.title()}: {source}"
            if target:
                summary += f" → {target}"
            elif action == "delete":
                summary += " (send to Recycle Bin, including folder contents)"

        fp = self._fingerprint(source) if source else None

        req = ApprovalRequest(
            action=action,
            path=str(source) if source else "",
            destination=str(target) if target else "",
            fingerprint=fp,
            code=code,
            summary=summary,
            expires=time.time() + self.config.get("approval_timeout_seconds", 120),
            state="pending",
        )
        self.pending[room] = req
        self._save_approvals()

        return self.status(room)

    def status(self, room: str) -> Dict[str, Any]:
        """Get the status of a pending request."""
        self._cleanup_expired()
        req = self.pending.get(room)
        if not req:
            return {"state": "none"}

        result = {
            "action": req.action,
            "path": req.path,
            "destination": req.destination,
            "code": req.code,
            "summary": req.summary,
            "expires_in": max(0, int(req.expires - time.time())),
            "state": req.state,
        }
        if req.result:
            result["result"] = req.result
        return result

    def decide(self, room: str, code: str, approve: bool) -> Dict[str, Any]:
        """Approve or reject a pending request."""
        self._cleanup_expired()
        req = self.pending.get(room)

        if not req or req.state != "pending" or not secrets.compare_digest(str(code), req.code):
            raise ValueError("No matching unexpired approval request.")

        req.state = "rejected" if not approve else "executing"
        self._save_approvals()

        if not approve:
            return self.status(room)

        # Execute the approved action
        try:
            action = req.action
            if action in ("shutdown", "restart"):
                self._execute_power_action(action)
            elif action == "lock":
                self._lock_workstation()
            else:
                source = Path(req.path)
                if req.fingerprint and self._fingerprint(source) != req.fingerprint:
                    raise ValueError("The source changed after approval was requested. Request approval again.")

                if action == "delete":
                    self._delete_to_recycle_bin(source)
                elif action == "rename":
                    target = Path(req.destination)
                    if target.exists():
                        raise ValueError("Destination already exists; nothing was overwritten.")
                    source.rename(target)
                elif action == "move":
                    target = Path(req.destination)
                    if target.exists():
                        raise ValueError("Destination already exists; nothing was overwritten.")
                    source.rename(target)

            req.state = "completed"
            req.result = "Operation completed successfully."
        except Exception as error:
            req.state = "failed"
            req.result = str(error) if isinstance(error, ValueError) else type(error).__name__

        self._save_approvals()
        return self.status(room)

    # --- Read-only operations ---

    def _list_folder(self, path: Path) -> Dict[str, Any]:
        if not path.is_dir():
            raise ValueError("Folder does not exist.")
        items = []
        for p in sorted(path.iterdir())[:100]:
            items.append({"name": p.name, "folder": p.is_dir()})
        return {"path": str(path), "items": items}

    def _open_folder(self, path: Path) -> Dict[str, Any]:
        if not path.is_dir():
            raise ValueError("Folder does not exist.")
        os.startfile(str(path))
        return {"result": "Folder opening requested."}

    def _create_folder(self, path: Path) -> Dict[str, Any]:
        path.mkdir(exist_ok=False)
        return {"result": "Folder created.", "path": str(path)}

    # --- Simple actions ---

    def _open_app(self, app_name: str) -> Dict[str, Any]:
        executable = self.APPS.get(app_name.lower().strip())
        if not executable:
            raise ValueError("Supported apps: Notepad, Calculator, File Explorer.")
        try:
            subprocess.Popen([str(Path(os.environ["WINDIR"]) / "System32" / executable)])
            return {"result": f"{app_name.title()} launch requested."}
        except Exception as e:
            raise ValueError(f"Failed to launch app: {e}")

    def _cancel_shutdown(self) -> Dict[str, Any]:
        shutdown_exe = Path(os.environ["WINDIR"]) / "System32" / "shutdown.exe"
        subprocess.run([str(shutdown_exe), "/a"], check=True, timeout=10, capture_output=True)
        return {"result": "Pending shutdown or restart cancelled."}

    # --- Approved actions ---

    def _execute_power_action(self, action: str) -> None:
        shutdown_exe = Path(os.environ["WINDIR"]) / "System32" / "shutdown.exe"
        mode = "/s" if action == "shutdown" else "/r"
        reason = f"JARVIS approved laptop {action}"
        subprocess.run(
            [str(shutdown_exe), mode, "/t", str(self.POWER_DELAY_SECONDS), "/d", "p:0:0", "/c", reason],
            check=True, timeout=10, capture_output=True,
        )

    def _lock_workstation(self) -> None:
        if not ctypes.windll.user32.LockWorkStation():
            raise OSError("Windows did not start workstation locking.")

    def _delete_to_recycle_bin(self, path: Path) -> None:
        try:
            from send2trash import send2trash
        except ImportError:
            raise RuntimeError("send2trash not installed. Run: pip install send2trash")
        send2trash(str(path))

    # --- Path validation ---

    def _validate_path(self, value: str) -> Path:
        """Validate and resolve a local path."""
        if not isinstance(value, str) or not value:
            raise ValueError("Use one exact absolute local path.")

        path = Path(value).expanduser()
        if not path.is_absolute() or ".." in path.parts or any(c in value for c in ("*", "?")):
            raise ValueError("Use one exact absolute local path, without wildcards or parent traversal.")

        if str(path).startswith("\\\\") or ":" in str(path)[2:]:
            raise ValueError("Network paths and alternate streams are not supported.")

        # Check for symlinks/junctions
        for part in (path, *path.parents):
            if part.exists() and (part.is_symlink() or getattr(part.stat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("Links and junctions are not supported.")

        path = path.resolve()

        # Check allowed roots
        allowed = self.config.allowed_roots
        if not any(path.is_relative_to(root) for root in allowed):
            raise ValueError(
                "Use a path inside Desktop, Documents, Downloads, Pictures, Music, or Videos."
            )

        # Check protected roots
        protected = self.config.protected_roots
        if any(path == root or path.is_relative_to(root) for root in protected):
            raise ValueError("This folder is protected from JARVIS operations.")

        return path

    def _fingerprint(self, path: Path) -> tuple:
        """Generate a fingerprint for a path."""
        s = path.stat()
        return (s.st_dev, s.st_ino, s.st_mtime_ns, s.st_size)


# Import at bottom
import json