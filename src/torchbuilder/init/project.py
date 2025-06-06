import os
from pathlib import PurePath

def get_project_path(init_fp: str) -> str:
    """
    Get the project path from the initialization file path.
    """
    init_path = PurePath(init_fp).parent
    if init_path.is_absolute():
        return str(init_path)
    else:
        return os.path.abspath(init_path)