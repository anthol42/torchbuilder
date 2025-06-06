import subprocess
import sys
import os
from typing import Optional
from ..utils import error
import shutil

def clone_repo(repo_url: str, dest_path: Optional[str] = None):
    """
    Clone a Git repository to the specified destination path.
    """
    if dest_path is None:
        dest_path = os.getcwd() + "/" + os.path.basename(repo_url).replace('.git', '')
    try:
        subprocess.run(["git", "clone", repo_url, dest_path], check=True)
    except subprocess.CalledProcessError as e:
        error("Failed to clone repository. Please check the repository URL and your network connection.")

    # Delete the .git directory if it exists
    git_dir = os.path.join(dest_path, ".git")
    if os.path.exists(git_dir):
        try:
            shutil.rmtree(git_dir)
        except Exception as e:
            error(f"Failed to remove .git directory: {e}")