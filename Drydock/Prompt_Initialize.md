# Lay the Keel: Initialize Drydock

Build the first executable foundation of Drydock in a new target directory by porting the proven
initialization, validation, and governance behavior from the existing Prototyper repository.

This is a clean-room target build. Treat Prototyper as a read-only behavioral reference and seed
source. Do not modify, move, rename, or delete any Prototyper or Specifications repository files.
The target directory may be deleted and rebuilt repeatedly during testing.

The Drydock product contract is defined by the current Drydock Specification and
`docs/whitepapers/drydock.md` in Prototyper. Where the contract and legacy implementation differ,
follow the Drydock contract. Record unresolved conflicts rather than silently preserving legacy
behavior.

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
drydock rigging update <Target>
drydock rigging verify <Target>
```

All other documented Drydock command paths must be present in help and return a clear,
non-traceback message such as `drydock plan create: not implemented`, with exit code `2`.

The initial build deliberately excludes planning engines, build execution, LLM calls, databases,
the Console, import translation, scoring, documentation generation, and rigging compaction.

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
| Hashing and rigging manifest | `hashlib` |
| Dates | `datetime` |
| Process invocation, only where later adapters require it | `subprocess` |
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

Never modify `PROTOTYPER_SOURCE`.

Never copy Prototyper's `.git/`, generated documentation, logs, execution data, caches, virtual
environments, backup files, or legacy Bash command implementations into Drydock.

Use these source mappings:

| Prototyper source | Drydock target |
|---|---|
| `RulesEngine/BUSINESS_RULES.md` | `Rigging/BUSINESS_RULES.md` |
| `RulesEngine/SPECIFICATION_CONTRACT.md` | `Rigging/SPECIFICATION_CONTRACT.md` |
| `RulesEngine/stack/` | `Rigging/stack/` |
| `RulesEngine/spec_template/` | `Rigging/specification_templates/` |
| `RulesEngine/templates/` | `Rigging/project_templates/` |
| Relevant reusable prompt files | `prompts/` |

Do not mechanically copy `RulesEngine/CLAUDE_RULES.md`; it is a generated Prototyper artifact.
Preserve other useful governance or branding files only when they are actively referenced by the
new Drydock repository.

Within newly created Drydock files, use `Rigging` terminology and paths. Do not create new
`RulesEngine` references. If copied seed content contains historical `RulesEngine` references,
change only references that are required for the new Drydock paths to function; report remaining
terminology debt.

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
      rigging.py
      stubs.py
  Rigging/
    BUSINESS_RULES.md
    SPECIFICATION_CONTRACT.md
    stack/
    specification_templates/
    project_templates/
  prompts/
  tests/
    conftest.py
    test_cli.py
    test_config.py
    test_init_specification.py
    test_validate_specification.py
    test_rigging.py
```

Keep responsibilities narrow. CLI parsing dispatches to application functions; it does not contain
filesystem or validation logic.

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
`Rigging/specification_templates/`.

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

Seed templates from Prototyper, but conform their names and content to the current Drydock Typed
Specification contract before treating them as the Drydock templates.

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
- Declared stack components have matching `Rigging/stack/<component>.md` files.
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

## Rigging Contract

Implement the non-LLM portion of Drydock Rigging.

### `drydock rigging update <Target>`

- Resolve `<Target>` as a name relative to configured `target_directory`.
- Require the target project directory to exist.
- Copy the current Drydock project templates and the compact/business-rules artifact selected by
  the current Drydock contract into the target project.
- Never overwrite target-owned files unless the Rigging contract explicitly identifies them as
  managed files.
- Write a deterministic managed-file manifest containing relative path and SHA-256 hash.
- Make repeated runs idempotent.
- Report copied, updated, unchanged, and skipped files.

If the current approved contract does not yet unambiguously define the generated compact business
rules artifact, install `Rigging/BUSINESS_RULES.md` as the temporary managed source and record that
choice in README and command output. Do not invent compaction behavior.

### `drydock rigging verify <Target>`

- Read the managed-file manifest.
- Verify required managed files exist and hashes match.
- Report missing, modified, and valid files.
- Exit `0` when compliant and `1` when not compliant.
- Do not modify the target.

### Deferred Rigging Command

Register `drydock rigging compact <Spec>`, but return the standard not-implemented response and exit
code `2`.

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
drydock document <Spec> <Target>
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
8. Run `drydock rigging update ExampleTarget` twice and confirm the second run is idempotent.
9. Modify a managed target file and confirm `drydock rigging verify ExampleTarget` fails.
10. Run representative deferred commands and confirm exit code `2` with no filesystem changes.
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
- `config`, `init`, `validate`, `rigging update`, and `rigging verify` are real Python
  implementations.
- Deferred commands are visible, parse correctly, fail safely, and do not write.
- Bash and PowerShell wrappers contain no business logic.
- No `.bat` interface exists.
- Tests and Ruff checks pass.
- README documents installation, the working command subset, deferred commands, configuration
  locations, source-tree launchers, and the temporary business-rules propagation decision if used.
- The implementation reports any contract conflicts or terminology debt discovered during the port.

Do not proceed into planning, build execution, agent-provider integration, persistence, or Console
implementation. This step lays the keel; later steps build on this verified foundation.
