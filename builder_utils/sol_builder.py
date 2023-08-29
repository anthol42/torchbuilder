from pathlib import PurePath
import os
from .utils import eprint
import subprocess
import json
from typing import Union

class Project:
    def __init__(self, out_path: Union[str, PurePath], template: str = "default", build_venv: bool = True):
        """
        :param out_path: The path where to create the project
        :param template: The template to use to create the project
        :param build_venv: Whether to build the venv based on requirements
        """
        self._out_path = out_path
        self._venv = build_venv
        torchbuilder_path = PurePath(os.path.dirname(__file__)).parent

        if os.path.exists(out_path):
            eprint("The project directory location isn't empty.  Consider changing the project's name or removing the "
                   "target directory")

        if not os.path.exists(f"{torchbuilder_path}/Templates/{template}"):
            eprint(f"The requested template: {template} does not exist.")

        if not os.path.exists(f"{torchbuilder_path}/Templates/{template}/.config/.index.json"):
            eprint(f"The requested template: {template} is broken since it does not contain a .config/.index.json file")

        with open(f"{torchbuilder_path}/Templates/{template}/.config/.index.json", "r") as file:
            self.template = json.load(file)

    def _recursive_build(self, path: str, remaining_template: dict, torchbuilder_path: PurePath):
        for item, source in remaining_template.items():
            if isinstance(source, dict):
                os.mkdir(f"{path}/{item}")
                self._recursive_build(f"{path}/{item}", remaining_template[item], torchbuilder_path)
            else:
                with open(f"{torchbuilder_path}/Templates/{source}", "rb") as infile:
                    content = infile.read()
                with open(f"{path}/{item}", "wb") as file:
                    file.write(content)

    def build(self):
        torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
        os.mkdir(self._out_path)
        self._recursive_build(self._out_path, self.template, torchbuilder_path)
        if self._venv:
            subprocess.run(['bash', f'{torchbuilder_path}/ressources/create_venv.sh', self._out_path])


def make(*args, **kwargs):
    """
    torchbuilder make <sol_pathname> --project='proj_name'
    """
    if len(args) != 1:
        eprint("You must enter a solution name after 'make'")

    sol_pathname = args[0]

    solution_path = os.getcwd() / PurePath(sol_pathname)
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent

    if "project" not in kwargs:
        eprint("You must provide a project name.  'torchbuilder make <sol_name> --project=<project_name>'")

    if os.path.exists(solution_path):
        eprint("The solution path already exists.  Consider using a different name or delete the corresponding folder.")

    os.makedirs(solution_path)

    with open(f'{torchbuilder_path}/ressources/gitignore.txt', 'r') as file:
        gitignore = file.read()
    with open(solution_path / PurePath(".gitignore"), 'w') as file:
        file.write(gitignore)
    with open(f"{torchbuilder_path}/ressources/version.txt") as file:
        content = file.read().split("\n")
        version, date = content[0], content[1]
    with open(f'{torchbuilder_path}/ressources/sol_README.md', 'r') as file:
        content = file.read()
        content = content.replace("<SOlUTION>", solution_path.name)
        content = content.replace("<VERSION>", version)
    with open(solution_path / PurePath("README.md"), 'w') as file:
        file.write(content)

    # Now, create the project
    if "template" in kwargs:
        template = kwargs['template']
    else:
        template = "default"

    if "venv" in kwargs:
        venv = kwargs["venv"].upper() == "TRUE"
    else:
        venv = True

    proj = Project(f"{solution_path}/{kwargs['project']}", template, build_venv=venv)
    proj.build()

    if kwargs.get('repo'):
        subprocess.run(['sh', f'{torchbuilder_path}/ressources/create_venv.sh', solution_path, kwargs["repo"]])

def new_proj(*args, **kwargs):
    if len(args) != 1:
        eprint("You must enter a project name after 'new'")
    project_path = os.getcwd() / PurePath(args[0])
    if "template" in kwargs:
        template = kwargs['template']
    else:
        template = "default"

    if "venv" in kwargs:
        venv = kwargs["venv"].upper() == "TRUE"
    else:
        venv = True

    proj = Project(f"{project_path}", template, build_venv=venv)
    proj.build()

