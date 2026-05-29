# Feature: Catalog Publish

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | The local agent upserts a project's metadata and capability catalog into DynamoDB through an IAM-authorised endpoint. |
| Depends On  | FEATURE-MARINA-LIB.md, FEATURE-ACCESS-CONTROL.md |
| Provides    | POST /catalog |

**Description:** Publish the read-mostly projection of a project — its `METADATA.md` identity and its
`AGENTS.md ## Capabilities` block — to the cloud catalog so the circle of trust can read it 24×7.

## Trigger

The local control-plane agent calls `mar.catalog.publish(project_meta, capabilities)` after a scan, or a
conformed project's `bin/` script calls it after a change. There is no browser path.

## Sequence

1. The agent assembles `project_meta` (name, display_name, short_description, status, stack, repo) from
   `METADATA.md` and `capabilities[]` from the project's `AGENTS.md ## Capabilities` JSON.
2. `mar.catalog.publish` SigV4-signs and `POST /catalog` with `{project_meta, capabilities}`.
3. The `catalog_publish` Lambda validates the body, then calls `authz.gate(principal, org, project,
   "readwrite")` — only a principal with write access to that project's repo may publish it.
4. The Lambda upserts one `project` item and one `capability` item per entry (DATABASE.md patterns 1–2),
   each `PutItem` guarded by the idempotency condition (`updated_at <= :now`). Capabilities absent from
   the new payload are removed (a publish is the full current projection for that project).
5. Returns `{project, published_capabilities, updated_at}`.

## Reads

- Request body (`project_meta`, `capabilities`).
- DynamoDB: existing capability items for the project (to compute removals).
- ACL via the access-control gate.

## Writes

- DynamoDB: `project` item (upsert), `capability` items (upsert + prune), through `marina.catalog`.

## Test

- **Script:** `bin/test_catalog_publish.sh` → publishes a synthetic project with two capabilities, then
  asserts via `GET /catalog/{project}` that the project and both capabilities are present; re-publishes
  with one capability and asserts the dropped one is pruned.
- **Pass criteria:** items match the published payload; idempotency condition prevents an older
  `updated_at` from overwriting a newer one; non-write principals get 403.
- **CloudWatch:** `catalog_publish` log group emits
  `{"event":"catalog_publish","project":...,"capabilities":N}`; access log shows `POST /catalog` 200.

## Open Questions

- Should publish be diff-based (only changed items) rather than full-projection-with-prune? Full
  projection is simpler and idempotent; diffing saves writes at scale but is unnecessary now.
- Should a publish also stamp a `catalog_version`/checksum on the project item so readers can detect
  staleness cheaply? Likely yes — a short hash of the payload. Defer unless a reader needs it.
