# Feature: Catalog Read

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Private 24x7 read of the org project tree, a single project subtree, or the capability list, via IAM-authorised GET endpoints. |
| Depends On  | FEATURE-CATALOG-PUBLISH.md, FEATURE-ACCESS-CONTROL.md |
| Provides    | GET /catalog, GET /catalog/{project}, GET /capabilities |

**Description:** The headline 24×7 win — any member of the circle of trust can read the catalog and
capabilities at any time (even when the publishing machine is off), through SigV4-authorised reads. The
data returned is last-known projection, never live.

## Trigger

A member calls `mar.catalog.read()` / `mar.catalog.read(project)` / `mar.catalog.read_capabilities(tags)`,
or hits the endpoints with the AWS CLI (`awscurl`-style SigV4). No anonymous access.

## Sequence

1. **`GET /catalog`** — `catalog_read` Lambda queries `PK=ORG#{org} AND begins_with(SK,"PROJECT#")`
   (DATABASE.md pattern 4), returns the project list. Allowed to any Org principal (the index is
   org-wide-readable); per-project detail is gated.
2. **`GET /catalog/{project}`** — gate checks read access to `{project}`; Lambda queries
   `begins_with(SK,"PROJECT#{project}")` (pattern 3) and returns the project plus its capabilities,
   heartbeats, and recent events assembled into one tree (joined client-side, never in DynamoDB).
3. **`GET /capabilities`** — queries capability items (pattern 6); optional `?tags=` filter applied
   client-side in the Lambda; results restricted to projects the principal may read.
4. Responses are JSON with `generated_at` so callers can detect staleness.

## Reads

- DynamoDB via `Query`/`GetItem` (patterns 3, 4, 5, 6); no scans.
- ACL via the access-control gate.

## Writes

- None.

## Test

- **Script:** `bin/test_catalog_read.sh` → after a known publish, asserts `GET /catalog` lists the
  project, `GET /catalog/{project}` returns the full subtree, and `GET /capabilities?tags=finance`
  filters correctly; asserts a principal without access to a project cannot read its detail.
- **Pass criteria:** correct items returned, tree assembled client-side, no `Scan` in the access path
  (verified against the DynamoDB call log / `moto` assertions), `generated_at` present.
- **CloudWatch:** `catalog_read` log group emits `{"event":"catalog_read","project":...,"items":N}`;
  access log shows the `GET` route, principal, status, and latency.

## Open Questions

- Should `GET /catalog/{project}` cap the number of recent events it inlines (e.g. last 20) to bound
  response size, with a separate endpoint for deeper history? Leaning yes — inline last 20, paginate the
  rest later.
- Caching: add a short CloudFront or in-Lambda cache for the org-wide `GET /catalog` index? Not in Phase
  1 — request volume is tiny; revisit only if read cost ever matters.
