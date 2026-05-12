# SCREEN: Docker Management

| Field | Value |
|-------|-------|
| Version | 20260512 V1 |
| Description | Per-project Docker configuration, build, and lifecycle management screen. |
| Route | `GET /projects/{name}/docker` |
| Parent | Projects |
| Main Menu | — |
| Tab Order | 5 (after Maintenance) |
| Depends On | ARCHITECTURE-DOCKER.md, UI-GENERAL.md, FEATURE-SERVICE-CATALOG.md |

Accessible from the project detail screen via a "Docker" tab. The tab appears for all projects; when Docker is disabled the tab shows only the enable toggle (collapsed state).

---

## Layout

Three-panel layout: **Configuration** (left column), **Status + Controls** (right column top), **Logs** (right column bottom).

---

## Configuration Panel

**Docker Toggle**
- Label: "Docker Enabled"
- Control: Bootstrap toggle switch
- Value read from / written to METADATA.md `docker_enabled`
- On enable: triggers `conform_dockerize` in background (shows spinner); generates Dockerfile
- On disable: hides all other controls; does not delete existing Dockerfile (user must manually remove)

**Host Port**
- Label: "Published Port (host)"
- Control: number input, default = project port from METADATA.md
- Maps to METADATA.md `docker_host_port`
- Hint text: "Container port {port} will be published on host port {docker_host_port}"
- Validation: must be 1–65535, warns if port already in use by another docker-enabled project

**Base Image**
- Label: "Base Image"
- Control: text input with auto-selected default shown as placeholder
- Placeholder derived from stack (e.g. `python:3.12-slim`)
- Maps to METADATA.md `docker_base_image`

**Extra System Packages**
- Label: "Extra apt Packages"
- Control: text input (space-separated)
- Maps to METADATA.md `docker_extra_packages`
- Example: `ffmpeg libpq-dev`

**[Save Configuration]** button — writes fields to METADATA.md; does not rebuild automatically.

**[Regenerate Dockerfile]** button — re-runs `conform_dockerize`; shows diff in a modal if Dockerfile already exists.

---

## Status + Controls Panel

**Container Status Badge**
- States: `NOT BUILT` (grey) | `BUILT` (blue) | `RUNNING` (green) | `STOPPED` (yellow) | `EXITED` (red)
- Sourced from `docker inspect` result; polled every 10s via HTMX while page is open

**Image Info** (shown when built)
- Image name: `game-{project_name}:latest`
- Built at: timestamp
- "Rebuild needed" warning: shown if Dockerfile mtime is newer than last build timestamp

**Action Buttons**

| State | Available Actions |
|-------|------------------|
| NOT BUILT | [Build Image] |
| BUILT / STOPPED | [Start Container], [Rebuild Image] |
| RUNNING | [Stop Container], [Restart Container], [Rebuild Image (requires stop first)] |
| EXITED | [Start Container], [Rebuild Image] |

**[Build Image]** — calls `POST /api/{name}/run/docker-build`; fire-and-poll (same pattern as other operations); streams output to the Build Log tab.

**[Start Container]** — calls `POST /api/{name}/run/start` (GAME ops.py routes to `docker run` when docker_enabled); uses configured host port.

**[Stop Container]** — calls `POST /api/{name}/run/stop` (GAME routes to `docker stop`).

---

## Logs Panel

**Tab strip:** `Build Log` | `Container Log`

- **Build Log:** Output from last `docker build` run. Scrollable, monospace. "No build yet" placeholder when image has never been built.
- **Container Log:** Output from `docker logs --tail 200 game-{name}`. Auto-refreshes every 5s while container is RUNNING via HTMX polling. Stops polling when container is STOPPED or EXITED.

---

## Dockerfile Preview

Collapsible section at bottom of page: "Generated Dockerfile"
- Shows current content of `Dockerfile` at project root (read via `GET /api/{name}/file/Dockerfile`)
- Read-only syntax-highlighted code block (`<pre><code>`)
- Button: "Regenerate" — triggers `conform_dockerize` and refreshes content

---

## HTMX Interactions

| Trigger | Endpoint | Target |
|---------|----------|--------|
| Page load | `GET /projects/{name}/docker` | Full page |
| Status poll (every 10s) | `GET /api/{name}/docker/status` | Status badge + action buttons |
| Log poll (every 5s, RUNNING only) | `GET /api/{name}/docker/log` | Container log panel |
| Save config | `POST /projects/{name}/docker/config` | Configuration panel (inline success/error message) |
| Build image | `POST /api/{name}/run/docker-build` | Logs panel (fire-and-poll run_id) |
| Dockerfile preview | `GET /api/{name}/file/Dockerfile` | Dockerfile preview block |

---

## New API Endpoints Needed

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{name}/docker` | Render Docker management screen |
| POST | `/projects/{name}/docker/config` | Save docker config fields to METADATA.md |
| GET | `/api/{name}/docker/status` | Container status + image info JSON |
| GET | `/api/{name}/docker/log` | Live container log tail (last 200 lines) |
| GET | `/api/{name}/file/{filename}` | Read a named file from the project root |

`POST /api/{name}/run/docker-build` reuses the existing script runner with a virtual `docker-build` operation registered per-project when docker_enabled is detected at scan time.

`GET /api/{name}/file/{filename}` is general-purpose — extend FEATURE-SERVICE-CATALOG.md to include it.

---

## Open Questions

- Should the Docker tab appear for ALL projects (greyed out / collapsed when disabled) or only when docker_enabled? Decision: always show the tab with a clear enable toggle — better discoverability.
- Should [Build Image] be blocked if configuration has unsaved changes? Yes — show "Save configuration first" tooltip.
- Should the Dockerfile diff (on regenerate) be shown inline or in a modal? Decision: modal, to keep the layout clean.
- Should `GET /api/{name}/file/{filename}` be scoped to a safe allowlist (Dockerfile, pyproject.toml) or open? Allowlist preferred for security.
