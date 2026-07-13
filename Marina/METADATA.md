# Marina

A local-first developer control plane that broadcasts project state to a private, pay-per-call AWS plane.

name: Marina
display_name: Marina
short_description: A local-first developer control plane with a private 24x7 AWS broadcast surface for project catalog, capabilities, and state.
status: PROTOTYPE
type: oneshot
base_branch:
version: 2026-05-28.1
updated: 20260528
image_description: A single sailboat moored in a calm harbour at dawn, clean flat-vector style, deep navy and teal palette, lots of negative space — evoking many vessels safely docked within one managed perimeter.
stack: Python/aws-dynamodb/aws-lambda/aws-api-gateway/aws-sqs/aws-s3/terraform/github-actions/marina-library
tags: framework, cloud, control-plane, aws
namespace: development
desired_state: on-demand
specification_directory: ../Specifications

## Agent Instructions

When working on this specification, add unresolved questions to the `## Open Questions` section at the bottom of the relevant specification file. Marina is built in minimal, dependency-ordered phases. The initial build is the local welcome/registration, capability discovery/storage, and Project Explorer slices. Invocation, exposure, cloud publication, Dockerization/Fargate, and AgentCore are later phases.
