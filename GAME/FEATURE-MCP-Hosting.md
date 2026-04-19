# Feature: MCP Hosting


| Field       | Value |
|-------------|-------|
| Version     | (set version) |
| Description |  |

**Version:** 2026-04-06 V1
**Description:** GAME as an MCP server host — discover, register, start, stop, and expose developer-created MCP servers

## Design Intent

Developers building projects on the platform may want to create MCP servers — tools that Claude (or other agents) can call during a conversation. Today, a developer would have to manually configure `.mcp.json`, manage the server process themselves, and tell coworkers how to connect. GAME should manage this lifecycle the same way it manages bin/ scripts: discover them, show them in the catalog, start/stop them, and let the developer expose them to others with a click.

**Key principle:** GAME does not require developers to write MCP servers. MCP is one transport option among five (see FEATURE-ServiceInterfaces.md). But when a developer does write one, GAME should be the place that hosts it — handling process lifecycle, port assignment, and discoverability.

**The coworker scenario:** Developer A writes a pricing lookup MCP server for their project. They register it in GAME and click "Expose" on the Service Catalog. GAME starts the server and makes the connection info available. Developer B adds it to their `.mcp.json` and Claude can now call pricing tools. When Developer A updates the server, GAME restarts it. No manual process management. No Slack messages saying "hey restart your MCP thing."

**Local-first, promote-to-remote:** MCP servers start as stdio (local subprocess, no network). When a developer clicks "Expose," GAME starts the server with SSE or streamable-HTTP transport on an assigned port. Coworkers connect over the network. The server code does not change — only the transport config. This mirrors the GAME philosophy: start simple, promote when needed.

---

## MCP Server Discovery

GAME discovers MCP servers during the project scan, similar to how it discovers bin/ scripts:

### Convention: `mcp/` Directory

A project that provides MCP servers places them in `mcp/`:

```
myproject/
  mcp/
    pricing.py          # MCP server script
    pricing.service.yaml  # Service manifest (FEATURE-ServiceInterfaces format)
```

The scanner reads `mcp/*.service.yaml` and registers each as a service with `source = mcp:{project_name}`. The `.py` file is the server entry point.

### Server Manifest Extension

MCP servers use the standard service manifest with additional MCP-specific fields:

```yaml
name: pricing
description: Product pricing lookup and calculation tools
version: 1.0.0

transports:
  mcp: true             # This IS an MCP server
  rest: false            # Not also exposed via REST (unless developer enables)

mcp:
  entry: pricing.py      # Script to run
  runtime: python        # python | node | binary
  requirements: requirements.txt  # Dependencies (optional)
  default_transport: stdio  # stdio | sse | streamable-http

tools:
  - name: get_price
    description: Look up the current price for a product by SKU
    inputs:
      sku:
        type: string
        required: true
    output:
      price: number
      currency: string
```

---

## MCP Server Lifecycle

### Registration

During scan, GAME:
1. Finds `mcp/*.service.yaml` in each project
2. Parses the manifest
3. Inserts/updates the `services` table with `source = mcp:{project_name}`
4. Inserts/updates `service_tools` with the tool definitions
5. Registers an entry in `mcp_servers` table (see schema below)

### Start / Stop

MCP servers are managed like any other operation — through the process engine (`ops.py`/`spawn.py`):

| Action | How |
|--------|-----|
| **Start (stdio)** | Not started by GAME — Claude Code starts it via `.mcp.json` config pointing at the script |
| **Start (exposed)** | GAME launches the server as a subprocess with SSE/streamable-HTTP transport on an assigned port |
| **Stop** | SIGTERM via process engine, same as any operation |
| **Restart** | Stop + Start (triggered by developer or after project update) |

### Expose / Unexpose

The Service Catalog screen shows an "Expose" toggle for each MCP server:

- **Unexposed (default):** Server is stdio-only. Only the local developer's Claude can use it via `.mcp.json` pointing at the script path. GAME does not start a process.
- **Exposed:** GAME starts the server on an assigned port (from a configurable range, default 9100-9199). The connection URL is shown in the Service Catalog. Other developers add the URL to their `.mcp.json`.

---

## .mcp.json Generation

GAME can generate `.mcp.json` snippets for any registered MCP server:

**Stdio (local use):**
```json
{
  "mcpServers": {
    "pricing": {
      "command": "python",
      "args": ["/path/to/myproject/mcp/pricing.py"],
      "transport": "stdio"
    }
  }
}
```

**SSE (exposed, network use):**
```json
{
  "mcpServers": {
    "pricing": {
      "url": "http://192.168.1.42:9101/mcp"
    }
  }
}
```

The Service Catalog provides a "Copy Config" button that copies the appropriate JSON snippet to the clipboard.

---

## New Database Table: `mcp_servers`

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| service_id | INTEGER FK | — | References services.id |
| project_id | INTEGER FK | — | References projects.id |
| entry_script | TEXT | — | Relative path to server script within the project |
| runtime | TEXT | 'python' | python / node / binary |
| requirements | TEXT | NULL | Path to requirements file (relative to project) |
| default_transport | TEXT | 'stdio' | stdio / sse / streamable-http |
| exposed | INTEGER | 0 | 1 = running on network port |
| assigned_port | INTEGER | NULL | Port assigned when exposed |
| pid | INTEGER | NULL | OS process ID when running |
| status | TEXT | 'stopped' | stopped / starting / running / error |
| last_started | TEXT | NULL | Timestamp |
| last_error | TEXT | NULL | Last error message if status = error |
| created_at | TEXT | datetime('now') | |
| updated_at | TEXT | datetime('now') | |

---

## New Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/mcp` | List all registered MCP servers with status |
| POST | `/api/mcp/{id}/start` | Start an MCP server (exposed mode) |
| POST | `/api/mcp/{id}/stop` | Stop a running MCP server |
| POST | `/api/mcp/{id}/expose` | Toggle expose on (start on network port) |
| POST | `/api/mcp/{id}/unexpose` | Toggle expose off (stop network process) |
| GET | `/api/mcp/{id}/config` | Get .mcp.json snippet for this server |

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `MCP_PORT_RANGE_START` | `9100` | First port in the MCP server port range |
| `MCP_PORT_RANGE_END` | `9199` | Last port in the MCP server port range |
| `MCP_AUTO_EXPOSE` | `false` | If true, newly discovered MCP servers are auto-exposed |

---

## Open Questions

- Should GAME provide a scaffold command (`game-cli mcp init {name}`) that generates a starter MCP server with the manifest template? Would reduce friction for developers creating their first MCP server.
- Should exposed MCP servers have authentication (API key, shared secret)? For local network use, probably not. For remote access, yes. Defer to when remote hosting is designed.
- Should GAME monitor MCP server health (periodic tool call or ping)? Or is process-alive sufficient?
