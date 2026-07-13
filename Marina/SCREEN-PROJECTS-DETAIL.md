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
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-REGISTRATION.md, FEATURE-PROJECT-ORGANIZATION.md, FEATURE-SERVICE-CATALOG.md, FEATURE-CAPABILITY-DISCOVERY.md |
| Provides | GET /projects/{id} |

## Layout

Header identity and registration summary, followed by tabs: Overview, Organization, Capabilities, Git,
Discovery Warnings, and Activity. Operations may be listed but are not runnable in the initial build.

## Overview

Show display name, repository path, source type, originating/current remote, remote owner/name, current
and default branch, HEAD commit/subject, author, working-tree status, ahead/behind counts, lifecycle
status, declared author, declared owner, namespace, tags, stack, health, registration state, and last
discovery time. Show declared author/owner separately from the latest Git commit author.

## Capabilities

List discovered services, data resources, shared resources, endpoints, links, operations, and MCP tools
from the service catalog. Each record shows stable key, source path/locator, parsed fields, validity,
content hash, first/last seen, and discovery run. Provide an evidence viewer and rediscovery action.

## Git and Discovery

Show raw and normalized repository identity, metadata fields, git evidence, scanner version, scan history,
warnings, and added/removed/changed capability records.

## Operations and Activity

Activity combines registration, organization changes, discovery changes, and warnings in reverse
chronological order. Run, Schedule, Publish, and Exposure actions are deferred from the initial build.

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Edit organization | Field/tag/namespace change | Update project organization and dashboard filters |
| Register candidate | Registration action | Persist the project projection after user confirmation |
| Rediscover | Button click | Rescan repository and refresh metadata/capabilities |
| Open evidence | Capability or field action | Show source file, locator, and parsed value |
| Resolve warning | Warning action | Open the source location or registration/configuration field |

## Open Questions

- None.
