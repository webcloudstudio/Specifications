# Screen: Projects — Detail

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Route | `GET /projects/{id}` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | — |
| Tab Order | — |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Project identity, organization, capabilities, standards, and operations. |
| Description | Single-project command surface for the project's metadata, grouping, conformance, exposed capabilities, workflow, and activity. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-ORGANIZATION.md, FEATURE-SERVICE-CATALOG.md, FEATURE-BATCH-RUNNER.md |
| Provides | GET /projects/{id} |

## Layout

Header identity and health summary, followed by tabs: Overview, Organization, Capabilities, Standards,
Workflow, Operations, and Activity.

## Overview

Show display name, repository path/remote/branch, lifecycle status, namespace, tags, stack, health,
conformance state, and last activity. Provide links to the repository, documentation, logs, and
Monitoring.

## Capabilities

List discovered services, data resources, shared resources, endpoints, links, and operations from the
service catalog. Each capability shows its source, standard status, and exposure state. Provide explicit
actions to expose or hide a capability.

## Standards

Show the selected standard profile, checks, latest result, exceptions, and validation history. A failed
check blocks the Conformed state and explains the remediation.

## Operations and Activity

Operations are allow-listed service-catalog entries with Run, Schedule, and View Log actions. Activity
combines organization changes, validation results, runs, health changes, publish events, and alerts in
reverse chronological order.

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Edit organization | Field/tag/namespace change | Update project organization and dashboard filters |
| Validate | Button click | Run the configured standard profile and refresh result |
| Expose capability | Explicit toggle | Persist visibility after confirmation and audit the change |
| Run operation | Operation button | Start controlled run; link to `/monitoring/processes?run_id={run_id}` |
| Create ticket | Workflow action | Create project-scoped ticket |
| Publish | Catalog action | Publish only explicitly exposed capabilities and project metadata |

## Open Questions

- None.
