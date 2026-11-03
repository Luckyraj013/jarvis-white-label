# JARVIS — Running Guide

Complete installation and usage guide for JARVIS Personal AI Assistant (White-Label Edition).

---

## 📋 Quick Start (TL;DR)

```bash
# 1. Clone
git clone https://github.com/Luckyraj013/jarvis-white-label.git
cd jarvis-white-label

# 2. Install dependencies
python -m pip install -r requirements.txt
python -m playwright install chromium

# 3. Configure (interactive wizard)
python setup.py
# → Enter your Gemini API key
# → Set your name, language, response style
# → Creates "Start JARVIS" on Desktop

# 4. Run
# Option A: Double-click "Start JARVIS" on Desktop
# Option B: python -m jarvis
```

---

## 🖥️ System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 1909+ | Windows 11 |
| **Python** | 3.12+ | 3.12/3.13 |
| **RAM** | 4 GB | 8 GB+ |
| **Storage** | 2 GB free | 4 GB+ free |
| **Microphone** | Required | Good quality USB mic |
| **Speakers** | Required | Headset (reduces echo) |
| **Internet** | Required (Gemini API) | Stable broadband |

---

## 🔧 Detailed Installation

### Step 1: Install Python

1. Download from **[python.org/downloads](https://python.org/downloads)** (Windows 64-bit installer)
2. **Run installer** — **✅ CHECK "Add Python to PATH"** (bottom of first screen)
3. Click **Install Now**
4. Verify: Open new terminal → `python --version` → shows 3.12.x or 3.13.x

> **If `python` not found but `py` works:** Use `py` instead of `python` in all commands below.

### Step 2: Clone Repository

```bash
git clone https://github.com/Luckyraj013/jarvis-white-label.git
cd jarvis-white-label
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
python -m pip install -r requirements.txt
```

Expected output: `Successfully installed ...` (50+ packages)

### Step 4: Install Playwright Browser

```bash
python -m playwright install chromium
```

Downloads ~200 MB Chromium. Wait for completion.

### Step 5: Run Setup Wizard

```bash
python setup.py
```

**Wizard prompts:**

| Prompt | Example | Notes |
|--------|---------|-------|
| Gemini API Key | `AIzaSy...` | Hidden input. Get from [AI Studio](https://aistudio.google.com/apikey) |
| Your name | `Alex` | Optional. JARVIS will address you by name |
| Language | `en-IN` | Default: Indian English. Use `en-US`, `hi-IN`, etc. |
| Response style | `balanced` | Options: `brief`, `balanced`, `detailed` |
| Model | `gemini-3.1-flash-live-preview` | Press Enter for default |
| Voice | `Charon` | Options: `Charon`, `Puck`, `Kore`, `Fenrir`, `Aoede` |
| Desktop shortcut? | `Y` | Creates "Start JARVIS" on Desktop |

### Step 6: Start JARVIS

**Option A: Desktop Shortcut (Recommended)**
- Double-click **"Start JARVIS"** on Desktop
- Opens terminal, starts listening

**Option B: Command Line**
```bash
python -m jarvis
```

**Option C: Development Mode** (auto-reload, local LiveKit)
```bash
python -m jarvis dev
```

---

## 🎙️ Using JARVIS

### First Run
1. Terminal opens → "JARVIS is ready"
2. **Speak naturally:** *"Jarvis, what time is it?"*
3. JARVIS responds via speakers

### Voice Commands

| Category | Examples |
|----------|----------|
| **General** | *"Good morning"*, *"What's the weather?"*, *"Search for Python tutorials"* |
| **Browser** | *"Open YouTube"*, *"Search YouTube for jazz"*, *"Play the first video"*, *"Open Google Maps"* |
| **Files** | *"List my Documents folder"*, *"Create folder Projects"*, *"Open file report.pdf"* |
| **System** | *"Set volume to 50 percent"*, *"Mute the computer"*, *"Open display settings"*, *"Shutdown in 30 seconds"* |
| **Preferences** | *"Remember my name is Alex"*, *"I prefer brief responses"*, *"What do you know about me?"* |
| **Camera/Screen** | *"Show me the camera"*, *"What's on my screen?"*, *"Stop sharing"* |

### Approval System
Destructive actions require **verbal approval**:
```
You: "Delete file old_report.pdf"
JARVIS: "Requesting approval. Code: 123456. Say 'approve 123456' to confirm."
You: "Approve 123456"
JARVIS: "File deleted."
```

| Action | Requires Approval |
|--------|-------------------|
| Delete file/folder | ✅ Yes |
| Rename/Move | ✅ Yes |
| Shutdown/Restart | ✅ Yes |
| Lock PC | ✅ Yes |
| Open app (Notepad, Calculator) | ❌ No |
| List/Open/Create folder | ❌ No |
| Volume/Brightness | ❌ No |

### Text Input (Alternative to Voice)
- Type in terminal when JARVIS is listening
- Use **Correction**: *"Correction to my last spoken command: play the second video"*

---

## ⚙️ Configuration

### Config File Locations
```
%USERPROFILE%\.jarvis\
├── config.json          # App settings (model, voice, folders)
├── secrets.bin          # Encrypted API keys (DPAPI)
├── preferences.json     # User preferences (name, language, style)
└── approvals.json       # Pending approval requests
```

### Change Settings Later
```bash
# Re-run setup wizard
python setup.py

# Or edit config directly
python -c "
from jarvis.config import Config
c = Config()
c.set('response_style', 'brief')
c.set('model', 'gemini-3.5-flash-live-preview')
c.save()
print('Updated')
"
```

### Available Settings (config.json)
```json
{
  "model": "gemini-3.1-flash-live-preview",
  "voice": "Charon",
  "language": "en-IN",
  "response_style": "balanced",
  "user_name": "Alex",
  "allowed_folders": ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"],
  "protected_folders": ["Codex", ".jarvis"],
  "approval_timeout_seconds": 120,
  "browser_headless": false,
  "browser_timeout_seconds": 30,
  "search_max_results": 10,
  "silence_duration_ms": 750
}
```

---

## 🔄 Updating JARVIS

```bash
cd jarvis-white-label
git pull origin main
python -m pip install -r requirements.txt
python -m playwright install chromium
# Re-run setup if new options added
python setup.py
```

---

## 🗂️ File Structure

```
jarvis-white-label/
├── setup.py              # Run once for configuration
├── create_shortcut.py    # Recreate desktop shortcut
├── requirements.txt      # Dependencies
├── RUNNING_GUIDE.md      # This file
├── TROUBLESHOOTING.md    # Common issues & fixes
├── jarvis/
│   ├── __main__.py       # Entry point (python -m jarvis)
│   ├── agent.py          # Voice agent + tools
│   ├── config.py         # Secure configuration
│   ├── browser.py        # Playwright browser
│   ├── operations.py     # File/system operations
│   ├── preferences.py    # User preferences
│   ├── search.py         # Web search
│   └── system_settings.py # Volume/brightness/settings
└── .jarvis/              # Created after setup (gitignored)
    ├── config.json
    ├── secrets.bin
    ├── preferences.json
    └── approvals.json
```

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Luckyraj013/jarvis-white-label/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Luckyraj013/jarvis-white-label/discussions)
- **API Key:** [Google AI Studio](https://aistudio.google.com/apikey)

---

**Enjoy your personal AI assistant!** 🤖