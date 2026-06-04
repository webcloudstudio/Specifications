# SPEC: Change_Log

| Field       | Value |
|-------------|-------|
| Version     | 20260604 V1 |
| Description |  |

# CHANGE_LOG.md — Marina

Append-only change log. Format: DATE | TYPE | SCOPE | DESCRIPTION
Types: CHANGE (pending), AC (permanent guardrail), DONE (applied — written by process script).
Scope: route path (/route), base filename (DATABASE.md), or spec filename (SCREEN-FOO.md).

2026-06-03 | CHANGE | DATABASE.md | last_scan value stored in platform_stats must be a full ISO-8601 string with UTC offset (e.g. 2026-06-03T14:50:56+00:00) — truncating to HH:MM or stripping the offset causes offset-naive vs offset-aware TypeError in _relative_time
2026-06-03 | DONE | DATABASE.md | Applied: tightened last_scan description to require UTC offset, added format example and prohibition on truncation
2026-06-03 | AC     | infra/foundation | Terraform layers (backend/foundation/services) must contain working HCL — resource/variable/output blocks. Comment-only stub .tf files are a build failure; terraform validate must pass and terraform fmt -check must report no diffs in each layer.
2026-06-03 | CHANGE | FEATURE-INFRA.md | infra/ Terraform tree was built as comment-only stubs (no variable blocks, hence 'undeclared variable org'). Rebuild backend/foundation/services per FEATURE-INFRA.md as real HCL: shared variables.tf (project/org/region/phase, no defaults), S3+DynamoDB backend, catalog table with TTL, SQS/S3/IAM in foundation, Lambdas+API Gateway in services, api_url output in services.
2026-06-03 | CHANGE | /setup/terraform | COMMANDS TO RUN card and api_url auto-read must match FEATURE-INFRA.md: layered tf-*.sh wrappers (backend->foundation->services) with -var-file=../env.tfvars; api_url is a services-layer output read via 'terraform -chdir=infra/services output -raw api_url', not foundation.
