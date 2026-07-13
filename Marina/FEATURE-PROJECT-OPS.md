# Feature: Project Operations (Deferred Adapter)

| Field | Value |
|-------|-------|
| Version | 20260713 V1 |
| Description | Optional adapter contract for exposing an external standards tool through Marina's controlled runner. |
| Status | DEFERRED; not part of Marina's core product scope |
| Depends On | FEATURE-BATCH-RUNNER.md, FEATURE-PROJECT-ORGANIZATION.md |
| Provides | — |

**Description:** Marina's active conformance model is standards-adapter neutral and is specified by
`SCREEN-PROJECTS-VALIDATION.md`. An external project tool may later be integrated as one adapter, but
Marina does not require, install, or model that tool as a product dependency.

## Deferred Contract

If enabled in a later phase, the adapter must:

1. Expose only named, allow-listed operations.
2. Run locally through the controlled batch runner.
3. Restrict all paths to registered project repositories.
4. Capture output, exit status, and duration in the normal run log.
5. Report validation results through the standard project event and conformance records.

## Reads

- Registered project path and selected standards profile.
- Adapter configuration.

## Writes

- Normal run state, logs, conformance results, and project events.
- No cloud execution and no unrestricted command or path input.

## Open Questions

- None.
