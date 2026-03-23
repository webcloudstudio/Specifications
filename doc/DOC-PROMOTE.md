# Step 6 — Promote

**Version:** 20260323 V4
**Description:** Squash-merge the prototype Feature Branch into the base branch

```bash
# cd to your prototype directory
git checkout <base_branch>
git merge --squash feature/<name>
git commit -m "Squash merge feature/<name>"
git branch -d feature/<name>
# push manually when ready
```
