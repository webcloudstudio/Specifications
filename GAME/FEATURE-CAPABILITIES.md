# Feature: Capability Catalog

**Version:** 20260417 V1
**Description:** Transport-agnostic capability registry — how projects declare callable functions and how the platform discovers, routes, and invokes them.

---

## Core Model

```
METADATA.md  →  AGENTS.md (capabilities block)  →  Service Catalog  →  invoke()
  identity        what this project can do           network index      single call
```

A **capability** is a named, typed, invokable function. It has a contract (inputs, outputs) that is independent of how it is called. The platform selects the transport.

---

## Declaring Capabilities (AGENTS.md)

Each project declares its capabilities in `AGENTS.md` under a `## Capabilities` section as a JSON block:

```json
{
  "capabilities": [
    {
      "name": "download_prices",
      "description": "Download historical market prices",
      "tags": ["finance", "data-source", "etl"],

      "invoke": {
        "cli": "bin/download_prices",
        "rest": {
          "method": "POST",
          "path": "/download/prices"
        },
        "mcp": "download_prices"
      },

      "input": {
        "symbol":     { "type": "string", "required": true },
        "start_date": { "type": "date",   "required": true },
        "end_date":   { "type": "date",   "required": true }
      },

      "output": {
        "dataset_id":      { "type": "string" },
        "rows_downloaded": { "type": "integer" }
      },

      "permissions": {
        "owners": ["ed", "bob"],
        "access": "readwrite"
      },

      "lifecycle": "on-demand"
    }
  ]
}
```

### Fields

| Field | Required | Values |
|-------|----------|--------|
| `name` | Yes | Globally unique slug within the network |
| `description` | Yes | One sentence |
| `tags` | No | Arbitrary strings for filtering |
| `invoke.cli` | If CLI enabled | Path to bin/ script |
| `invoke.rest` | If REST enabled | `method` + `path` |
| `invoke.mcp` | If MCP enabled | MCP tool name |
| `input` | Yes | Named fields with `type` and `required` |
| `output` | Yes | Named fields with `type` |
| `permissions.owners` | No | List of user identities with write access |
| `permissions.access` | No | `readonly` \| `readwrite` |
| `lifecycle` | Yes | `on-demand` \| `always-on` \| `scheduled` |

---

## Service Catalog API

The Service Catalog aggregates `## Capabilities` blocks from all discovered projects.

### Query Capabilities

```
GET /api/capabilities
```

All query parameters are optional.

**Request:**
```json
{
  "tags": ["finance"],
  "owner": "ed",
  "namespace": "development"
}
```

**Response:**
```json
{
  "capabilities": [
    {
      "name": "download_prices",
      "project": "market_downloader",
      "description": "Download historical market prices",
      "tags": ["finance", "data-source", "etl"],
      "transports": ["cli", "rest", "mcp"],
      "lifecycle": "on-demand"
    }
  ]
}
```

### Invoke a Capability

```
POST /api/capabilities/invoke
```

**Request:**
```json
{
  "capability": "download_prices",
  "args": {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-02-01"
  },
  "identity": "ed",
  "preferred_transport": "auto"
}
```

`preferred_transport`: `auto` | `cli` | `rest` | `mcp`

**Response (success):**
```json
{
  "status": "success",
  "capability": "download_prices",
  "transport_used": "cli",
  "result": {
    "dataset_id": "ds_88421",
    "rows_downloaded": 523
  }
}
```

**Response (async accepted):**
```json
{
  "status": "accepted",
  "job_id": "job_9912",
  "message": "Capability running asynchronously"
}
```

**Response (error):**
```json
{
  "status": "error",
  "error": "permission_denied",
  "message": "User not authorized for capability"
}
```

---

## Transport Selection

The platform resolves transport automatically when `preferred_transport: auto`:

| Caller | Transport |
|--------|-----------|
| Local Python | CLI |
| Remote Python | REST |
| AI Agent | MCP |

Resolution order: `cli` → `rest` → `mcp`. The first available transport wins unless the caller specifies one.

---

## Invocation Interface

All execution resolves to a single logical interface regardless of transport:

```python
async def invoke(
    capability: str,
    args: dict,
    context: dict | None = None
) -> dict:
    ...
```

The platform resolves: capability → project → availability → permissions → transport → execution.

---

## Rules

1. Capability names are globally unique within the network. Name collisions surface immediately at catalog assembly time.
2. Contracts are transport-independent. Input/output schemas apply regardless of how the capability is called.
3. All input and output must be structured and machine-readable (JSON preferred).
4. Permissions are declared in the publishing project's `AGENTS.md` and enforced by the platform.
5. Projects may change their implementation without breaking clients as long as the contract (input/output schema) is unchanged.

---

## Relationship to Existing Features

| Feature | Role |
|---------|------|
| `FEATURE-SERVICE-CATALOG.md` | Script runner and endpoint catalog (the existing local surface area view) |
| `FEATURE-CAPABILITIES.md` (this file) | Network-level capability registry with typed contracts and transport routing |
| `FEATURE-ServiceInterfaces.md` | Superseded by this file — the YAML manifest approach is replaced by the JSON capabilities block in AGENTS.md |

---

## Open Questions

- Should capability name collisions fail hard (startup error) or resolve by precedence (local wins over remote)?
- Should `lifecycle: always-on` capabilities auto-start their backing service when the server comes up?
- Should the catalog screen (SCREEN-CATALOG.md) show a Capabilities tab alongside Scripts / REST / MCP?
