# Specification Directory

    # Clean Up Specifications Directories by Adding Readmes
    # Problem: Metadata is stored in files not in a Better location like the readme. 
    # Solution: Move it to predefined locations in the readme files
    Modify the subdirectories for projects and "stack" to include README.md file.  Move programatic metadata like Prerequesites from the markdown file to README.md so README alone can provide context aware metadata while file-only metadata stays in individual files
        Use Heading 1 Markdown to indicate section name - ie. "# Catalog" for Catalog Metadata
        Section #Catalog contains files and their short description
        Section #Stacks has stack_short_name,stack_short_descr,when to use,[component technologies] 
        Section #Prerequisites has prerequesites

    # Problem 2: What is my specification application
        Specifictions/GAME -> Old code so archivedc to GAME_old
        SPEC_STANDARD.md
        Specifications/
            -rwxrwxrwx 1 barlo barlo  8957 Mar  7 16:06 SPEC_STANDARD.md
            -rwxrwxrwx 1 barlo barlo 97044 Mar 11 21:35 SPEC_STANDARD.pdf
        project_specifications/
            -rwxrwxrwx 1 barlo barlo  21451 Mar 11 10:13  APPROACH.md
        docs/
            -rwxrwxrwx 1 barlo barlo  2572 Mar 11 13:05 LOGGING.md
        
        Editing Modifications
            GAME is Generic Agent Management Environment
            Call it "The GAME Methedology"
            Simplify the methedology and other documents - technical short and simple
            Some of the text wraps... so the new lines are being respected ADD A STANDARD TO STRIP DOS LINEFEEDS FROM FILES AUTOMATICALLY BECAUSE IT MESSES THINGS UP.


    # Core Insights

        PROJECT_NAME
            README.md
            <markdown files>
                Project.md
                0X_<FEATURE>.md


