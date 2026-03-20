# Screen: Configuration

## Purpose

This file allows editing of the metadata stored for each project and visualization of the other data

## Metadata Section

Shows the key value pairs from Metadata.md 

## Read Only Section

The screen has a section on the right with the metadata discovered using file system probes. Each 

## Script Discovery

Information discovered from the scripts 

## Layout

Tabular design with standard header colunns
    status
    Project Icon
    display_name
    port (label port:)
    show_on_homepage (label show:)
    tags:  (label tags:)
    Cog Icon

Selecting the Cog Icon on the far right allows a screen enabling edit of ANY of the fields in metadata.md

The Workflow: item does not need to show (prior version) - that is handled by simply clicking on the workflow status button

The Initial Columns Status Badge, An Icon indicating Project Type, and Project name are a standard header for several pages.

## Persistence

All data edited on this screen is saved in the database and in the project metadata.md
Persistence is immediate after a field is tabbed out of or the tab itself is exited