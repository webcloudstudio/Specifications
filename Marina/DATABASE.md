# DATABASE: Marina Catalog (DynamoDB single-table)

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | One DynamoDB table per environment holding the whole organization tree — projects, capabilities, heartbeats, events, and access grants — read as subtrees, never joined on the server. |

**Description:** The DynamoDB single-table hierarchical schema and the exact access patterns it serves.
See `stack/aws-dynamodb.md` for the rules this design follows.

---

## Design Principle

Marina's data is **simple and hierarchical**: one organization contains projects; a project contains
capabilities, heartbeats, events, and access grants. It is read as a subtree and assembled in the
client. The schema therefore uses one table with a composite key whose hierarchy lives in the sort key,
so any "read this project and everything under it" is a single `Query`. There are **no server-side
joins and no `Scan`s**.

## Table

`marina-{project}-catalog` — `PAY_PER_REQUEST`, PITR on, SSE on. Composite primary key `PK` (partition)
+ `SK` (sort). One partition per organization is the tenant boundary.

## Item Types and Keys

| Item type | PK | SK | Notes |
|-----------|----|----|-------|
| Project | `ORG#{org}` | `PROJECT#{project}` | Identity + metadata |
| Capability | `ORG#{org}` | `PROJECT#{project}#CAP#{name}` | One per declared capability |
| Heartbeat | `ORG#{org}` | `PROJECT#{project}#HB#{program}` | Latest state per program (overwritten) |
| Event | `ORG#{org}` | `PROJECT#{project}#EVT#{ulid}` | Append-only; ULID sorts by time; carries a `ttl` epoch (30-day expiry) |
| Access grant | `ORG#{org}` | `PROJECT#{project}#ACL#{principal}` | Repo→capability authorisation (see FEATURE-ACCESS-CONTROL) |

Every item carries `type`, `project`, and `updated_at` (ISO-8601).

### Representative items

```json
{ "PK": "ORG#acme", "SK": "PROJECT#market",
  "type": "project", "project": "market", "display_name": "Market Downloader",
  "short_description": "Daily price ETL", "status": "ACTIVE", "stack": "Python/SQLite",
  "repo": "acme/market", "updated_at": "2026-05-28T12:00:00Z" }

{ "PK": "ORG#acme", "SK": "PROJECT#market#CAP#download_prices",
  "type": "capability", "project": "market", "name": "download_prices",
  "description": "Download historical market prices", "tags": ["finance","etl"],
  "transports": ["cli","rest"], "owners": ["ed"], "access": "readwrite",
  "updated_at": "2026-05-28T12:00:00Z" }

{ "PK": "ORG#acme", "SK": "PROJECT#market#HB#daily",
  "type": "heartbeat", "project": "market", "program": "daily",
  "state": "OK", "message": "completed", "updated_at": "2026-05-28T06:05:00Z" }

{ "PK": "ORG#acme", "SK": "PROJECT#market#EVT#01J...ULID",
  "type": "event", "project": "market", "severity": "ERROR",
  "message": "rate limited by upstream", "updated_at": "2026-05-28T06:04:11Z",
  "ttl": 1751004251 }

{ "PK": "ORG#acme", "SK": "PROJECT#market#ACL#arn:aws:iam::111:user/jane",
  "type": "acl", "project": "market", "principal": "arn:aws:iam::111:user/jane",
  "repo": "acme/market", "access": "readwrite", "updated_at": "2026-05-28T09:00:00Z" }
```

## Access Patterns (every read/write served by GetItem or Query)

| # | Pattern | Feature | Operation | Key condition |
|---|---------|---------|-----------|---------------|
| 1 | Upsert project metadata | catalog-publish | PutItem | `PK=ORG#{org}, SK=PROJECT#{p}` |
| 2 | Upsert a capability | catalog-publish | PutItem | `PK=ORG#{org}, SK=PROJECT#{p}#CAP#{c}` |
| 3 | Read one project + all children | catalog-read | Query | `PK=ORG#{org} AND begins_with(SK,"PROJECT#{p}")` |
| 4 | List all projects in org | catalog-read | Query | `PK=ORG#{org} AND begins_with(SK,"PROJECT#")` then filter `type=project` client-side |
| 5 | Read one capability | catalog-read | GetItem | `PK=ORG#{org}, SK=PROJECT#{p}#CAP#{c}` |
| 6 | List capabilities (optionally by tag) | capabilities-read | Query | `PK=ORG#{org} AND begins_with(SK,"...#CAP#")`; tag filter client-side |
| 7 | Write a heartbeat | report-ingest | PutItem | `PK=ORG#{org}, SK=PROJECT#{p}#HB#{prog}` |
| 8 | Append an event | report-ingest | PutItem | `PK=ORG#{org}, SK=PROJECT#{p}#EVT#{ulid}` |
| 9 | Latest heartbeats for a project | health-read | Query | `... begins_with(SK,"PROJECT#{p}#HB#")` |
| 10 | Recent events newest-first | health-read | Query | `... begins_with(SK,"PROJECT#{p}#EVT#"), ScanIndexForward=False, Limit=N` |
| 11 | Read a principal's grant | access-control | GetItem | `PK=ORG#{org}, SK=PROJECT#{p}#ACL#{principal}` |
| 12 | Write a grant at onboarding | access-control | PutItem | `PK=ORG#{org}, SK=PROJECT#{p}#ACL#{principal}` |

No GSI is required for Phase 1/2 — the base key serves every pattern. A GSI is added only if a future
cross-project query (e.g. "all capabilities tagged finance across all projects") becomes a hot path.

## Writes Are Idempotent

Publish overwrites the current projection with `PutItem` guarded by a condition
(`attribute_not_exists(SK) OR updated_at <= :now`) so concurrent or out-of-order publishers cannot
regress a newer record. The existence check uses `SK` (the unique key within the partition), not `PK`:
`attribute_not_exists(PK)` is never true for an item that already exists, so it would silently disable
the guard. All writes go through `marina.catalog` / `marina.report`.

## Event Retention (TTL)

Event items carry a `ttl` attribute — Unix epoch seconds set to `updated_at + 30 days`. DynamoDB TTL is
enabled on the table against the `ttl` attribute, so events self-expire and never accumulate cost. The
30-day window keeps recent debugging history without unbounded growth. Project/capability/heartbeat/ACL
items carry no `ttl` and persist until overwritten or explicitly removed.

## Open Questions

- Heartbeat history is latest-only (`HB#{program}` overwrite) for Phase 1/2. A short ring of
  `HB#{program}#{ulid}` entries would aid post-incident debugging — add only if a real incident shows
  the latest-only view is insufficient.
