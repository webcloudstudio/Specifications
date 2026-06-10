# Lay the Keel: Initialize Drydock

Build the first executable foundation of Drydock in a new target directory by porting the proven
initialization, validation, and governance behavior from the existing Prototyper repository.

This is a clean-room target build. Treat Prototyper as a read-only behavioral reference and seed
source. Do not modify, move, rename, or delete any Prototyper or Specifications repository files.
The target directory may be deleted and rebuilt repeatedly during testing.

At build time, the current Drydock build specification will be available as
`<SPECIFICATION_DIRECTORY>/Drydock/drydock.md`. Use this precedence when sources differ:

1. This `Prompt_Initialize.md` controls the scope and acceptance criteria for Lay the Keel.
2. `Drydock/drydock.md` is the current Drydock product and behavior contract.
3. Prototyper is the read-only behavioral reference and seed source.

Record unresolved conflicts rather than silently preserving legacy behavior.

## Build Objective

At completion, Drydock is an installable cross-platform Python CLI and the following commands work
without calling Bash, PowerShell, or legacy Prototyper scripts:

```text
drydock --help
drydock --version
drydock config show
drydock config set specification_directory <path>
drydock config set target_directory <path>
drydock init <Spec>
drydock init <Spec> --update
drydock init <Spec> --force
drydock validate <Spec>
drydock validate <Spec> --verbose
```

All other documented Drydock command paths must be present in help and return a clear,
non-traceback message such as `drydock plan create: not implemented`, with exit code `2`.

The initial build deliberately excludes planning engines, build execution, LLM calls, databases,
the QuarterDeck, import translation, scoring, documentation generation, rigging compaction, and
propagation of Rigging into target projects.

## Implementation Decisions

Use Python `>=3.11`.

Use a standard-library-first implementation:

| Concern | Library |
|---|---|
| CLI parsing and nested commands | `argparse` |
| Paths and cross-platform filesystem behavior | `pathlib` |
| File copying and directory operations | `shutil` |
| Configuration serialization | `json` |
| Typed internal contracts | `dataclasses`, `enum`, and type hints |
| Logging | `logging` |
| Packaged resource access | `importlib.resources` |
| Dates | `datetime` |
| OS-appropriate global configuration directory | `platformdirs` |
| Tests | `pytest` |
| Linting and formatting | `ruff` |
| Python package build backend | `hatchling` |

Do not add Typer, Click, Rich, Pydantic, a database, an ORM, a dependency-injection framework, or
an application framework in this step. The foundation does not need them.

Install the CLI through this Python console entry point:

```toml
[project.scripts]
drydock = "drydock.cli:main"
```

The installed console entry point is the authoritative interface on every platform. Python package
installation creates the appropriate Windows `drydock.exe` launcher, so do not maintain a `.bat`
implementation.

`drydock --version` and the root `drydock --help` output must print:

```text
Copyright (c) 2026 Web Cloud Studio. All rights reserved.
```

Do not print the copyright notice during every normal subcommand invocation.

Also provide thin source-tree convenience launchers:

```text
bin/drydock.sh
bin/drydock.ps1
```

Both launchers only locate the repository and execute `python -m drydock`. They contain no command
logic and must produce the same behavior as the installed `drydock` command.

## Source And Target Rules

Before writing, identify:

- `PROTOTYPER_SOURCE`: the existing Prototyper repository containing `RulesEngine/`, `prompts/`,
  and the legacy `bin/` implementations.
- `DRYDOCK_TARGET`: the new target software repository being built.

Fail before writing if both resolve to the same directory.

Never modify `PROTOTYPER_SOURCE`. The agent has full read access to `PROTOTYPER_SOURCE` — read any
`bin/`, `RulesEngine/`, or `prompts/` file needed to understand the behavior being ported.

Never copy Prototyper's `.git/`, generated documentation, logs, execution data, caches, virtual
environments, backup files, or legacy Bash command implementations into Drydock.

Copy the complete Prototyper `RulesEngine/` directory into Drydock as `Rigging/`. Preserve its
complete directory structure and current contents. This includes all current files under:

```text
RulesEngine/*              -> Rigging/*
RulesEngine/spec_template/ -> Rigging/spec_template/
RulesEngine/stack/         -> Rigging/stack/
RulesEngine/templates/     -> Rigging/templates/
```

The copied Rigging is an intentional seed snapshot. Include generated and compact RulesEngine
artifacts that are already present, including `CLAUDE_RULES.md`, `CLAUDE_RULES_compact.md`, and
existing `_compact.md` stack files. Later Drydock workflows may change how these are generated.

Within newly created Drydock files, use `Rigging` terminology and paths. Do not create new
`RulesEngine` references. If copied seed content contains historical `RulesEngine` references,
change only references that are required for the new Drydock paths to function; report remaining
terminology debt.

Do not copy Prototyper prompts during Lay the Keel. Create `prompts/README.md` explaining that
prompts will be ported with the commands that consume them.

The root-level `Rigging/` directory is the human-editable source of truth. The installed Python
package must also contain a synchronized read-only copy at `drydock/resources/Rigging/` so
`drydock init` and `drydock validate` work from an installed wheel outside the source checkout.
Configure Hatchling to include the root `Rigging/` tree at that package-resource destination.

Implement one Rigging resource resolver:

1. During source-tree execution, use the root-level `Rigging/` directory.
2. During installed-package execution, use `importlib.resources` to read
   `drydock/resources/Rigging/`.

The same `init` and `validate` code must use this resolver; do not duplicate command logic.

## Required Repository Layout

Create this minimum structure:

```text
DRYDOCK_TARGET/
  AGENTS.md
  METADATA.md
  README.md
  LICENSE
  pyproject.toml
  .gitignore
  .env.sample
  bin/
    drydock.sh
    drydock.ps1
    test.sh
  src/
    drydock/
      __init__.py
      __main__.py
      cli.py
      errors.py
      config.py
      paths.py
      metadata.py
      init_specification.py
      validate_specification.py
      stubs.py
      resources/
        Rigging/
  Rigging/
    # Complete seeded copy of Prototyper RulesEngine/
    spec_template/
    stack/
    templates/
  prompts/
    README.md
  tests/
    conftest.py
    test_cli.py
    test_config.py
    test_init_specification.py
    test_validate_specification.py
```

Keep responsibilities narrow. CLI parsing dispatches to application functions; it does not contain
filesystem or validation logic.

`bin/test.sh` contains no business logic. Its sole purpose is to activate the project virtual
environment and run `python -m pytest`. It is the canonical test entry point for platform tooling.

## License Contract

Create `LICENSE` with this exact proprietary license:

```text
Copyright (c) 2026 Web Cloud Studio. All rights reserved.

This software and its associated documentation are proprietary and confidential property of
Web Cloud Studio.

No part of this software or documentation may be copied, reproduced, modified, distributed,
published, transmitted, sublicensed, sold, used, or otherwise exploited, in whole or in part,
without prior explicit written permission from Web Cloud Studio.

Possession of a copy does not grant any license or right to use the software or documentation.
Unauthorized use is strictly prohibited.
```

Set the Python project license metadata to proprietary and include `LICENSE` in source and wheel
distributions. Do not substitute an open-source license.

## Configuration Contract

`drydock config` manages exactly two required global values:

```text
specification_directory
target_directory
```

Persist them as JSON under the user-specific configuration directory returned by:

```python
platformdirs.user_config_path("drydock", appauthor=False)
```

Use a file named `config.json`.

Resolution precedence:

1. Environment variables `SPECIFICATION_DIRECTORY` and `TARGET_DIRECTORY`.
2. Values in global `config.json`.
3. No implicit directory guesses.

Do not read or write `.env` files for global Drydock configuration.

Requirements:

- Store normalized absolute paths.
- Expand `~`.
- `config set` requires an existing directory.
- `config show` prints each effective value and its source.
- Commands fail with an actionable message when a required path is not configured.
- Tests isolate configuration from the real user profile.

## Specification Initialization Contract

Port the useful deterministic behavior of Prototyper `bin/setup.sh` into Python.

`drydock init <Spec>` creates `<specification_directory>/<Spec>/` from
the packaged `Rigging/spec_template/` resource.

Requirements:

- Reject unsafe names and path traversal. `<Spec>` is a name relative to the configured
  specification root, not an arbitrary path.
- Create the directory when absent.
- Refuse to overwrite an existing directory by default.
- `--update` copies only missing template files.
- `--force` overwrites template-managed files.
- Replace template tokens including project display name, project slug, short-description
  placeholder, current ISO date, and compact date.
- Derive a readable display name deterministically from hyphens and underscores.
- Use UTF-8 and platform-independent line handling.
- Print created, updated, and skipped files.
- Return `0` on success and `1` on invalid input or filesystem failure.
- Never invoke an LLM and do not implement legacy `--analyze` in this step.

For Lay the Keel, preserve and use the current Prototyper `RulesEngine/spec_template/` file set:

```text
ACCEPTANCE_CRITERIA.md
ARCHITECTURE.md
DATABASE.md
FEATURE-Example.md
HOMEPAGE.md
IDEAS.md
INTENT.md
METADATA.md
README.md
SCREEN-Example.md
UI-Component-Example.md
UI.md
```

Do not rename, remove, or redesign these templates during Lay the Keel. They may iterate after the
initial Drydock framework is operational.

## Specification Validation Contract

Port the deterministic, generally applicable checks from Prototyper `bin/validate.sh` into Python.

At minimum validate:

- Specification directory exists.
- Required files from the current Drydock contract exist.
- Required `METADATA.md` fields exist and have valid values.
- `METADATA.md` name matches the requested Specification name.
- Specification filenames follow the current Typed Specification contract.
- Required terminal sections exist where the current contract requires them.
- Example template files produce warnings.
- Declared stack components have matching packaged `Rigging/stack/<component>.md` files.
- Generated/process artifacts are distinguished from authored files.

Output requirements:

- Group findings by section.
- Distinguish `PASS`, `WARN`, and `FAIL`.
- Default output shows warnings and failures; `--verbose` also shows passes.
- Print a final deterministic summary.
- Exit `0` when there are no failures, including when warnings exist.
- Exit `1` when any failure exists.
- Do not inspect or validate a target application in this step.

Represent findings using a typed Python model rather than printing directly from each rule.

Running `drydock validate` immediately after `drydock init` is a valid and expected workflow. All
template-seeded files are present; unedited stubs produce warnings, not failures. The output shows
which files have been authored and which remain as unedited templates — this is the intended
incremental use pattern, not an error condition.

## Rigging Seed Contract

Lay the Keel creates Drydock's own Rigging by copying the complete Prototyper `RulesEngine/` tree as
defined above. It does not propagate files from Drydock Rigging into target projects.

Register `drydock rigging compact <Spec>`, `drydock rigging update <Target>`, and
`drydock rigging verify <Target>`, but return the standard not-implemented response and exit code
`2`. Target-project propagation and verification will be implemented only after their managed-file
contract is defined.

## Deferred Command Surface

Register these documented command paths so help exposes the intended Drydock interface:

```text
drydock plan init <Spec>
drydock plan create <Spec>
drydock plan show <Spec>
drydock build <Spec> <Target>
drydock build status <Spec> <Target>
drydock build score <Spec> <Target>
drydock iterate <Spec> <Target> [BOTH|SPEC|TGT] <Scope> <Change>
drydock import <Spec> <Target> --format <auto|source|speckit>
drydock analyze <Spec> [<Target>]
drydock rigging compact <Spec>
drydock rigging update <Target>
drydock rigging verify <Target>
drydock document <Spec> <Target>
drydock document generate <Spec> <Target>
drydock document assemble <Spec> <Target>
```

Every deferred command must:

- Parse its documented arguments.
- Return one concise `not implemented` message.
- Exit with code `2`.
- Never create or modify files.
- Never call a legacy Prototyper script.

## Error And Output Contract

- Expected user errors print a concise message without a traceback.
- Unexpected internal errors may show a traceback only when `--debug` is supplied.
- Use stdout for successful command results and stderr for errors.
- Use exit code `0` for success, `1` for validation/operational failure, and `2` for usage errors or
  intentionally deferred commands.
- No command may silently fall back to Prototyper.

## Testing And Verification

Write tests before considering the foundation complete.

Tests must use temporary directories and must not modify the real Prototyper, Specifications, target
projects, or user configuration.

Required verification:

1. Install the package in an isolated environment.
2. Run `drydock --help` and confirm every documented top-level command appears.
3. Set temporary specification and target roots using `drydock config set`.
4. Run `drydock init ExampleProject`.
5. Run `drydock validate ExampleProject`.
6. Run `drydock init ExampleProject --update` and confirm it is non-destructive.
7. Modify a template-managed test file, run `--force`, and confirm overwrite behavior.
8. Build and install a wheel, change outside the source checkout, and confirm `drydock init` and
   `drydock validate` can read the packaged Rigging resources.
9. Confirm root `drydock --help` and `drydock --version` show the copyright notice.
10. Run representative deferred commands, including all three `rigging` commands and all three
    `document` forms, and confirm exit code `2` with no filesystem changes.
11. Run the full test suite and Ruff checks.
12. Confirm `bin/drydock.sh`, `bin/drydock.ps1`, `python -m drydock`, and the installed `drydock`
    entry point dispatch to the same Python CLI.

Minimum acceptance commands:

```bash
python -m pytest
ruff check .
ruff format --check .
drydock --help
drydock config show
```

PowerShell behavior may be verified structurally when PowerShell is unavailable in the build
environment; state that limitation explicitly.

## Completion Requirements

The build is complete only when:

- A fresh target directory can be built from this prompt without modifying Prototyper.
- The Python package installs and the `drydock` command works.
- `config`, `init`, and `validate` are real Python implementations.
- The complete Prototyper `RulesEngine/` tree is present as Drydock `Rigging/`, and installed wheels
  contain synchronized packaged Rigging resources.
- Deferred commands are visible, parse correctly, fail safely, and do not write.
- Bash and PowerShell wrappers contain no business logic.
- No `.bat` interface exists.
- The proprietary Web Cloud Studio license is present and packaged.
- Tests and Ruff checks pass.
- README documents installation, the working command subset, deferred commands, configuration
  locations, source-tree launchers, packaged Rigging behavior, and proprietary license.
- The implementation reports any contract conflicts or terminology debt discovered during the port.

Do not proceed into planning, build execution, agent-provider integration, persistence, or Console
implementation. This step lays the keel; later steps build on this verified foundation.
