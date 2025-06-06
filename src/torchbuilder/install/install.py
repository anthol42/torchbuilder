from typing import Optional
import os
from ..utils import error
from pathlib import PurePath
import json
import shutil
from .copy_tree import copy_tree
from .remote import clone_repo

def install_template(path: str, alias: Optional[str] = None):
    home_path = os.path.expanduser("~/.torchbuilder/templates")
    # Ensure the home path exists
    if not os.path.exists(home_path):
        os.makedirs(home_path)

    # If remote repository, clone it
    if path.startswith("git+"):
        github: bool = True
        repo_url = path[4:]
        if not repo_url.endswith(".git"):
            error("Repository URL must end with .git")
        alias = PurePath(repo_url).name.replace(".git", "") if alias is None else alias
    else:
        github: bool = False
        src_path = os.path.abspath(path)
        alias = PurePath(src_path).name if alias is None else alias

    dest_path = os.path.join(home_path, alias)
    if os.path.exists(dest_path):
        error(f"Template named {alias} already exists. Use the update command to update it or uninstall it first.")

    if github:
        # Clone the repository to a temporary directory
        temp_dir = os.path.join(PurePath(home_path).parent, "temp_repo")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        clone_repo(repo_url, temp_dir)
        src_path = temp_dir


    # Check if the src_path has a .gitignore file
    gitignore = os.path.exists(os.path.join(src_path, ".gitignore"))
    if gitignore:
        with open(os.path.join(src_path, ".gitignore"), "r") as f:
            gitignore_content = f.read()
    else:
        gitignore_content = None

    # Copy the directory tree
    result = copy_tree(src_path, dest_path, gitignore_content)
    if result.error:
        error(result.msg)

    # update the template registry
    registry_path = f'{home_path}/.registry.json'

    if not os.path.exists(registry_path):
        with open(registry_path, "w") as f:
            json.dump({}, f)

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    registry[alias] = {
        "src": path[4:] if github else "local",
    }
    with open(registry_path, "w") as f:
        json.dump(registry, f)