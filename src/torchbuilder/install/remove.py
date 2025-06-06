import json
import shutil
import os


def remove_template(dest_path: str, home_path: str, alias: str):
    shutil.rmtree(dest_path)

    # remove it from the registry
    registry_path = f'{home_path}/.registry.json'
    if not os.path.exists(registry_path):
        return
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    if alias in registry:
        del registry[alias]
        with open(registry_path, "w") as f:
            json.dump(registry, f)