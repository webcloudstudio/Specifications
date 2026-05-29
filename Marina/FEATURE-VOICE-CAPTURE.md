# Feature: Voice Capture

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Capture a voice note from inside the firewall to S3 and enqueue a transcription job; the local agent transcribes with Whisper and appends the text. No audio leaves to a public surface. |
| Depends On  | FEATURE-ASYNCQUEUE.md, FEATURE-S3-SHARE.md |
| Provides    | — |

**Description:** The durable, screen-less successor to GAME's VoiceForward. Audio is captured **inside
the firewall**, stored in S3, and a transcription job is enqueued. The local Marina agent drains the
job and runs Whisper locally (no GPU/cloud transcription cost), then appends the text to the configured
project file. If the local agent is off, nothing is lost — the job waits in the queue.

## Trigger

A capture client **inside the firewall** (a local recorder page or a small relay on the LAN) records
audio and, on stop, uploads it and enqueues a job. There is no public inbound endpoint — the capture
client runs on the local network and uses the member's AWS identity (SigV4).

## Sequence

1. **Capture (inside firewall):** the recorder produces an audio blob and a `label`.
2. **Store:** the client uploads the blob to S3 via `mar.share.put(audio, key="voice/{member}/{uuid}.webm")`
   (reuses the S3 share's bucket + prefix model, direct SigV4 upload).
3. **Enqueue:** the client calls `mar.queue.submit(queue="voice", service="voiceforward",
   tool="transcribe", payload={audio_key, label})`. Submission succeeds 24×7 regardless of the local
   agent's state.
4. **Drain (local agent):** on its next drain, the agent pulls the job, downloads the audio from S3
   (`mar.share.get`), runs **local** Whisper (`base` model, lazy-loaded), and appends a dated entry to the
   label's target file under `$PROJECTS_DIR`. On success the message is deleted; on failure it retries via
   SQS, then DLQs.

## Reads

- SQS `voice` queue (drain); S3 audio object; local Whisper model; the label→target-file mapping.

## Writes

- S3 audio object (capture); SQS message (enqueue); the appended text in the target project file (local,
  on drain). No transcription happens in the cloud.

## Test

- **Script:** `bin/test_voice_capture.sh` → uploads a short sample audio to S3, enqueues a `transcribe`
  job, runs a local drain with a stubbed/real Whisper, and asserts the transcribed text is appended to a
  temp target file and the message is deleted; asserts a failed transcription retries then DLQs.
- **Pass criteria:** audio stored in S3 under the member prefix; job processed end-to-end locally;
  nothing lost if the drain is delayed; no cloud transcription invoked.
- **CloudWatch:** the `voice` SQS metrics show enqueue/drain; the queue-drain Lambda/agent log records
  `{"event":"voice_transcribed","audio_key":...,"chars":N}`.

## Open Questions

- Audio retention in S3: delete after successful transcription, or keep for re-transcription with a
  lifecycle expiry (e.g. 7 days)? Leaning keep-7-days via lifecycle, then auto-delete.
- Whisper model size: `base` default; make it a local agent setting (`WHISPER_MODEL`) without affecting
  the cloud contract.
- Capture client form factor (local recorder page vs. LAN relay) is a local-plane concern, specified when
  the local agent is built; this feature only fixes the S3+SQS contract.
