import os
from typing import Optional
import subprocess
from rich import print

def init_uv_project(path: str):
    """
    Initialize a UV project in the given path. If the uv command is not found, it will attempt to install it.
    """
    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        need2install = False
    except FileNotFoundError:
        print("[yellow]UV was not found in path. Consider adding it to avoid on-the-fly installation. Installing it via "
              "pip to continue project installation.[/yellow]")
        need2install = True

    if need2install:
        try:
            subprocess.run(["pip", "install", "--user", "uv"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install UV using pip. Consider installing it manually.")

    try:
        subprocess.run(["uv", "sync"], cwd=path, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to initialize UV project: {e}")