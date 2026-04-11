# Screen: VoiceForward — Setup Documentation

**Version:** 20260328 V1
**Description:** Static documentation page explaining how to install dependencies, configure WSL2 network access, and connect an iPhone to the VoiceForward recorder.

## Menu Navigation

Main Menu: Settings [right]
Sub Menu: Voice Docs

## Route

```
GET /settings/voiceforward/docs
```

Settings sub-bar is active. Voice Docs tab is selected.

## Layout

Single-column, max-width 800px. Five `cc-card` sections in sequence. No dynamic data — content is static HTML rendered server-side.

```
┌──────────────────────────────────────────────────────────────┐
│  VoiceForward Setup                                          │
│  ──────────────────────────────────────────────────────────  │
│  ┌─ 1. Prerequisites ─────────────────────────────────────┐  │
│  │  Install ffmpeg and openai-whisper...           [Copy] │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌─ 2. WSL2 Network Setup ────────────────────────────────┐  │
│  │  netsh portproxy command...                     [Copy] │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌─ 3. Finding Your Laptop IP ────────────────────────────┐  │
│  │  ipconfig instructions...                              │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌─ 4. Connecting from iPhone ────────────────────────────┐  │
│  │  http://[IP]:5001/voice walkthrough...                 │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌─ 5. Managing Buttons ──────────────────────────────────┐  │
│  │  Relative path format + link to config screen          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Sections

### 1. Prerequisites

**Install ffmpeg** (WSL2 / Ubuntu):
```bash
sudo apt update && sudo apt install -y ffmpeg
```

**Install Whisper** (in the GAME virtualenv):
```bash
pip install openai-whisper
```

Note: `openai-whisper` pulls PyTorch and several other dependencies — expect ~1 GB install size. The Whisper `base` model (~140 MB) downloads automatically on the first transcription request and is cached locally.

---

### 2. WSL2 Network Setup

The GAME server runs inside WSL2. To reach it from a phone on the same WiFi, Windows must forward the port from its network interface to WSL2.

**Run these commands in Windows PowerShell (as Administrator):**

Add port proxy (run once; survives reboots):
```powershell
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=127.0.0.1
```

Allow port 5001 through Windows Firewall:
```powershell
netsh advfirewall firewall add rule name="GAME VoiceForward" dir=in action=allow protocol=TCP localport=5001
```

To verify the proxy is active:
```powershell
netsh interface portproxy show v4tov4
```

To remove it later:
```powershell
netsh interface portproxy delete v4tov4 listenport=5001 listenaddress=0.0.0.0
```

---

### 3. Finding Your Laptop IP

1. Open **Command Prompt** on Windows (`Win + R` → `cmd` → Enter)
2. Run: `ipconfig`
3. Find the **Wi-Fi** adapter section
4. Note the **IPv4 Address** — looks like `192.168.x.x` or `10.x.x.x`

This is the address your phone will use. The IP may change if your router reassigns it — if the connection stops working, re-run `ipconfig` to check.

---

### 4. Connecting from iPhone

1. Make sure your iPhone and laptop are on the **same WiFi network**
2. Open **Safari** on iPhone
3. Navigate to: `http://[YOUR-LAPTOP-IP]:5001/voice`
   - Example: `http://192.168.1.42:5001/voice`
4. On first use, Safari will prompt: **"[site] would like to access the microphone"** — tap **Allow**
5. The recorder page appears with your configured buttons

**Add to Home Screen (optional):**
- Tap the Share button (box with arrow) → **Add to Home Screen**
- This creates a bookmark icon that opens the recorder directly

---

### 5. Managing Buttons

Buttons are configured in GAME settings — not in code. Each button needs:

| Field | Description | Example |
|-------|-------------|---------|
| Button Text | Label shown on the button | `BOOK IDEAS` |
| File to Append To | Path relative to `$PROJECTS_DIR` | `TheTruth/ideas.md` |
| Color | Hex background color | `#fdab3d` |

`$PROJECTS_DIR` is set in your GAME `.env` file. A target of `TheTruth/ideas.md` resolves to `{PROJECTS_DIR}/TheTruth/ideas.md`. The file and any missing parent directories are created automatically on first use.

→ [Manage Buttons](/settings/voiceforward/config)

## Elements

| Element | Description |
|---------|-------------|
| Section cards | Five `cc-card` blocks; each has a `cc-card-header` with section number and title |
| Code blocks | `<pre class="bg-light border rounded p-3">` with monospace text |
| Copy buttons | `[Copy]` button in top-right of each code block; JS copies `innerText` to clipboard; label flashes "Copied!" for 1.5s |
| Internal link | Section 5 button links to `/settings/voiceforward/config` using standard Bootstrap outline button |

## Data Flow

No reads or writes. Static content rendered once server-side. Template contains the full documentation text; no DB queries.

## Open Questions

- Should the docs page detect whether Whisper is installed and show a status indicator (installed / not installed)? Could be useful; adds a server-side check on page load.
- Should the WSL2 portproxy section auto-populate the correct port from `$GAME_PORT`/`.env` instead of hard-coding 5001?
