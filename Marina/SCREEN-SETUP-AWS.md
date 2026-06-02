# Screen: Setup — AWS

| Field | Value |
|-------|-------|
| Version | 20260602 V4 |
| Header Background | `mn-hdr-bg--cloud` |
| Route | `GET /setup/aws` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | AWS |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Step-by-step AWS credential configuration, IAM connectivity check, and Python connectivity test. Configure the AWS profile, region, and org slug. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/aws |

## Header KPIs

Left column of the page header. Component type: **Status Light** (`mn-hdr-light`).

| State | Light | Condition |
|-------|-------|-----------|
| ✅ | `mn-hdr-light--ok` (green) | `aws_profile` set AND `python_aws_ok = 1` |
| ⚠️ | `mn-hdr-light--warn` (amber) | `aws_profile` set BUT `python_aws_ok = 0` or untested |
| ❌ | `mn-hdr-light--error` (red) | `aws_profile` empty or IAM unreachable |

## Layout

Single-column, max-width 900px, centered. Four `mn-card` sections stacked vertically: Identity, Organisation, Python Connectivity, IAM Check.

## Collapsible Card Behaviour

Every card is collapsible via Bootstrap 5 collapse. The card header acts as the toggle.

| Rule | Detail |
|------|--------|
| Start expanded | Card status is not OK (missing, unconfigured, or check failed) |
| Start collapsed | Card status is OK |
| Collapsed header | Must display a `✅ OK` badge so the user can see at a glance the item is configured |

Status criteria per card:

| Card | OK when |
|------|---------|
| AWS IDENTITY | `aws sts get-caller-identity` returns a valid ARN |
| ORGANISATION | `marina_org` setting is non-empty |
| PYTHON CONNECTIVITY | boto3 `sts.get_caller_identity()` returns a valid ARN |
| IAM REACHABILITY CHECK | Same result as AWS IDENTITY (shares the same check) |

```
┌──────────────────────────────────────────────────────────────┐
│  🔑  AWS IDENTITY                                            │
│  ───────────────────────────────────────────────────────── │
│  AWS Profile   [ default                                ▏ ] │
│  AWS Region    (from AWS_REGION env — set in .env)          │
│  ─────────────────────────────────────────────────────────  │
│  ℹ️  Marina uses the named AWS profile from your local       │
│     credentials file (~/.aws/credentials or SSO).           │
│     Set the profile name above, then click Check.           │
│                              [Check AWS Identity]           │
│  ✅  Authenticated as: arn:aws:iam::111:user/ed              │
├──────────────────────────────────────────────────────────────┤
│  🏢  ORGANISATION                                            │
│  ───────────────────────────────────────────────────────── │
│  Marina Org    [ acme                                   ▏ ] │
│  ─────────────────────────────────────────────────────────  │
│  ℹ️  The org slug is the DynamoDB partition key. All your    │
│     projects are stored under this key. Use a short         │
│     lowercase slug (e.g. acme, myname, dev-team).           │
├──────────────────────────────────────────────────────────────┤
│  🐍  PYTHON CONNECTIVITY                                     │
│  ───────────────────────────────────────────────────────── │
│  Tests that Marina's Python process can reach AWS via        │
│  boto3 using the configured profile and region.             │
│  This check must pass before Terraform can run.             │
│                                                              │
│  Status:  ✅  boto3 connected — arn:aws:iam::111:user/ed    │
│                              [Test Connection]              │
├──────────────────────────────────────────────────────────────┤
│  ✅  IAM REACHABILITY CHECK                                  │
│  ───────────────────────────────────────────────────────── │
│  Calls aws sts get-caller-identity to verify credentials.   │
│  Account: 111222333444                                       │
│  User ARN: arn:aws:iam::111222333444:user/ed                 │
│  Region:   us-east-1                                         │
│                              [Re-check]                      │
└──────────────────────────────────────────────────────────────┘
```

## AWS IDENTITY Card

Two fields: AWS Profile (inline editable, settings-backed) and AWS Region (read-only, env-backed).

| Field | Key | Editable | Notes |
|-------|-----|----------|-------|
| AWS Profile | `aws_profile` (settings) | Yes | Default: `default`. Used in all boto3/AWS CLI calls. |
| AWS Region | `AWS_REGION` (env) | No | Shown as read-only. Add `AWS_REGION=us-east-1` to `.env` to set. |

Below the fields: a `[Check AWS Identity]` button. On click calls `POST /api/setup/aws/check-identity`. Shows result inline:
- ✅ — ARN, account ID, region
- ❌ — error message with hint (e.g., `Profile 'foo' not found in ~/.aws/credentials`)

Static guidance block below: instructions for configuring AWS credentials via `aws configure` or SSO.

## ORGANISATION Card

Single inline-editable field: Marina Org (`marina_org`, settings-backed).

| Field | Key | Editable | Notes |
|-------|-----|----------|-------|
| Marina Org | `marina_org` (settings) | Yes | Default: `Marina`. No additional AWS setup required — the org slug is a DynamoDB partition key only. |

Validation: lowercase alphanumeric plus hyphens only (`^[a-z0-9-]+$`). Server rejects invalid slugs with 400. Client-side warning shown before save.

Static guidance block: explains the org slug is the DynamoDB partition key and that changing it after data exists requires a migration.

## PYTHON CONNECTIVITY Card

Tests that the Marina Flask process itself can make AWS API calls via boto3. This is separate from the AWS CLI identity check — it confirms that the Python environment, boto3 library, and IAM credentials are all functional together.

`[Test Connection]` triggers `POST /api/setup/aws/check-python`. Result shown inline:
- ✅ — `boto3 connected — {ARN}` (teal)
- ❌ — error message with hint (e.g., `NoCredentialsError: Unable to locate credentials`)

Static guidance block: explains this check is required for Terraform to run, and that it validates the same profile/region configured above.

The result is persisted in `platform_stats` as `python_aws_ok` (1/0) so the Terraform page can gate on it without re-running the check.

## IAM REACHABILITY CHECK Card

Displays the result of `aws sts get-caller-identity` using the configured `aws_profile`. Fields shown: Account, User ARN, Region, UserId.

`[Re-check]` button triggers `POST /api/setup/aws/check-identity` and updates this card in place.

On failure, shows the exact AWS error message and a link to the AWS tab help guide.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/setup/aws/check-identity` | — | HTML fragment: identity card content (✅ or ❌) |
| POST | `/api/setup/aws/check-python` | — | HTML fragment: Python connectivity result (✅ or ❌) |
| POST | `/api/setup/config` | `key`, `value` | Icon fragment (shared with Summary) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`aws_profile`, `marina_org`) | `settings` table via `/api/setup/config` |
| `AWS_REGION` (env) | `platform_stats.python_aws_ok` (on check-python) |
| `aws sts get-caller-identity` (subprocess) | None |
| boto3 `sts.get_caller_identity()` | None |

## Open Questions

- Should Marina support AWS SSO profiles in addition to static credentials? V1: use the named profile as-is — SSO profiles work transparently via the AWS SDK if already configured via `aws sso login`.
- Should the API endpoint card auto-detect the URL from Terraform state if `terraform/` exists? V2 — too fragile for V1.
