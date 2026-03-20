# Intent

## Who

Technical product owners managing multiple AI-assisted prototypes.

## Problem

Each prototype is an island. No unified view of what exists, what's running, what's healthy. Starting, stopping, monitoring, and documenting projects requires manual context-switching between terminals, browsers, and file managers.

## Solution

A single dashboard that auto-discovers projects from the filesystem. Projects conform to minimal standards (METADATA.md, script headers) and the platform provides operations, monitoring, documentation, and workflow management in return. The core principle is **contract-earns-capability**: add a file, gain a feature.

## Scope

- **In scope**: Project discovery, operations (run/stop scripts), process logging, health monitoring, portfolio publishing, ticketing/workflow, configuration editing, self-documentation.
- **Out of scope**: Code editing, deployment to cloud, CI/CD pipelines, multi-user auth.

## Tagline

**Rapid Project Development** — from idea to running prototype in one command.
