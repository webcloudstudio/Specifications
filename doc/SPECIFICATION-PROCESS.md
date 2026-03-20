# Specification Process

Write concise specs. Expand them. Build the application. Each step has one command.

1. `bash bin/create_spec.sh MyProject "Short description"` — creates `Specifications/MyProject/` with template files
2. Edit the spec files in `MyProject/` — fill in INTENT.md, ARCHITECTURE.md, add SCREEN and FEATURE files as needed. Delete DATABASE.md or UI.md if not applicable.
3. `bash bin/validate.sh MyProject` — checks required files, naming, fields. Exit 0 = ready.
4. `bash bin/convert.sh MyProject > convert-prompt.md` — generates expansion prompt. Feed to an AI agent to produce detailed specs.
5. `bash bin/build.sh MyProject > build-prompt.md` — tags the commit, generates a complete build prompt. Feed to an AI agent to build the application.
6. Promote: copy the spec directory to its own repo when the application works.

After a build, iterate: edit specs, re-validate, re-build. Each build creates a new annotated git tag (`build/MyProject/2026-03-20.1`) that permanently records the exact spec state used.

```bash
# Diff specs between builds
git diff build/MyProject/2026-03-19.1..build/MyProject/2026-03-20.1 -- MyProject/
```
