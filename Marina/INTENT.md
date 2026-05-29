# Intent

Important: This file contains the highest-level objectives of Marina. Features must serve these.

## Purpose 1 — A Local-First Control Plane With a Private Cloud Surface

Marina helps an agentic developer manage many projects. Operations act on local processes, disk, and
logs and therefore stay on the developer's machine. The state worth sharing — the capability catalog,
project metadata, and last-known health — is broadcast to pay-per-call AWS services so a private circle
of trust can read it 24×7, even when the developer's machine is off.

The defining constraint: **no public inbound**. The local machine never opens a listener to the
internet; it makes only outbound, SigV4-signed calls to AWS. The only public surface is an
IAM-authorised API Gateway that no anonymous caller can reach. This protects the developer's home
network, which is otherwise vulnerable to inbound attack.

## Purpose 2 — Conform Projects So Their Capabilities Can Be Broadcast

Projects expose their surface area through annotations: `METADATA.md` identity, `bin/` CommandCenter
headers, and an `AGENTS.md` capability catalog. Marina aggregates these into a single catalog. The big
win is consistency — once a project is conformed, Marina can publish, observe, and (later) invoke it
without bespoke integration.

## Purpose 3 — Encapsulate the Cloud Behind One Library

Every cloud interaction goes through the `marina` Python library — never raw boto3 in project code. The
library is the swap layer: the backend (DynamoDB / SQS / S3 / API Gateway today) can change without any
consumer changing a line. This is a deliberate architectural bet against vendor lock-in and against
scattered, drifting integration code.

## Audience and Circle of Trust

The audience is a small private group — family, friends, or a small company. Identity is **AWS
Organization membership**: onboarding ingests a member's AWS account into the Org. The grouping unit is
"everyone in the private company"; finer gates are declared in the specifications.

**Capability access mirrors git-repo access.** If a member can use a project's repository, they may
invoke that project's capability. The authorisation signal is the member's repo access, recorded into an
Org-side access table at onboarding and checked at invoke time. Onboarding must be easy for
non-technical members who know little about AWS.

## Security Posture (non-negotiables)

- No public IP and no inbound listener on any member's local network.
- API Gateway authorised by IAM/SigV4 only; no anonymous access, no API keys, no WAF, no Secrets Manager.
- DynamoDB partitioned by organization; per-project access gated by the repo→capability mapping.
- Even voice capture originates from inside the firewall.
- No secrets in Terraform state or code; identity is the AWS principal.

## True Purpose

This is also the owner's portfolio work, authored to a Principal Cloud Architect standard. Specifications
favour simple delivery, encapsulation (so AWS can be swapped), and best practices throughout.
