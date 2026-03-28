# Feature: VoiceForward

**Version:** 20260328 V1
**Description:** Mobile voice recorder — records audio on the phone, transcribes with local Whisper, and appends text to a configured project file.

VoiceForward adds a mobile-accessible recorder page to the GAME server. The user opens `/voice` in iPhone Safari, taps a labeled button, records a voice note, and the GAME server transcribes it locally with Whisper and appends the text to the appropriate project file. Buttons are configured via a settings screen — not hard-coded.

---

## Capabilities

1. **Button Config Store** — CRUD for voice buttons stored in `voice_buttons` table. Each button has a label, a target file path (relative to `$PROJECTS_DIR`), a color, and a sort order.
2. **Audio Upload + Transcription** — `POST /api/voice/upload` receives a webm/ogg audio blob and a label from the phone browser. Saves to a temp file, transcribes with Whisper `base` model, looks up the target path from the DB by label, appends the transcribed text to the file.
3. **File Appender** — Resolves `$PROJECTS_DIR/{target_file}`, creates the file and any missing parent directories if they do not exist, and appends a dated entry.

---

## Triggers

| Trigger | Description |
|---------|-------------|
| `POST /api/voice/upload` | Phone browser sends audio blob + label after recording stops |
| `GET /voice` | Phone browser loads the mobile recorder page |

---

## Upload Logic

```
POST /api/voice/upload
  body: multipart — audio (webm/ogg blob), label (string)

1. Validate: label exists in voice_buttons (active=1); return 400 if not found
2. Save audio blob to temp file (e.g. /tmp/vf_{uuid}.webm)
3. model = whisper.load_model("base")   # lazy-loaded; cached after first call
4. result = model.transcribe(temp_file)
5. text = result["text"].strip()
6. Delete temp file
7. Call append_to_file(target_file, label, text)
8. Return JSON: {status: "ok", text: text, target_file: target_file}

On error: return JSON {status: "error", message: ...} with appropriate HTTP status
```

---

## File Append Format

Each entry appended to the target file:

```
---
**YYYY-MM-DD HH:MM** [LABEL]
{transcribed text}
```

---

## New Table: `voice_buttons`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PK, autoincrement | |
| label | TEXT | NOT NULL, UNIQUE | Display text, e.g. "BOOK IDEAS" |
| target_file | TEXT | NOT NULL | Relative to `$PROJECTS_DIR`, e.g. `TheTruth/ideas.md` |
| color | TEXT | NOT NULL | Hex color for button background |
| sort_order | INTEGER | NOT NULL | Display order (ascending) |
| active | BOOLEAN | NOT NULL, DEFAULT 1 | Hidden from recorder if 0 |

---

## Seed Data

Inserted at migration time:

| label | target_file | color | sort_order |
|-------|-------------|-------|-----------|
| BOOK IDEAS | TheTruth/ideas.md | #fdab3d | 1 |
| GAME SPEC | Specifications/GAME/ideas.md | #0073ea | 2 |
| GAME | GAME/queue.md | #00c875 | 3 |

---

## New Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/voice` | Mobile recorder page (no GAME nav) |
| POST | `/api/voice/upload` | Receive audio + label; transcribe; append |
| GET | `/settings/voiceforward` | Redirect → `/settings/voiceforward/config` |
| GET | `/settings/voiceforward/config` | Button management screen |
| GET | `/settings/voiceforward/docs` | Setup documentation page |
| POST | `/api/voice/buttons` | Create a new button |
| PUT | `/api/voice/buttons/{id}` | Update button fields |
| DELETE | `/api/voice/buttons/{id}` | Delete button |
| PUT | `/api/voice/buttons/{id}/reorder` | Update sort_order |

---

## New Module: `voiceforward.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_buttons` | `() → list[dict]` | Query `voice_buttons` WHERE active=1 ORDER BY sort_order |
| `get_button_by_label` | `(label: str) → dict \| None` | Lookup button by label (case-sensitive) |
| `transcribe` | `(audio_path: str) → str` | Load Whisper base model (lazy, cached); return transcribed text |
| `append_to_file` | `(target_file: str, label: str, text: str)` | Resolve full path via `$PROJECTS_DIR`; create dirs/file if needed; append dated entry |
| `route` | `(label: str, audio_path: str) → dict` | Orchestrates: lookup → transcribe → append → return result dict |

---

## Dependencies

Add to `requirements.txt`:
```
openai-whisper
```

System requirement (install separately):
```
ffmpeg
```

Whisper `base` model (~140 MB) downloads on first transcription call. Subsequent calls use the cached model in memory for the server process lifetime.

---

## Open Questions

- Should the Whisper model size be configurable via `.env` (`WHISPER_MODEL=base`)? Currently hard-coded to `base`; `small` or `medium` would improve accuracy for unusual vocabulary at higher CPU cost.
- Should audio files be retained (e.g. in `data/voice_recordings/`) for later re-transcription, or always deleted after processing? Currently deleted after processing.
- Should `$PROJECTS_DIR` be the only supported root, or should buttons support an absolute path override for targets outside the projects directory?
