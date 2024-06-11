# TODO
TODO list for version **0.3.0**  
Current version: **0.2.2**

## Features and Functionalities
- [X] Add a way to clean hidden files and Python cache files and folders this should remove venv, all cache files, pycache and 
folders (except gitignore) 
- [X] Add a way to export and import templates
- [ ] Make templating dynamic (Possibility to link module files or external files -> the compiling process will make them part of the template (Static))
- [ ] Make sub-template rendering: Possibility to add a token that is replaced at build time (When building the template  - inference)  
Example: Format the title of a readme with the name of the project

- [ ] Make app installable by pip and make the utils such as color, resultTable, etc available from the package (And linkable in templates)
- [ ] Make a hub of templates (Repo github) where people can submit their templates and others can download them.
- [ ] Add update method in torchbuilder that will clone the repo and update torchbuilder while keeping templates
we can use github api for this (https://api.github.com/repos/{owner}/{repo}/contents/{path})

## Templates
- [ ] Update default template
  - [ ] (next version) Add a scripting helper module to run multiple files at the same time (in parallel)
  - [ ] include wall time in result table
  - [ ] Add a way to remove records from result table
  - [ ] Add way to see stats of resultTable (ex: categories, number of elements per category)
  - [ ] Add a way to access élément by runID with getitem magic function.  Maybe can delete or set.
- [ ] Create a new template using torch lightning
- [ ] Create a single page template using keras 3