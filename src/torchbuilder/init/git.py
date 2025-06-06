import subprocess

def init_git_repo(path: str):
    """
    Initialize a git repository in the given path.
    """
    try:
        subprocess.run(["git", "init"], cwd=path, check=True)
        subprocess.run(["git", "add", "."], cwd=path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=path, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to initialize git repository: {e}")