# JARVIS — Troubleshooting Guide

Common issues and solutions for JARVIS White-Label Edition.

---

## 🚨 Quick Diagnosis

| Symptom | Likely Cause | Jump To |
|---------|--------------|---------|
| `'python' not recognized` | Python not in PATH | [Python PATH](#python-not-in-path) |
| `No module named pip` | pip not installed | [Missing pip](#missing-pip) |
| `Gemini API key invalid` | Key format / validation | [API Key Issues](#api-key-issues) |
| `Access denied` | Permissions | [Permission Errors](#permission-errors) |
| Shortcut doesn't start | Wrong Python path in shortcut | [Shortcut Issues](#shortcut-issues) |
| Microphone not working | Privacy settings | [Audio Issues](#audio-issues) |
| `playwright` not found | Browser not installed | [Playwright Issues](#playwright-issues) |
| `ModuleNotFoundError` | Missing dependencies | [Missing Dependencies](#missing-dependencies) |

---

## 🔧 Installation Issues

### Python Not in PATH

**Error:** `'python' is not recognized as an internal or external command`

**Fix 1: Use `py` launcher (works always)**
```cmd
py --version
py -m pip install -r requirements.txt
py -m playwright install chromium
py setup.py
py -m jarvis
```

**Fix 2: Disable Windows Store aliases**
1. Settings → Apps → **App execution aliases**
2. Turn **OFF**: `python.exe` and `python3.exe`
3. Restart terminal

**Fix 3: Reinstall with PATH**
1. Uninstall Python (Settings → Apps)
2. Download from [python.org](https://python.org/downloads)
3. **✅ CHECK "Add Python to PATH"** during install
4. Restart terminal

---

### Missing pip

**Error:** `No module named pip` or `py -m pip` fails

```cmd
# Install pip
py -m ensurepip --upgrade

# Verify
py -m pip --version
```

**If that fails:**
```cmd
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
py get-pip.py
```

---

### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'xxx'`

```cmd
# Reinstall all dependencies
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

# If specific module missing
py -m pip install <module_name>
```

**Common missing modules:**
| Module | Install Command |
|--------|-----------------|
| `livekit.agents` | `py -m pip install livekit-agents[google]` |
| `playwright` | `py -m pip install playwright` |
| `pycaw` | `py -m pip install pycaw` |
| `wmi` | `py -m pip install wmi` |
| `send2trash` | `py -m pip install send2trash` |

---

## 🔑 API Key Issues

### "Invalid API Key" During Setup

**Cause:** Validation checks for `AIza` prefix + 20+ chars. Some keys differ.

**Fix: Set key directly (bypasses validation)**
```cmd
cd jarvis-white-label
py -c "
from jarvis.config import Config
c = Config()
c.gemini_api_key = 'YOUR_ACTUAL_KEY_HERE'
c.save()
print('Saved:', c.gemini_api_key[:15] + '...')
"
```

### "Gemini API key is missing" When Starting

**Cause:** Key not saved or corrupted.

**Fix:**
```cmd
# Check if key exists
py -c "from jarvis.config import Config; c=Config(); print('Key:', 'SET' if c.gemini_api_key else 'MISSING')"

# Re-set if missing
py -c "from jarvis.config import Config; c=Config(); c.gemini_api_key='YOUR_KEY'; c.save()"
```

### API Quota Exceeded / 429 Errors

**Cause:** Free tier limits reached.

**Fixes:**
- Wait for quota reset (usually daily)
- Upgrade at [AI Studio Billing](https://aistudio.google.com/apikey)
- Use lighter model: `gemini-3.1-flash-live-preview` (default)

---

## 🖱️ Shortcut Issues

### Shortcut Doesn't Start / Flashes and Closes

**Cause:** Shortcut uses `python` but it's not in PATH.

**Fix 1: Recreate shortcut with full path**
```cmd
cd jarvis-white-label
py create_shortcut.py
```

**Fix 2: Manually fix shortcut**
1. Right-click "Start JARVIS" → **Properties**
2. **Target:** Full Python path + `-m jarvis`
   ```
   C:\Users\<USER>\AppData\Local\Programs\Python\Python315\python.exe -m jarvis
   ```
   (Find yours: `where python` or `py -c "import sys; print(sys.executable)"`)
3. **Start in:** Project folder
   ```
   C:\Users\<USER>\Documents\jarvis-white-label
   ```

**Fix 3: Run directly instead**
```cmd
cd C:\Users\<USER>\Documents\jarvis-white-label
py -m jarvis
```

### Shortcut Creates Multiple Windows

**Cause:** Double-clicking repeatedly.

**Fix:** Single-click only. If multiple open, close all and restart.

---

## 🎤 Audio Issues

### Microphone Not Detected / No Input

**Fix 1: Windows Privacy Settings**
1. Settings → **Privacy & security** → **Microphone**
2. **ON**: "Microphone access"
3. **ON**: "Let apps access your microphone"
4. **ON**: "Let desktop apps access your microphone"

**Fix 2: Check Default Device**
1. Right-click speaker icon → **Sound settings**
2. **Input** → Select your microphone
3. Test: "Start test" → speak → see bar move

**Fix 3: Exclusive Mode Off**
1. Sound settings → **More sound settings** (Control Panel)
2. **Recording** tab → Right-click mic → **Properties**
3. **Advanced** → **UNCHECK** "Allow applications to take exclusive control"

---

### No Sound / JARVIS Not Speaking

**Fix 1: Check Output Device**
1. Sound settings → **Output** → Select speakers/headphones
2. Volume mixer → Ensure "System Sounds" and Python not muted

**Fix 2: Check JARVIS Mute State**
- Say: *"Unmute"* or *"Resume"*
- Or check terminal for "speaker_mute" messages

---

### Echo / Feedback Loop

**Cause:** Speakers too loud, mic picks up JARVIS voice.

**Fixes:**
- Use **headset/headphones** (best fix)
- Lower speaker volume
- Move mic away from speakers
- Say *"Mute"* to stop JARVIS speaking, then *"Resume"*

---

## 🌐 Playwright Issues

### "playwright: command not found" / Browser Not Installed

```cmd
# Install Playwright browsers
py -m playwright install chromium

# If fails, install with deps
py -m playwright install --with-deps chromium
```

### Browser Crashes / "Target page, context or browser has been closed"

**Cause:** Browser process killed or crashed.

**Fixes:**
- Restart JARVIS
- Check antivirus not blocking Playwright
- Try headless mode: Edit `config.json` → `"browser_headless": true`

---

### "Executable doesn't exist" for Chromium

```cmd
# Force reinstall
py -m playwright uninstall chromium
py -m playwright install chromium
```

---

## 🔒 Permission Errors

### "Access is denied" / "PermissionError"

**Fix 1: Run as Administrator**
1. Search "cmd" → Right-click → **Run as administrator**
2. Navigate to project: `cd C:\Users\<USER>\Documents\jarvis-white-label`
3. Run commands

**Fix 2: Check Folder Permissions**
```cmd
# Take ownership of project folder
icacls "C:\Users\<USER>\Documents\jarvis-white-label" /grant %USERNAME%:F /T
```

**Fix 3: Antivirus Blocking**
- Add project folder to antivirus exclusions
- Windows Defender → Virus protection → Manage settings → Exclusions

---

### "File in use" / "Cannot delete shortcut"

**Fix:** Close all JARVIS terminals, then retry.

```cmd
# Force kill any Python processes
taskkill /f /im python.exe
```

---

## 📁 File Operation Issues

### "Folder is protected from JARVIS operations"

**Cause:** Path outside allowed folders or in protected list.

**Allowed by default:**
- Desktop
- Documents
- Downloads
- Pictures
- Music
- Videos

**Fix: Use allowed path**
```cmd
# Correct
C:\Users\<USER>\Documents\MyFolder

# Incorrect (protected)
C:\Users\<USER>\Documents\Codex\...
C:\Users\<USER>\.jarvis\...
C:\Program Files\...
```

**Fix: Add custom allowed folder**
```cmd
py -c "
from jarvis.config import Config
c = Config()
folders = c.get('allowed_folders', [])
folders.append('MyCustomFolder')
c.set('allowed_folders', folders)
c.save()
print('Added:', folders)
"
```

---

### "Destination must not exist" on Rename/Move

**Cause:** Target file/folder already exists.

**Fix:** Use different name or delete target first.

---

### "Source changed after approval" Error

**Cause:** File modified between approval request and execution.

**Fix:** Re-request the operation.

---

## 🪟 Windows Settings Issues

### Volume/Brightness Not Working

**Error:** "Could not get volume: ..." or "No supported internal display"

**Volume Fix:**
```cmd
# Check audio endpoint
py -c "
from pycaw.pycaw import AudioUtilities
devices = AudioUtilities.GetSpeakers()
print('Device:', devices.FriendlyName)
vol = devices.EndpointVolume
print('Level:', vol.GetMasterVolumeLevelScalar() * 100)
print('Muted:', vol.GetMute())
"
```

**Brightness Fix:**
- Only works on **laptop internal displays**
- External monitors: Use monitor buttons
- Desktop PCs: Usually not supported via WMI

---

### "ms-settings: URI failed" Opening Settings

**Cause:** Windows version doesn't support that page.

**Fix:** Use supported pages only (see `system_settings.py` SETTINGS_PAGES).

---

## 🐛 Runtime Errors

### "LiveKit connection failed" / WebSocket Errors

**Cause:** Network/firewall blocking LiveKit local server.

**Fixes:**
- Allow Python through Windows Firewall
- Run `py -m jarvis dev` (starts local LiveKit server)
- Check no VPN/proxy interfering with localhost

---

### "Gemini connection had an error. Retrying..."

**Cause:** Temporary network/API issue.

**Fix:** Wait — JARVIS auto-retries. If persistent:
- Check internet connection
- Verify API key valid at [AI Studio](https://aistudio.google.com/apikey)
- Check quota not exceeded

---

### "Browser action could not be verified"

**Cause:** Page load timeout, permission prompt, or navigation blocked.

**Fixes:**
- Increase timeout: `config.json` → `"browser_timeout_seconds": 60`
- Handle prompts manually in JARVIS browser window
- Try simpler action first (e.g., `open` before `click_link`)

---

### "Local operation connection failed"

**Cause:** Windows node not running (only for multi-device setup).

**Fix:** This is standalone version — local operations run in-process. Restart JARVIS.

---

## 🔄 Reset / Clean Start

### Complete Reset (Remove All User Data)

```cmd
# WARNING: Deletes API key, preferences, approvals
rmdir /s /q "%USERPROFILE%\.jarvis"

# Then re-run setup
cd jarvis-white-label
py setup.py
```

### Reset Only Preferences

```cmd
py -c "
from jarvis.config import Config
from jarvis.preferences import Preferences
c = Config()
p = Preferences(c)
p.clear()
print('Preferences cleared')
"
```

### Reinstall Everything

```cmd
# 1. Remove project
cd ..
rmdir /s /q jarvis-white-label

# 2. Re-clone
git clone https://github.com/Luckyraj013/jarvis-white-label.git
cd jarvis-white-label

# 3. Reinstall deps
py -m pip install -r requirements.txt
py -m playwright install chromium

# 4. Setup
py setup.py
```

---

## 📞 Still Stuck?

### Collect Debug Info

```cmd
# System info
py -c "import sys, platform; print(f'Python: {sys.version}'); print(f'OS: {platform.platform()}')"

# JARVIS config
py -c "from jarvis.config import Config; c=Config(); print(f'Config: {c.config_path}'); print(f'Data: {c.data_dir}'); print(f'Key: {\"SET\" if c.gemini_api_key else \"MISSING\"}')"

# Dependencies
py -m pip list | findstr -i "livekit playwright pycaw wmi send2trash"
```

### Open GitHub Issue

Include:
1. **Error message** (full text)
2. **Steps to reproduce**
3. **Debug info** from above
4. **Windows version** (`winver`)
5. **Python version** (`python --version`)

[**Create Issue →**](https://github.com/Luckyraj013/jarvis-white-label/issues/new)

---

## 📋 Common Commands Reference

| Task | Command |
|------|---------|
| Install deps | `py -m pip install -r requirements.txt` |
| Install browser | `py -m playwright install chromium` |
| Run setup | `py setup.py` |
| Start JARVIS | `py -m jarvis` |
| Dev mode | `py -m jarvis dev` |
| Set API key | `py -c "from jarvis.config import Config; c=Config(); c.gemini_api_key='KEY'; c.save()"` |
| Recreate shortcut | `py create_shortcut.py` |
| Reset user data | `rmdir /s /q "%USERPROFILE%\.jarvis"` |
| View config | `py -c "from jarvis.config import Config; import json; c=Config(); print(json.dumps(c._config, indent=2))"` |
| Update | `git pull && py -m pip install -r requirements.txt` |

---

**Most issues are fixed by:** Re-running `setup.py`, recreating shortcut, or checking Windows microphone permissions. 🎯