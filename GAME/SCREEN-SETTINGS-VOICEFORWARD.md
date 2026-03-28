# Screen: VoiceForward — Mobile Recorder

**Version:** 20260328 V1
**Description:** Mobile-optimized voice recorder page served by the GAME server. No GAME navigation bar rendered — standalone full-viewport page designed for iPhone Safari.

## Route

```
GET /voice
```

Not nested under `/settings/`. Standalone route with no top bar or sub-bar. Intended to be bookmarked on iPhone home screen.

## Layout

Full viewport, single centered column, max-width 480px. Dark theme (matching GAME's `data-bs-theme="dark"`). Large touch targets throughout.

```
┌────────────────────────────────┐
│  VoiceForward              ⚙   │  ← header; ⚙ links to /settings/voiceforward/config
│  ────────────────────────────  │
│                                │
│  ┌──────────────────────────┐  │
│  │       BOOK IDEAS         │  │  ← color: #fdab3d; min height 80px
│  └──────────────────────────┘  │
│                                │
│  ┌──────────────────────────┐  │
│  │        GAME SPEC         │  │  ← color: #0073ea
│  └──────────────────────────┘  │
│                                │
│  ┌──────────────────────────┐  │
│  │          GAME            │  │  ← color: #00c875
│  └──────────────────────────┘  │
│                                │
│  ┌──────────────────────────┐  │  ← result card (hidden until recording completes)
│  │  ✓ Saved to GAME/q...    │  │
│  │  "Check the queue and    │  │
│  │   run daily build"       │  │
│  │  2026-03-28 14:32        │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

## Elements

| Element | Description |
|---------|-------------|
| Header bar | App name "VoiceForward" (small, muted); gear icon (⚙) links to `/settings/voiceforward/config` |
| Buttons | One per active `voice_buttons` row, ORDER BY sort_order; full width, min 80px tall, 8px border-radius, bold uppercase label, 18px font |
| Result card | Hidden on load; shown below buttons after each recording completes |
| Error banner | Red Bootstrap alert; shown on upload or transcription failure; includes Retry button |

## Button State Machine

Each button cycles through states independently. Only one recording may be active at a time — all other buttons are disabled while a recording is in progress.

| State | Visual | Behavior |
|-------|--------|----------|
| **Idle** | Normal button color | Tap → request mic permission if needed; start MediaRecorder; transition to Recording |
| **Recording** | Button pulses (CSS animation on `box-shadow`); label shows `⏺ 0:12`; timer increments | Tap again → stop recording; OR auto-stop at 60 seconds |
| **Uploading** | Button shows spinner; label `Uploading…` | POSTing multipart audio + label to `/api/voice/upload` |
| **Done** | Button flashes green briefly, returns to Idle | Result card updated with text + target file + timestamp |
| **Error** | Red banner appears below buttons | Retry button re-submits the last recorded audio blob |

## Recording

- Uses `MediaRecorder` browser API (webm/ogg format)
- Audio blob held in memory until upload completes; not stored to phone
- On permission denied: show inline message "Microphone access is required"
- On browser not supporting MediaRecorder: show "This browser does not support recording. Use Safari on iOS 14.3+"

## Result Card

| Field | Content |
|-------|---------|
| Status icon | ✓ (green checkmark) |
| Destination | `Saved to {target_file}` (truncated with `…` if long) |
| Transcript | Full transcribed text, wrapping |
| Timestamp | `YYYY-MM-DD HH:MM` |

Card is replaced on each new successful recording.

## Data Flow

| Reads | Writes |
|-------|--------|
| `GET /voice` → renders buttons from `voice_buttons` (server-side, on page load) | `POST /api/voice/upload` → appends to target file on server |

Buttons are rendered server-side at page load. No dynamic HTMX reloading of buttons during a session.

## Open Questions

- Should the page auto-refresh the button list periodically in case buttons are reconfigured from the desktop? Not in V1 — a manual page refresh is sufficient.
- Should completed recordings be visually logged in a scrollable history section below the result card? Could be useful; defer to V2.
