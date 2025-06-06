import os
from typing import Optional
import subprocess
from rich import print

def init_venv(path: Optional[str] = None, requirements_path: str = "requirements.txt"):
    """
    Initialize a virtual environment in the given path. If the requirements.txt file is present, it will install the
    dependencies listed in it.
    """
    if path is None:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)

    venv_path = os.path.join(path, "venv")

    # Create the virtual environment
    try:
        subprocess.run(["python", "-m", "venv", venv_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create virtual environment: {e}")

    # Install requirements if the file exists
    requirements_file = os.path.join(path, requirements_path)
    if os.path.exists(requirements_file):
        try:
            subprocess.run([f"{venv_path}/bin/pip", "install", "-r", requirements_file], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install dependencies: {e}")