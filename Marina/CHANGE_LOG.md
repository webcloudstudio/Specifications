# CHANGE_LOG.md — Marina

Append-only change log. Format: DATE | TYPE | SCOPE | DESCRIPTION
Types: CHANGE (pending), AC (permanent guardrail), DONE (applied — written by process script).
Scope: route path (/route), base filename (DATABASE.md), or spec filename (SCREEN-FOO.md).

2026-06-01 | CHANGE | /setup/aws | Cards should be collapsible: start expanded if status is not OK, start collapsed if status is OK; collapsed state must clearly indicate the item is OK
2026-06-01 | CHANGE | /setup/github | Same collapsible card behavior as /setup/aws: start expanded if not OK, start collapsed if OK, with clear OK state indicator
2026-06-01 | CHANGE | /setup/summary | Add editable text box for PROJECTS_DIR that saves the value on blur (tab out)
2026-06-01 | CHANGE | /setup/aws | Set default value for Marina Org field to 'Marina' (no additional AWS setup required for the org slug — it is a DynamoDB partition key only)
2026-06-01 | CHANGE | /setup/projects | Add text box for PROJECTS_DIR; validate that the directory exists on blur (tab out)
2026-06-01 | CHANGE | /setup/github | Success criteria is successfully fetching >= 1 repositories; test connectivity via both SSH and the gh CLI command
2026-06-01 | CHANGE | /setup/github | Page success (OK state) unlocks and enables navigation to /setup/repositories
2026-06-01 | CHANGE | /setup/summary | Remove the SCAN STATUS card — it has been moved to the new /setup/scan screen
2026-06-01 | CHANGE | /setup/scan | New screen (tab 5): SCAN STATUS content moved from /setup/summary; Scan button (previously Fetch on /setup/repositories) triggers POST /api/repositories/sync and refreshes the status card inline
2026-06-01 | CHANGE | /setup/repositories | Remove the Fetch/Refresh button — sync is now triggered exclusively from /setup/scan
2026-06-01 | CHANGE | /setup/repositories | Clicking the Repositories sub-tab must reload/refresh the repo list
2026-06-01 | CHANGE | /setup/repositories | Remove the 'Back to my repos' banner button when viewing another user's repos
2026-06-01 | CHANGE | /setup/repositories | Add On Disk marker: show a small disk icon on rows where the repo is present locally; no icon otherwise
2026-06-01 | CHANGE | /setup/repositories | Remove the description sub-line from each repo row to reduce row height
2026-06-01 | CHANGE | /setup/repositories | Replace disk icon action with a Download button for repos not yet on disk; do not show Download if the repo is already in PROJECTS_DIR — always show Open (small)
2026-06-01 | CHANGE | /setup/repositories | Open button must open the GitHub repo URL in a new browser tab
2026-06-01 | CHANGE | /setup/repositories | Buttons must be colorful and stylized; rows must be compact and not tall — use small pill-style buttons with icons
2026-06-01 | CHANGE | /setup/projects | Show the projects setup page as a single compact line in the dashboard; use icons
2026-06-01 | DONE   | /setup/aws | Applied via iterate a4c990d
