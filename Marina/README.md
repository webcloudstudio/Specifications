# Marina

A local-first control plane for agentic developers, with a private 24×7 AWS broadcast surface.

## Intent

Marina organizes a developer's local and downloaded git projects, applies a small set of standards,
catalogs their capabilities, and gives the owner observability and command-and-control over them.
Operations that act on local processes, disk, and logs stay on the developer's machine. The read-mostly
state worth sharing — the **capability catalog, project metadata, and last-known health** — can be
published to pay-per-call AWS services so it is reachable 24×7 by a private circle of trust, with **no
public inbound** anywhere.

Marina is the successor to the GAME prototype, built from the start around the two-plane hybrid analysed
in the prototyper project's Marina architecture notes.

## The Two Planes

- **Local control plane** — scanner, process engine, log ingestor, scheduler. Outbound-only; no listener
  on the public internet.
- **Cloud broadcast plane (this specification's focus)** — DynamoDB (catalog/state), API Gateway + Lambda
  (private IAM-authorised read/ingest), SQS (durable queue), S3 (blobs + company share). Accessed only
  through the `marina` client library, never raw boto3.

## Scope

This specification covers onboarding, project organization, conformance, capability exposure, and local
operations/monitoring. The AWS broadcast plane, durable ingest, and company share are integration
capabilities. Dockerization, Fargate, AgentCore, and Prototyper remain outside Marina's core scope.

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
bash ../prototyper/bin/validate.sh Marina
python3 ../prototyper/bin/build_spec_relationships.py Marina
bash ../prototyper/bin/oneshot.sh Marina        # or per-feature minimal builds in dependency order
```
