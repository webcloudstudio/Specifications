# Marina

A local-first control plane for agentic developers, with a private 24×7 AWS broadcast surface.

## Intent

Marina conforms a developer's projects to a small set of standards, then gives the owner observability
and command-and-control over them. Operations that act on local processes, disk, and logs stay on the
developer's machine. The read-mostly state worth sharing — the **capability catalog, project metadata,
and last-known health** — is published to pay-per-call AWS services so it is reachable 24×7 by a private
circle of trust, with **no public inbound** anywhere.

Marina is the successor to the GAME prototype, built from the start around the two-plane hybrid analysed
in `Prototyper/docs/marina-aws.md`.

## The Two Planes

- **Local control plane** — scanner, process engine, log ingestor, scheduler. Outbound-only; no listener
  on the public internet.
- **Cloud broadcast plane (this specification's focus)** — DynamoDB (catalog/state), API Gateway + Lambda
  (private IAM-authorised read/ingest), SQS (durable queue), S3 (blobs + company share). Accessed only
  through the `marina` client library, never raw boto3.

## Scope

This specification covers **Phase 1** (read/ingest/report surface) and **Phase 2** (durable ingest and
company share). Phase 3 (Dockerization / Fargate) and later phases (AgentCore, browser UI) are documented
as deferred in `IDEAS.md`.

## Specification Map

| Document | Answers |
|----------|---------|
| `INTENT.md` | Goals, audience, security posture |
| `ARCHITECTURE.md` | Two planes, the `marina` library, Terraform layout, directory structure |
| `DATABASE.md` | DynamoDB single-table hierarchical schema and access patterns |
| `FUNCTIONALITY.md` | Index of features by phase |
| `FEATURE-*.md` | Per-feature: trigger, sequence, reads/writes, and a callable test |
| `AGENTS.md` | Endpoints and capability catalog |
| `IDEAS.md` | Deferred phases and spikes |

## Building From This Specification

```bash
bash ../Prototyper/bin/validate.sh Marina
python3 ../Prototyper/bin/build_spec_relationships.py Marina
bash ../Prototyper/bin/oneshot.sh Marina        # or per-feature minimal builds in dependency order
```
