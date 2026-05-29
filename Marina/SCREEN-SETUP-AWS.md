# Screen: Setup — AWS

| Field | Value |
|-------|-------|
| Version | 20260529 V1 |
| Route | `GET /setup/aws` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | AWS |
| Tab Order | 1: Summary · 2: AWS · 3: GitHub · 4: Repositories · 5: Projects · 6: Settings |
| Description | Step-by-step AWS credential configuration and IAM connectivity check. Configure the AWS profile, region, org slug, and Marina API endpoint. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/aws |

## Layout

Single-column, max-width 900px, centered. Four `mn-card` sections stacked vertically: Identity, Organisation, API Endpoint, IAM Check.

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
│  🌐  MARINA API ENDPOINT                                     │
│  ───────────────────────────────────────────────────────── │
│  Set MARINA_API_URL in .env after deploying Terraform:      │
│  MARINA_API_URL=https://abc123.execute-api.us-east-1...     │
│                                                              │
│  Current value:  ⚠️  (not set)                              │
│                                                              │
│  Steps to deploy:                                            │
│  1. cd terraform && terraform init                           │
│  2. terraform plan -var="org=acme"                          │
│  3. terraform apply                                          │
│  4. Copy the api_url output to .env                         │
│  5. Restart Marina                                           │
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

Validation: lowercase alphanumeric plus hyphens only (`^[a-z0-9-]+$`). Server rejects invalid slugs with 400. Client-side warning shown before save.

Static guidance block: explains the org slug is the DynamoDB partition key and that changing it after data exists requires a migration.

## MARINA API ENDPOINT Card

Read-only display of `MARINA_API_URL` env var status (✅ / ⚠️). No editable field — the URL is set in `.env` because it requires a restart.

Step-by-step Terraform deployment guide rendered as a numbered instruction list. Steps reference the Marina `terraform/` directory.

A `[Copy MARINA_API_URL env line]` button copies the template string `MARINA_API_URL=<url>` to clipboard once a URL is configured, to ease `.env` editing.

## IAM REACHABILITY CHECK Card

Displays the result of `aws sts get-caller-identity` using the configured `aws_profile`. Fields shown: Account, User ARN, Region, UserId.

`[Re-check]` button triggers `POST /api/setup/aws/check-identity` and updates this card in place.

On failure, shows the exact AWS error message and a link to the AWS tab help guide.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/setup/aws/check-identity` | — | HTML fragment: identity card content (✅ or ❌) |
| POST | `/api/setup/config` | `key`, `value` | Icon fragment (shared with Summary) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`aws_profile`, `marina_org`) | `settings` table via `/api/setup/config` |
| `AWS_REGION`, `MARINA_API_URL` (env) | None |
| `aws sts get-caller-identity` (subprocess) | None |

## Open Questions

- Should Marina support AWS SSO profiles in addition to static credentials? V1: use the named profile as-is — SSO profiles work transparently via the AWS SDK if already configured via `aws sso login`.
- Should the API endpoint card auto-detect the URL from Terraform state if `terraform/` exists? V2 — too fragile for V1.
