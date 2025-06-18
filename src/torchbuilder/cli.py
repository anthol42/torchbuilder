import json
import sys

import typer
import os
from typing import Optional
from pathlib import PurePath
from torchbuilder.utils import error
from torchbuilder.install import remove_template, install_template
from rich import print
import shutil
from torchbuilder._version import __version__
app = typer.Typer()

@app.command()
def install(path: str, alias: Optional[str] = None):
    """
    Install a repository as a template. All the files and directories listed in the .gitignore file will be ignored.
    The repository will become available as a template under the alias name.
    """
    install_template(path, alias)

@app.command()
def ls():
    """
    List all installed templates.
    """
    home_path = os.path.expanduser("~/.torchbuilder/templates")
    if not os.path.exists(home_path):
        typer.echo("No templates installed")
        return

    templates = os.listdir(home_path)
    if not templates:
        print(f"[yellow]No template installed[/yellow]")
    else:
        typer.echo("Installed templates:")
        for template in templates:
            if os.path.isdir(os.path.join(home_path, template)):
                typer.echo(f"- {template}")

@app.command()
def update(alias: str, path: Optional[str] = None):
    """
    Update the template names alias. If the path is not provided and the template is a remote repository, it will be
    cloned again.
    """
    home_path = os.path.expanduser("~/.torchbuilder/templates")
    dest_path = os.path.join(home_path, alias)

    # Check if some templates are installed
    if not os.path.exists(home_path) or not os.listdir(home_path):
        error(f"No templates installed. Cannot remove {alias}.")

    # Check if the template exists
    if not os.path.exists(dest_path):
        error(f"Template named {alias} does not exist.")

    if alias == ".registry.json":
        error("Cannot update the registry file.")

    if path is None:
        # If no path is provided, check if the template is a remote repository
        registry_path = f'{home_path}/.registry.json'
        if not os.path.exists(registry_path):
            error("Registry file does not exist. Cannot update the template without path.")

        with open(registry_path, 'r') as f:
            registry = json.load(f)

        if alias not in registry:
            error(f"Template named {alias} does not exist in the registry.")

        src = registry[alias]["src"]
        if src == "local":
            error("The template is not a remote repository. Please provide the path to the template.")
        else:
            path = f'git+{src}'

    # Remove the existing template
    remove_template(dest_path, home_path, alias)

    # Add the new template
    install_template(path, alias)

@app.command()
def remove(alias: str):
    """
    Remove a template by its alias.
    """
    home_path = os.path.expanduser("~/.torchbuilder/templates")
    dest_path = os.path.join(home_path, alias)

    # Check if some templates are installed
    if not os.path.exists(home_path) or not os.listdir(home_path):
        error(f"No templates installed. Cannot remove {alias}.")

    # Check if the template exists
    if not os.path.exists(dest_path):
        error(f"Template named {alias} does not exist.")

    if alias == ".registry.json":
        error("Cannot remove the registry file.")

    remove_template(dest_path, home_path, alias)

@app.command()
def new(path: str, template: str = "default", noinit: bool = False):
    """
    Create a new project from a template. If noinit flag is set, the initialization script will not be run
    and will need to be run manually.
    """
    home_path = os.path.expanduser("~/.torchbuilder/templates")
    template_path = os.path.join(home_path, template)
    if (not os.path.exists(home_path) or not os.listdir(home_path)) and template != "default":
        error(f"No templates installed. Cannot create a new project from {template}.")

    if not os.path.exists(template_path) and template != "default":
        error(f"Template named {template} does not exist.")

    # No template found, but the default template is requested.
    # We will install the default template from the repository.
    elif not os.path.exists(template_path) and template == "default":
        print(f"[yellow]No template named found. Installing the default template...[/yellow]")
        install_template("git+https://github.com/anthol42/tb-template_functional.git", "default")

    dest_path = os.path.abspath(path)
    if os.path.exists(dest_path):
        error(f"Destination path {dest_path} already exists. Please choose a different path.")

    # Copy the template to the destination path
    shutil.copytree(template_path, dest_path)

    # If noinit is not set, run the initialization script
    if not noinit:
        init_script = os.path.join(dest_path, ".template_init.py")
        if os.path.exists(init_script):
            try:
                import subprocess
                subprocess.run([sys.executable, init_script], check=True)
            except subprocess.CalledProcessError as e:
                error(f"Initialization script failed: {e}")

            # Remove the initialization script after running it
            os.remove(init_script)
        else:
            print(f"[yellow]No initialization script found in the template. Skipping initialization.[/yellow]")

def version_callback(value: bool):
    if value:
        print(f"Torchbuilder version: {__version__}")
        raise typer.Exit()

@app.callback()
def cb(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    # Weird synthax, but this is what enables the --version flag to work
    return

def main():
    app()

if __name__ == "__main__":
    main()