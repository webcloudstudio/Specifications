# Please update the following
===
# Clean Up Specifications Directories by Adding Readmes
    # Directory projects/Specifications
    # Problem: Metadata is stored in files - it should be in a Better location like METADATA.md
    # Modify the subdirectories for projects and "stack" to include README.md file.  Move programatic metadata like Prerequesites from the markdown file to README.md so README alone can provide context aware metadata while file-only metadata stays in individual files
        Use Heading 1 Markdown to indicate section name - ie. "# Catalog" for Catalog Metadata
        Section #Catalog contains files and their short description
        Section #Stacks has stack_short_name,stack_short_descr,when to use,[component technologies] 
        Section #Prerequisites has prerequesites
    Create a list of metadata commonly used for projects including the ones i have designed.  This metadata database can be used for our orchestration and should include technical and non technical features
===
# Multiple Instances of Specification Workflow

Current Locations
        Specifictions/GAME -> Old code so archived to GAME_old
        Specifications/SPEC_STANDARD.md -> Archived to _unused
            -rwxrwxrwx 1 barlo barlo  8957 Mar  7 16:06 SPEC_STANDARD.md
        GAME/project_specifications/
            -rwxrwxrwx 1 barlo barlo  21451 Mar 11 10:13  APPROACH.md
        GAME/docs/
            -rwxrwxrwx 1 barlo barlo  2572 Mar 11 13:05 LOGGING.md

        DECISION - The GAME software is tooling to manages agents and software packages for small and mid sized business
        DECISION - THE Specifications software in ~/Projects/Specifications is the software to document and rebuild from specificaitons
                 - it contains latest copies
        ACTION - 
            move GAME/docs/features to GAME/docs/GAME 
            move GAME/docs/*.md (LOGGING, METHEDOLOGY...) and the index and rebuild_index.sh to the Specification project 
            Update the Specifications/rebuild_index.sh so index.html will show all project subdirectories and rebuild the index to show the spec and the projects.  The index.html file afterwards should have "FOUNDATION" and then a link to GAME and other directories by project - each of which should kind have their own index.html.  When we click on GAME we get the GAME specification and a link back to the foundation.  

===
Standardize Persistence
    The persistence methedology is awful and individually defined for the project

    I want a single METADATA.md file per project that contains project configuration
        Please define the file.  with format like: name, git repository, short description, links etc
        All project metadata from the git*

    For all directories in projects/
        convert git_homepage.md and Links.md to the metadata.md format if the files exist

    Update the projects/GAME software to no longer use git_homepage.md and Links.md

Standardize Batch Convention
        The related problem is all the conventions around the metadata for scripts.  The problem is that scripts should automatically perform operations like logging and other capabilities
        
        If we use bash scripts to manage all START, STOP, or other MAINTENANCE operations.  It is a primary endpoint for the systems
        My methedology has been previously noted and includes sdtout/stderr redirection and built in heartbeating/event/logging management 
            it performs all normal command and control job management operations we expect.  
        Create a standard best practices document for BASH_SCRIPT_INTEGRATION.md in projects/Specifications
            add ideas commontly used by others - there could be standard scripts like heartbeat.sh and get_event_log.sh as you see fit
        Standardize Port Management
            if we are starting and stopping or polling servers, we need a mechanism to get PORT globally in each script for which it is needed
            this can be a bash primitive

===
Documentation Update

Given the above prompts just implemneted, please update the documentation and workflow

These are instructions to update the documentation originally stored in projects/GAME/docs/ which have been moved to projects/Specifications

THE DOCUMENTATION IN ~/projects/Specification
                stack
                capabilities
                    README.md
                    MARKDOWN FILES
                <PROJECT DIRECTORIES>
                    README.md
                    MARKDOWN FILES

Incorporate the excalidraw diagrams which are in GAME/static/contents and their png conversions in GAME/static/diagrams to the specification for GAME which is in docs/features.

        Editing Modifications
            GAME is Generic Agent Management Environment
            Call it "The GAME Methedology"
            Simplify the methedology and other documents - technical short and simple
            Keep it simple
            Each Capability

        Part 1 of this prompt is to create a list of capabilities
            What is needed to make an application - observability -> logging/heartbeats/events command&control -> service start/stop/status etc...
            What infrastructure features would you add - Developement/QA/Production Services ... 
        Part 2 of this prompt is to flesh them out with very simple common best practices
        Part 3 is to take out the boilerplate expanations of why we do things fromt he documentation and keep it simple - what does this model do, how does it do it.  I want the various feature documentation to be in consistent documented sections

        Design the capabilities with well defined contracts.  Example capabilities are the items i have mentioned as required (heartbeats, events, logging...) with each having perhaps multiple 


# Multiple Instances of Specification Workflow

Current Locations
        Specifictions/GAME -> Old code so archived to GAME_old
        Specifications/SPEC_STANDARD.md -> Archived to _unused
            -rwxrwxrwx 1 barlo barlo  8957 Mar  7 16:06 SPEC_STANDARD.md
        GAME/project_specifications/
            -rwxrwxrwx 1 barlo barlo  21451 Mar 11 10:13  APPROACH.md
        GAME/docs/
            -rwxrwxrwx 1 barlo barlo  2572 Mar 11 13:05 LOGGING.md

        DECISION - The GAME software is tooling to manages agents and software packages for small and mid sized business
        DECISION - THE Specifications software in ~/Projects/Specifications is the software to document and rebuild from specificaitons
                 - it contains latest copies
        ACTION - 
            move GAME/docs/features to GAME/docs/GAME 
            move GAME/docs/*.md (LOGGING, METHEDOLOGY...) and the index and rebuild_index.sh to the Specification project 
            Update the Specifications/rebuild_index.sh so index.html will show all project subdirectories and rebuild the index to show the spec and the projects.  The index.html file afterwards should have "FOUNDATION" and then a link to GAME and other directories by project - each of which should kind have their own index.html.  When we click on GAME we get the GAME specification and a link back to the foundation.  