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
3. It reads the ACL item `PK=ORG#{org}, SK=PROJECT#{project}#ACL#{principal}` (DATABASE.md pattern 11),
   served from an **in-process cache keyed by `(org, project, principal)` with a 5-minute TTL**; a miss
   falls back to `GetItem`. The cache is a latency optimisation only (see ARCHITECTURE.md); a revoked
   grant stops working within five minutes.
4. If the grant exists and its `access` covers the requested action (`read` ⊆ `readwrite`), allow;
   otherwise return `403 forbidden`. Org-wide read of the catalog index (project list) is allowed to any
   Org principal; per-project detail and any invoke require a grant.

**Onboarding (`POST /onboard` — Org-admin only):**

1. `POST /onboard` is restricted to a specific Org-admin principal (its invoke role trusts only the admin
   ARN). Members cannot grant themselves access; only an admin writes grants.
2. A member is added to the AWS Organization (their account/role becomes a valid SigV4 principal).
3. Onboarding verifies the member's git-repo access at onboard time by calling the GitHub REST API with a
   supplied token (`GET /user/repos?affiliation=owner,collaborator,organization_member`). The token is
   **used once and never persisted**. For each repo that maps to a Marina project, it writes an ACL grant
   (`PUT PK=ORG#{org}, SK=PROJECT#{project}#ACL#{principal}`, DATABASE.md pattern 12) with `access`
   derived from the collaborator permission: `admin`/`maintain`/`write` → `readwrite`; `triage`/`read` →
   `readonly`.
4. The grant records the `repo` it came from so it can be re-derived if repo access changes.

**Re-derivation:** a **nightly scheduled re-sync Lambda** re-derives all grants so they track repo-access
changes without manual re-onboarding (cheap; keeps grants current). The gate itself never calls GitHub —
it reads the ACL table (cached), keeping per-request latency low and removing a runtime GitHub
dependency.

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

- None open. The repo→grant derivation (GitHub token at onboard, never stored), the 5-minute in-process
  gate cache, the nightly re-sync, and admin-only `POST /onboard` are all settled above.
