# merge.sh

**Version:** 20260327 V1
**Script:** `bin/merge.sh`
**Description:** Squash-merge the prototype Feature Branch into the base branch and delete it.

Reads `BUILD_FEATURE_BRANCH_NAME` from `Specifications/<PROJECT>/.env` and `base_branch` from `METADATA.md`. Called automatically by the Prototyper UI. Can also be run directly with explicit overrides.

## Usage

```bash
bash bin/merge.sh <spec-name>
bash bin/merge.sh <spec-name> --feature feature/<name>
bash bin/merge.sh <spec-name> --base main
bash bin/merge.sh <spec-name> --dry-run
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<spec-name>` | Specification directory name under `Specifications/` |
| `--feature <branch>` | Override feature branch (default: from `.env`) |
| `--base <branch>` | Override base branch (default: from `METADATA.md`) |
| `--dry-run` | Preview without merging |

## Reads

| File | Field |
|------|-------|
| `Specifications/<PROJECT>/.env` | `BUILD_FEATURE_BRANCH_NAME` |
| `Specifications/<PROJECT>/METADATA.md` | `base_branch` |

## Writes

| Output | Description |
|--------|-------------|
| Squash commit on base branch | All feature branch commits collapsed to one |
| Feature branch deleted | `git branch -d feature/<name>` |
| `METADATA.md status` | Updated to `ACTIVE` by merge.sh |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Configuration error or git failure |
