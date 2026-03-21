# Promote / Merge

**Version:** 20260321 V3
**Description:** Merge a Feature Branch (Prototype) into the base branch

A **Prototype** is a Project on a Feature Branch. Once tested, `merge.sh` squash-merges it
into the base branch and deletes the feature branch. No git commands visible to the user —
GAME triggers this automatically via UI.

---

## What Happens

```
Prototype (feature/name)  →  merge.sh  →  Project (base branch)
```

1. `git checkout <base_branch>` in `../<ProjectName>/`
2. `git merge --squash feature/<name>`
3. `git commit` with message referencing the spec tag
4. `git branch -d feature/<name>`
5. Prints: `Merged to <base_branch> — push when ready`

Does **not** push. Use GAME or push manually.

---

## Direct Usage

```bash
# GAME calls this automatically. Direct usage:
bash bin/merge.sh <spec-name>
bash bin/merge.sh <spec-name> --feature feature/my-name --base main
bash bin/merge.sh <spec-name> --dry-run
```

| Arg | Effect |
|-----|--------|
| `--feature <branch>` | Override feature branch (default: reads `.env`) |
| `--base <branch>` | Override base branch (default: reads `METADATA.md` or auto-detects) |
| `--dry-run` | Preview without merging |

---

## Prerequisites

| Requirement | Where |
|-------------|-------|
| `BUILD_FEATURE_BRANCH_NAME=feature/name` | `Specifications/<Name>/.env` |
| `base_branch: main` | `Specifications/<Name>/METADATA.md` (or auto-detected) |
| `git_repo:` set | `Specifications/<Name>/METADATA.md` |
| Feature branch exists in `../<Name>/` | Created by `bin/build.sh` |

---

## After Merge

```bash
# Push to remote (via GAME or directly):
git -C ../<ProjectName> push

# Validate compliance:
bash bin/ProjectValidate.sh <ProjectName>
```
