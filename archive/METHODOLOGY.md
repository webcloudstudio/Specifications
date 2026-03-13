# The Specification Methodology

**spec_v4 · 2026-03-11**

---

## What This Is

This is a way of writing specifications so that an AI agent can build or rebuild a
project from them — without the original developer present, without prior context, and
without guessing.

The key insight is that most project specs mix up two separate things:

- **What the product does** — the features, the user experience, what gets stored, what
  gets displayed
- **How it is built** — the language, the database, the framework, the deployment model

When these are mixed, the spec becomes outdated the moment a technology choice changes.
An AI session that reads it cannot tell whether a detail is a business requirement or an
implementation decision from two years ago.

This methodology keeps them separate.

---

## The Three Layers

### Layer 1: What the Product Does

This is the feature specification. Each feature gets its own document. The document
describes:

- What problem it solves
- What the user can do
- What data flows in and out
- Which other features it connects to
- What the project must provide to enable this feature (the contract)

No technology words. No framework names. No database schemas. A feature spec written
today should still describe the same product if the stack is replaced tomorrow.

### Layer 2: The Contract

This is the binding layer between what the product does and how it is built.

A contract is a plain text file that a project provides. The platform reads it. The
platform gains information about the project — what operations it supports, what its
metadata is, where it runs — without being told directly.

Contracts are files like `CLAUDE.md`, `git_homepage.md`, and the headers inside `bin/`
scripts. They are committed to git alongside the code they describe. An AI agent reading
a contract file can derive everything it needs to interact with that project correctly.

See **THE-CONTRACT.md** for the full list of contracts with examples.

### Layer 3: How It Is Built

This is the technical specification: stack choice, module structure, data models,
infrastructure. It answers "how" only. It must satisfy every contract declared in Layer 2.

When an AI builds the project, it reads Layer 1 to understand what to build, Layer 2 to
know what artifacts to produce, and uses Layer 3 as the implementation guide.

---

## Why AI Needs This Structure

An AI agent working on a project without this structure must infer intent from code.
That works for isolated changes. It breaks for anything that requires understanding *why*
a design decision was made, *what* the intended user experience is, or *which features
are not yet built*.

With this structure:

- **Feature specs** tell the agent what to build and what the user expects
- **Contracts** tell the agent what artifacts to produce (scripts, files, headers)
- **Technical specs** tell the agent which tools and patterns to use

An agent can be dropped into any feature ticket, read three documents, and produce
correct, consistent, platform-aware output.

---

## How Projects Earn Platform Capabilities

The platform (GAME) does not have a registration UI. Projects do not fill out forms.
Instead, a project earns capabilities by implementing contracts.

| A project provides... | The platform gives it... |
|----------------------|--------------------------|
| A `bin/start.sh` with a Name header | A "Start" button in the dashboard |
| A `git_homepage.md` with Show: true | A card on the portfolio site |
| A `CLAUDE.md` with endpoints | Clickable service links in the UI |
| A declared port in a bin/ header | Automatic health monitoring |
| Structured status messages in scripts | Live state tracking in the process monitor |

Nothing in this list requires changing the platform. A project adds the file; the
platform discovers the capability on the next scan.

---

## What the Specification Does Not Prescribe

- Which programming language is used
- Which database stores the data
- Which framework serves the UI
- Which cloud provider hosts the product
- Which AI model implements the features

These are Layer 3 decisions. They belong in the technical spec, not here.

---

## The Purpose of This Document Set

Every document in this spec_v4 directory answers exactly one question:

| Document | Question |
|----------|---------|
| METHODOLOGY.md (this file) | How does this specification work? |
| THE-CONTRACT.md | What must a project provide? |
| PERSISTENCE.md | How does a project store its own data? |
| OPERATIONS.md | What must operational scripts expose? |
| LOGGING.md | How do scripts produce observable output? |
| features/*.md | What does each platform feature do? |

An AI agent building any part of the platform should read METHODOLOGY.md first, then the
feature spec for the feature being built, then the contracts relevant to that feature.
