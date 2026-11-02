# JARVIS — Personal AI Assistant (White-Label Edition)

A standalone, privacy-first personal AI assistant for Windows. Runs entirely on your PC — no cloud dependencies for core features, no external servers required.

## Features

- 🎙️ **Voice Conversation** — Natural voice chat with Gemini Live API
- 🌐 **Web Search** — Real-time search via DuckDuckGo
- 🖥️ **Browser Control** — Dedicated browser with navigation, YouTube, Maps, media controls
- 📁 **File Operations** — List, open, create, rename, move, delete files (with approval)
- ⚙️ **System Control** — Volume, brightness, shutdown/restart, Windows Settings
- 📷 **Camera & Screen** — Camera access, screen capture/share
- 💾 **Preferences** — Remembers your name, language, response style
- 🔒 **Privacy-First** — All data stays local; API keys stored securely

## Quick Start

### Prerequisites
- Windows 10/11
- Python 3.12+
- Microphone & speakers
- Google Gemini API key (free from [AI Studio](https://aistudio.google.com/apikey))

### Installation

```powershell
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/jarvis-white-label.git
cd jarvis-white-label

# 2. Run the setup wizard (interactive)
python setup.py

# 3. Start JARVIS
python -m jarvis
```

The setup wizard will:
1. Prompt for your Gemini API key (hidden input)
2. Ask for your name, preferred language, response style
3. Create a desktop shortcut "Start JARVIS"
4. Configure all paths automatically

### Usage

After setup, you can start JARVIS in two ways:
- **Double-click** "Start JARVIS" on your desktop
- **Run** `python -m jarvis` from the project folder

Then simply speak: *"Jarvis, what's the weather?"* or *"Open YouTube and search for jazz music"*

## Architecture

```
jarvis-white-label/
├── jarvis/                 # Main package
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── agent.py           # Voice agent with all tools
│   ├── browser.py         # Playwright browser control
│   ├── operations.py      # Local file/system operations
│   ├── preferences.py     # User preferences
│   ├── search.py          # Web search (DuckDuckGo)
│   └── system_settings.py # Volume/brightness/settings
├── setup.py               # Interactive setup wizard
├── create_shortcut.py     # Desktop shortcut creator
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Capabilities

### Voice Commands
| Category | Examples |
|----------|----------|
| **Search** | "Search for Python tutorials", "What's the latest AI news?" |
| **Browser** | "Open YouTube", "Play the first video", "Search Google Maps for coffee shops" |
| **Files** | "List my Documents folder", "Create a folder called Projects", "Delete that file" |
| **System** | "Set volume to 50%", "Mute the computer", "Open display settings", "Shutdown in 30 seconds" |
| **Preferences** | "Remember my name is Alex", "I prefer brief responses", "What do you know about me?" |
| **Media** | "Show me the camera", "What's on my screen?", "Stop sharing" |

### Approval System
Destructive operations (delete, rename, move, shutdown, restart, lock) require explicit approval with a 6-digit code. Say *"approve 123456"* or use the approval UI.

## Configuration

All settings stored in `~/.jarvis/`:
- `config.json` — API keys, paths, model settings
- `preferences.json` — Your name, language, response style
- `approvals.json` — Pending approval requests

## Security

- API keys stored in Windows Credential Manager (DPAPI)
- No telemetry, no data collection
- All processing local except Gemini API calls
- File operations restricted to personal folders
- Approval required for destructive actions

## Customization

Edit `jarvis/config.py` to change:
- Model (`gemini-3.1-flash-live-preview`, etc.)
- Voice (`Charon`, `Puck`, `Kore`, etc.)
- Supported file operations
- Approval timeout

## License

MIT License — see [LICENSE](LICENSE)

## Contributing

1. Fork the repo
2. Create a feature branch
3. Submit a PR

---

**Built for privacy. Runs on your hardware. Your rules.**