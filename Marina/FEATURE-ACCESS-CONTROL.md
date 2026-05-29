# Feature: Access Control

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Org-identity authorisation that mirrors git-repo access — the shared gate every read and invoke path calls before touching project data. |
| Depends On  | FEATURE-MARINA-LIB.md |
| Provides    | POST /onboard |

**Description:** The authorisation model. Identity is the caller's AWS Organization principal (proven by
SigV4 at API Gateway). Authorisation mirrors git-repo access: if a member can use a project's repository,
they may read or invoke that project's capability. Grants are recorded in an Org-side ACL table at
onboarding and checked at request time by a shared gate module.

## Trigger

- **Onboarding:** `POST /onboard` registers a member's AWS principal and computes their project grants
  from their git-repo access.
- **Every protected request:** `catalog_read`, `report_ingest`, `queue_submit`, and `share_index` call
  the shared `authz.gate(principal, org, project, access)` before acting.

## Sequence

**Authorisation gate (per request):**

1. API Gateway has already authenticated the caller (IAM/SigV4); the Lambda reads the principal ARN from
   the request context (`$context.identity.userArn`).
2. The gate resolves the target `project` from the route/body.
3. It reads the ACL item `PK=ORG#{org}, SK=PROJECT#{project}#ACL#{principal}` (DATABASE.md pattern 11).
4. If the grant exists and its `access` covers the requested action (`read` ⊆ `readwrite`), allow;
   otherwise return `403 forbidden`. Org-wide read of the catalog index (project list) is allowed to any
   Org principal; per-project detail and any invoke require a grant.

**Onboarding (`POST /onboard`):**

1. A member is added to the AWS Organization (their account/role becomes a valid SigV4 principal).
2. Onboarding verifies the member's git-repo access (Spike 2: GitHub token check at onboarding time) and,
   for each repo they can use, writes an ACL grant
   (`PUT PK=ORG#{org}, SK=PROJECT#{project}#ACL#{principal}`, DATABASE.md pattern 12) with `access`
   derived from repo permission (`read` vs `readwrite`).
3. The grant records the `repo` it came from so it can be re-derived if repo access changes.

**Re-derivation:** onboarding (or a periodic re-sync) is the source of truth for grants. The gate itself
does not call GitHub — it reads the ACL table, keeping per-request latency low and removing a runtime
GitHub dependency.

## Reads

- DynamoDB ACL items (`...#ACL#{principal}`).
- Request context principal ARN from API Gateway (IAM auth).
- At onboarding: the member's git-repo access (one-time, via their token).

## Writes

- DynamoDB ACL items on onboarding / re-sync.

## Test

- **Script:** `bin/test_access_control.sh` → (1) onboard a synthetic principal with access to repo A
  only; (2) assert `GET /catalog/{A}` succeeds and `GET /catalog/{B}` returns 403; (3) assert an
  un-onboarded principal gets the org-wide project list but 403 on any project detail.
- **Pass criteria:** grants written correctly; gate allows/denies per the matrix above; no GitHub call
  occurs on the read path.
- **CloudWatch:** denials log a structured `{"event":"authz_deny","principal":...,"project":...}` line in
  the relevant Lambda log group; the access-log group shows the 403 status.

## Open Questions

- Spike 2: confirm the repo→grant derivation (GitHub token check at onboarding) and whether the gate
  caches the ACL per warm Lambda for a short TTL to cut DynamoDB reads. Default: direct read, no cache.
- Should grant re-sync be a scheduled job or only re-run on explicit re-onboard? A nightly re-sync keeps
  grants current as repo access changes; explicit-only is simpler. Leaning nightly re-sync (cheap).
- Should `POST /onboard` itself be Org-admin-only (a specific principal), rather than self-serve? Yes —
  only an Org admin principal may write grants; members cannot grant themselves access.
