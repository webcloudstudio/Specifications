# BUILD_PLAN_INTENT.md — GAME
# Created by: bash bin/build_plan.sh GAME create
#
# Commands:
#   bash bin/build_plan.sh GAME verify   fix sizes, preview phases by priority
#   bash bin/build_plan.sh GAME run       validate ordering, write BUILD_PLAN.md
#
# Sizes in KB. Run verify to refresh them after editing spec files.
# Prefix a file line with # to skip it from the build.

## Foundation - Database
# instructions: Build the SQLite schema only from DATABASE.md with WAL mode and FK pragma. Do not create the Flask app or any routes yet.
DATABASE.md (31k)

## Foundation - Flask
# instructions: Create the Flask app factory (app/__init__.py), initialise SQLite from the existing schema, create bin/common.sh and bin/start.sh. Ensure the /health endpoint returns 200. Do not implement screens or features yet. Error handlers must not call render_template — return JSON only in this phase since the template layer does not exist yet. Do not create any HTML templates.
# stack: python, flask

## Database Github Repos 001
DATABASE-github-repos-001.md (2k)

## Service Catalog
FEATURE-SERVICE-CATALOG.md (12k)
FEATURE-SCANNER.md (4k)

## Default and Welcome Screens
SCREEN-DEFAULT.md (3k)
SCREEN-WELCOME-PROJECTS.md (1k)
SCREEN-WELCOME-PROTOTYPES.md (1k)
SCREEN-WELCOME-SUMMARY.md (6k)
FEATURE-Project-Download.md

## Catalog
SCREEN-CATALOG.md (9k)

## Projects Screens
SCREEN-PROJECTS-CONFIGURATION.md (1k)
SCREEN-PROJECTS-DASHBOARD.md (3k)
SCREEN-PROJECTS-DETAIL.md (4k)
SCREEN-PROJECTS-MAINTENANCE.md (1k)
SCREEN-PROJECTS-SETUP.md (5k)
SCREEN-PROJECTS-VALIDATION.md (4k)

## Settings Screens
SCREEN-SETTINGS-GENERAL.md (4k)
SCREEN-SETTINGS-HELP.md (2k)
SCREEN-SETTINGS-TAGS.md (5k)
SCREEN-HELP.md (3k)

## Prototypes Screens
SCREEN-PROTOTYPES-MAINTENANCE.md (3k)
SCREEN-PROTOTYPES-CONFIGURATION.md (2k)
SCREEN-PROTOTYPES-LIST.md (5k)
SCREEN-PROTOTYPES-VALIDATION.md (3k)

## Homepage Publisher
FEATURE-HOMEPAGE-PUBLISHER.md (11k)
HOMEPAGE.md (1k)

## Homepage UI
SCREEN-PUBLISHER.md (4k)

## Workflow Service
FEATURE-Workflow-Service.md (11k)

## Workflow UI
SCREEN-WORKFLOW-ADD-TICKET.md (1k)
SCREEN-WORKFLOW-MANAGE.md (1k)
SCREEN-WORKFLOW-WORKFLOW.md (2k)

## Mcp Hosting
FEATURE-MCP-Hosting.md (7k)

## Healthcheck
FEATURE-HEALTHCHECK.md (8k)

## Monitoring Screens
SCREEN-MONITORING-MONITORING.md (6k)
SCREEN-MONITORING-PROCESSES.md (2k)
SCREEN-MONITORING-SCHEDULER.md (4k)

## Batchrunner
## Cli Gateway
FEATURE-BatchRunner.md (6k)
FEATURE-CLI-GATEWAY.md (4k)

## Asyncqueue 
FEATURE-AsyncQueue.md (11k)
FEATURE-VOICEFORWARD.md (5k)

## Voiceforward
SCREEN-VOICEFORWARD-MOBILE.md (4k)
SCREEN-SETTINGS-VOICE-DOCS.md (6k)
SCREEN-SETTINGS-VOICE.md (4k)



## Welcome Github [NEW]
SCREEN-WELCOME-GITHUB.md (8k)

