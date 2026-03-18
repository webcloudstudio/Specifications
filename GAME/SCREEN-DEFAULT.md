# Screen: Default

**The main view.** Configurable Default Project Screen

---

## Layout

Full-width project list. One row per project. Nav bar at top 
  
## Nav bar

The nav bar has 
    a custom title passed in as an argument
    a filter button rotating states from Archive/Idea/Normal/All with the behavior that Archive shoes just Archived status, Idea shows just Idea status, Normal shows everything but Archived and Idea, and All shows all.  The default is normal. 

## Per-Project Row Mandatory Elements

| Element | Location | Column Title | Source | Interaction |
|---------|--------|-------------|------------|------------------------|
| Status badge | First Column     | Status | METADATA.md `status` | Click -> increment/rotate status |
| Namespace badge | Second Column | <none> | METADATA.md `namespace` | Display only |
| Project name | Third Column     | Project | METADATA.md `display_name` | Click → project detail |
| Settings | Last Column          | <none> | Operation Icon | Click -> Open page project/<id>
  
The Status Badge, when single clicked, should change the projects status through the workflow defined elsewhere

The Per project table will have a header identified by the column titles above.  When a column title row is selected that row will sort the table.  If you click the Status Badge it will change and persist

## Middle Page Column Display

The middle of the page will display columns which can be set dynamically on the form.  The following table lists the Elements which can be passed into the program for display in the middle columns.

The column order should display in terms of the passed in arguments.  If the form is called with Tags,Help it will show the tags column with the title Tag and in the next column it will show the Help section with the 

## Optional Fields to Show

| Element | Column Title | Source | Interaction |
|------------|---------|--------|-------------|
| Tags | Tags | METADATA.md | tags displayed in their colors|
| Port | Port | METADATA.md | port for the server |
| Tags | Tags | METADATA.md | tags displayed in their colors|

| Stack | Stack summary | METADATA.md `stack` | Display only |
| Actions | Action Buttons | bin/ headers (one per registered script) | Click → run script |
| Links | Quick links | AGENTS.md bookmarks | Click → open URL |
| Claude | Claude | CLAUDE.md button | Click → open CLAUDE.md |
| Help | Help | HELP button | Click → open Project Help Page in doc[s]/index.htm[l] |
| Maintenance | Maintenance | bin/ headers with string "Category: Maintenance" | Click → run script |
| LastUpdate | Last Update | Database | last time the project code or data was updated.

The LastUpdate field is a new field that should be identified if possible on Startup based on the last time the METADATA.md file or the project files were updated (perhaps the last git commit)

## Startup Behavior

Action Buttons are Buttons stored in the project bin/ directory that have a common header

    The string "CommandCenter Operation" within the first 20 lines
    The string "Name: <operation name>" identifying the operation name

Optional fields useful here are
    The optional string "Category: <operation category>"
    This enables us to show a subset of the operations on the screen