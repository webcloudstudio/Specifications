# HOMEPAGE: Homepage

| Field       | Value |
|-------------|-------|
| Version     | 20260419 V1 |
| Description |  |

# Homepage

**Version:** 20260326.1
**Description:** Portfolio homepage branding, contact details, and bio content for the Publisher screen

## Branding

```
logo:              Ed Barlow
name:              Ed Barlow
copyright:         Web Cloud Studio — Ed Barlow
section_title:     My Projects
section_subtitle:
```

## Contact

```
email:      edward.m.barlow@gmail.com
phone:      (914) 837-4798
phone_e164: +19148374798
```

## Bio

**AI Assisted Developer**

My Methods can one shot small and mid sized projects with prebuilt technical guidance.
My Methods provide standards conformity:

- Workflow And Specification Based Design
- Scaled Automation and Monitoring
- Seamless Standard Conformity
- Metrics

**Principal Engineer/Director** at major hedge funds, investment banks, and startups

**Author, Speaker, Game Developer, Data Engineer**

## Feature Workflow

![Feature Workflow](/webcloudstudio/diagrams/v3-feature-workflow.png)

## Project Definition

![Project Definition](/webcloudstudio/diagrams/v3-project-definition.png)

## AI Workflow

![AI Workflow](/webcloudstudio/diagrams/v3-ai-workflow.png)

## Notes

- Site config is read from `GAME/config/site_config.md` (the project's own directory, not the Specifications repo). `HOMEPAGE.md` in the Specifications repo is the human-readable reference for branding values; `site_config.md` is the live editable source.
- Image paths are `base_path`-relative absolute paths (e.g., `/sitename/images/name.webp`), generated at build time by `homepage_build.py` using the `GITHUB_PAGES_BASE_URL` env var.

See `HOMEPAGE-PUBLISHER.md` for the full build specification.
