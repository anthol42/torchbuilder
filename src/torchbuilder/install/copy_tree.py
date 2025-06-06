import os
import shutil
import fnmatch
from typing import Optional, List, Set
from pathlib import Path
from ..utils import Error, Success, State

def copy_tree(src: str, dst: str, gitignore: Optional[str] = None) -> State:
    """
    Copy a directory tree from src to dst, optionally ignoring files listed in gitignore.
    If the operation is successful, return True; otherwise, return False.
    :param src: Source directory path.
    :param dst: Destination directory path.
    :param gitignore: the content of a .gitignore file to ignore files if it exists.
    """
    try:
        # Convert to Path objects for easier manipulation
        src_path = Path(src)
        dst_path = Path(dst)

        # Check if source exists and is a directory
        if not src_path.exists():
            return Error("Source directory does not exist.")
        if not src_path.is_dir():
            return Error("Source directory is not a directory.")

        # Parse gitignore patterns
        ignore_patterns = _parse_gitignore(gitignore) if gitignore else []

        # Create destination directory if it doesn't exist
        if dst_path.exists():
            if dst_path.is_dir():
                return Error("Destination directory already exists.")
            else:
                return Error("Destination path already exists")

        dst_path.mkdir(parents=True, exist_ok=True)

        # Copy the directory tree
        _copy_directory_recursive(src_path, dst_path, ignore_patterns)

        return Success("Directory copied successfully.")

    except Exception as e:
        # Log the error if needed (could add logging here)
        return False


def _parse_gitignore(gitignore_content: str) -> List[str]:
    """
    Parse gitignore content and return a list of patterns.
    """
    patterns = []

    for line in gitignore_content.strip().split('\n'):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Remove trailing whitespace and add to patterns
        patterns.append(line.rstrip())

    return patterns


def _should_ignore(path: Path, base_path: Path, patterns: List[str]) -> bool:
    """
    Check if a path should be ignored based on gitignore patterns.
    """
    if not patterns:
        return False

    # Get relative path from base directory
    try:
        rel_path = path.relative_to(base_path)
    except ValueError:
        return False

    # Convert to string with forward slashes (gitignore uses forward slashes)
    rel_path_str = str(rel_path).replace(os.sep, '/')
    path_parts = rel_path_str.split('/')

    for pattern in patterns:
        # Skip negation patterns for simplicity (would need more complex logic)
        if pattern.startswith('!'):
            continue

        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if path.is_dir() and _matches_pattern(rel_path_str, pattern, path_parts):
                return True
        else:
            # Handle file and directory patterns
            if _matches_pattern(rel_path_str, pattern, path_parts):
                return True

    return False


def _matches_pattern(rel_path: str, pattern: str, path_parts: List[str]) -> bool:
    """
    Check if a relative path matches a gitignore pattern.
    """
    # Handle patterns that start with /
    if pattern.startswith('/'):
        pattern = pattern[1:]
        return fnmatch.fnmatch(rel_path, pattern)

    # Handle patterns with directory separators
    if '/' in pattern:
        return fnmatch.fnmatch(rel_path, pattern)

    # Handle simple patterns - match against any part of the path
    for part in path_parts:
        if fnmatch.fnmatch(part, pattern):
            return True

    # Also check against the full relative path
    return fnmatch.fnmatch(rel_path, pattern)


def _copy_directory_recursive(src_path: Path, dst_path: Path, ignore_patterns: List[str]):
    """
    Recursively copy directory contents, respecting ignore patterns.
    """
    for item in src_path.iterdir():
        # Check if this item should be ignored
        if _should_ignore(item, src_path.parent, ignore_patterns):
            continue

        dst_item = dst_path / item.name

        if item.is_dir():
            # Create directory and recurse
            dst_item.mkdir(exist_ok=True)
            _copy_directory_recursive(item, dst_item, ignore_patterns)
        else:
            # Copy file
            shutil.copy2(item, dst_item)
