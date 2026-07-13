To properly test Specification-Driven Development (SDD), the specification needs to be broad enough to encompass server states, multi-layered operations, UI rendering constraints, and edge-case exceptions.
A highly detailed, production-grade English Markdown Functional Specification for a multi-layered application is outlined below, followed by open-source repositories that utilize pure English specifications for their system builds.
------------------------------
## Functional Specification: Secure Team Inventory Matrix (STIM)## 1. Product Overview & Architecture
STIM is a lightweight, self-contained web application used to track company hardware inventory across multiple corporate teams.

* Architecture: The application must run as a local HTTP Web Server. It serves a dynamic HTML/CSS frontend to the browser and manages data strictly server-side.
* Persistency: All state must be persisted in a flat JSON file named inventory.json. It must initialize an empty array [] if the file does not exist at startup.
* Zero-Dependency Core: The backend must only use standard libraries or fundamental routing packages (e.g., standard libraries or native frameworks in Python, Node.js, or Go). No external database engines or heavyweight ORMs are permitted.

------------------------------
## 2. Global State & Data Models
The inventory.json file must contain an array of objects matching this exact conceptual data model:

| Field Name | Type | Validation Rules | Description |
|---|---|---|---|
| id | String | Format: INV- followed by 4 sequential digits (e.g., INV-0001). | Generated automatically by the server. |
| assetName | String | Length: 3 to 50 characters. Alphanumeric, spaces, and hyphens only. | The name of the item (e.g., "MacBook Pro"). |
| team | String | Must match exactly one: Engineering, Design, or Operations. | Assignee department. |
| assignedTo | String | A valid email address structure (user@domain.com). | Employee holding the asset. |
| status | String | Must match exactly one: In Use or In Storage. | Operational state. |
| lastInspected | String | Date format: YYYY-MM-DD. Cannot be a future date. | Date the hardware was verified. |

------------------------------
## 3. HTTP REST API Specifications
The backend web server must expose a clean JSON API. All payload requests/responses must use the header Content-Type: application/json.
## GET /api/assets

* Purpose: Retrieves all inventory items.
* Query Parameters: Supports an optional filter ?team=Name (e.g., /api/assets?team=Engineering).
* Behavior: If the team filter is active, return only matching items. If empty, return all items. Sort the final list chronologically by lastInspected (oldest date first).
* Success Output: 200 OK with a JSON array of asset objects. [1] 

## POST /api/assets

* Purpose: Registers a new piece of hardware.
* Payload Constraints: Expects a JSON body containing assetName, team, assignedTo, status, and lastInspected. The server must auto-generate the sequential id.
* Failure Modes:
* If validation fails for any field, return 400 Bad Request with payload: {"error": "Validation failed: [Reason]"}.
   * If an asset with the exact same assetName AND assignedTo email already exists, return 409 Conflict with payload: {"error": "Duplicate asset assignment prohibited."}.
* Success Output: 201 Created with the fully generated asset object.

## DELETE /api/assets/:id

* Purpose: Deletes a hardware record via URL path parameters.
* Behavior: Search for the item matching :id. If not found, return 404 Not Found with {"error": "Asset ID not found"}. If found, remove it from the array, update inventory.json, and return 200 OK with {"message": "Asset successfully removed"}.

------------------------------
## 4. Frontend Web UI Specifications
The server must serve an interactive UI via HTML and Tailwind CSS (loaded via CDN) when hitting the root route GET /. No frontend single-page application (SPA) frameworks are allowed (No React, Vue, or Svelte). Use clean, vanilla JavaScript native asynchronous fetch calls. [2] 
## UI Layout & Components

* Header: Displays a bold title "STIM // Core Inventory Control" and a live reactive counter showing the total number of items currently "In Use".
* The Input Panel: A horizontal form grid containing inputs for Name, Team (dropdown select), Email, Status (dropdown select), and Date.
* UI Constraint: The Add Asset button must stay disabled (disabled attribute) until all input criteria are filled and valid according to Section 2 rules.
* The Main Grid Workspace: A structured layout rendering the inventory as individual "cards" or a responsive table.
* Each card/row must display its data points clearly.
   * If an asset's lastInspected date is older than 180 days from the current system time, the card wrapper must explicitly toggle a soft red background border (border-red-500 border-2) to signify an overdue status.
   * Every item must have a clearly visible red "Decommission" button. Clicking this must launch a standard native browser confirmation dialog (confirm()). If accepted, it makes the DELETE API call and smoothly drops the DOM node from view without a full page refresh.

------------------------------
## Existing GitHub Repositories for SDD & English Specifications
If you want to view, clone, or study repositories built specifically around human-readable markdown specifications, browse these open-source templates and platforms: [3] 

* yoshiakist / specre: A specialized toolset built purely for Spec-Driven Development. It details how individual behaviors are mapped directly to markdown specification documents so that AI agents don't suffer from context drift or bloated codebase assumptions. [4] 
* [paulasilvatech / specky](https://github.com/paulasilvatech/specky): An agentic, specification-driven development environment. It houses structural configurations detailing how to use strict text structures to enforce exact code outputs via LLM frameworks. [5] 
* [jam01 / Software Design Description (SDD) Template](https://github.com/jam01/SDD-Template): An incredible architecture repository following IEEE standards. It is entirely based on writing comprehensive English Markdown templates for software layouts, checking traceability gates, and building technical foundations before code is generated. [6, 7] 
* [noahbald / awesome-architecture-md](https://github.com/noahbald/awesome-architecture-md): A curated collection of excellent real-world Markdown architectural tracking layouts. It links directly to production repositories that manage their rules using plain text files. [8] 

------------------------------
Would you like to move forward by having me:

* Write a comprehensive script prompt that forces an AI code editor to build this exact STIM web server system directly from this text?
* Add an Authentication and Role Layer requirement to this specification to make it even more enterprise-ready for your testing?


[1] [https://docs.platformatic.dev](https://docs.platformatic.dev/docs/learn/beginner/crud-application)
[2] [https://wonderingaboutai.substack.com](https://wonderingaboutai.substack.com/p/tailwind-is-the-best-css-framework)
[3] [https://www.reddit.com](https://www.reddit.com/r/GeminiAI/comments/1ttkznq/a_free_opensource_library_of_designmd_files_for/)
[4] [https://github.com](https://github.com/yoshiakist/specre/blob/main/README.md)
[5] [https://github.com](https://github.com/paulasilvatech/specky)
[6] [https://github.com](https://github.com/jam01/SDD-Template)
[7] [https://github.com](https://github.com/jam01/SRS-Template)
[8] [https://github.com](https://github.com/noahbald/awesome-architecture-md)

