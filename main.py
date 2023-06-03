import os
from pathlib import PurePath
os.chdir(PurePath(__file__).parent)
import shutil
from setting import filetree
import sys
from setting import File
import subprocess
import time

class Solution:
    def __init__(self, path: PurePath):
        with open(path, 'r') as file:
            solution = file.read().split("\n")
        name = solution[0]
        projects = set()
        for line in solution[1:]:
            projects.add(line.replace("\t", "").replace("\n", "")) if len(line) > 0 else None
        self.name = name
        self.projects = projects
    def new(self, project_name):
        self.projects.add(project_name) if project_name is not None else None


    def remove(self, project_name):
        self.projects.remove(project_name) if project_name is not None else None


    def save(self, path: PurePath):
        if len(self.projects) == 0 or self.projects is None:
            out = ""
        else:
            out = '\n\t'.join(self.projects)
        out = f'{self.name}\n\t' + out
        with open(path, 'w') as file:
            file.write(out)

def _make_subfolder(initial_path: os.path, tree: dict):
    for key, value in tree.items():
        key = os.path.join(key)
        if isinstance(value, dict):
            os.makedirs(f"{initial_path}/{key}")
            _make_subfolder(f"{initial_path}/{key}", value)
        elif isinstance(value, File):
            with open(f"{initial_path}/{key}", "w") as file:
                file.write(value.content)
        else:
            raise ValueError(f"Value of type:{type(value)} is not allowed int filetree.  Value must be File or Dict.")

def create_project(project_path, cli_kwargs = None):
    project_name = project_path.name
    try:
        shutil.rmtree(project_path)
    except FileNotFoundError:
        pass
    filetree['README.md'].content = f"# {project_name}\n\n## Description\n\n## How to use\n\n## Examples"
    os.mkdir(project_path)
    _make_subfolder(f'{project_path}', filetree)
    if not cli_kwargs.get("--venv"):
        pass
    else:
        subprocess.run(['sh', './resources/create_venv.sh', project_path])


def create_solution(solution_path: PurePath, project_name=None, cli_kwargs={}):
    solution_name = solution_path.name
    try:
        shutil.rmtree(solution_path)
    except FileNotFoundError:
        pass
    os.makedirs(solution_path)
    with open(f'{solution_path}/.solution.sol', 'w') as file:
        file.write(f"{solution_name}\n")
    with open('resources/gitignore.txt', 'r') as file:
        gitignore = file.read()
    with open(solution_path / PurePath(".gitignore"), 'w') as file:
        file.write(gitignore)
    with open(solution_path / PurePath("README.md"), 'w') as file:
        file.write(f"# {solution_name}\n\n## Description\n\n## How to use\n\n## Examples")
    if project_name:
        solution = Solution(solution_path / PurePath(".solution.sol"))
        solution.new(project_name)
        solution.save(solution_path / PurePath(".solution.sol"))
        create_project(solution_path / PurePath(project_name), cli_kwargs)
    if cli_kwargs.get('--repo'):
        subprocess.run(['sh', './resources/init_git.sh', solution_path, cli_kwargs["--repo"]])


def interactive_mode():
    print("Interactive mode not implemented yet.  Use arguments to create solution or projects")

def parse_kw(args):
    kw = {}
    for arg in args:
        parse = arg.split("=")
        if len(parse) != 2:
            print(f"Invalid kwarg: '{arg}' !  Must be of form: 'key'='value'")
            quit(-1)
        key, value = parse
        if value == "True":
            value = True
        elif value == "False":
            value = False
        kw[key] = value
    return kw


if __name__ == "__main__":
    cli_args = sys.argv[1:]
    if len(cli_args) == 0:
        print("You must provide the current working directory")
        exit(-1)
    wd = PurePath(cli_args[0])
    if len(cli_args) == 1:
        interactive_mode()
    else:
        if cli_args[1] == 'make':
            if len(cli_args) < 3:
                print("You must enter a solution name after 'make'")
                quit(-1)
            solution_path = wd / PurePath(cli_args[2])
            if len(cli_args)>2:
                kw = parse_kw(cli_args[3:])
            else:
                kw = {}

            create_solution(solution_path, kw.get("project"), kw)
            exit(0)
        elif cli_args[1] == 'new':
            if len(cli_args) < 3:
                print("You must enter a project name after 'new'")
                quit(-1)
            project_path = wd / PurePath(cli_args[2])
            project_name = project_path.name
            solution_path = project_path.parent
            if len(cli_args)>2:
                kw = parse_kw(cli_args[3:])
            else:
                kw = {}
            if not os.path.exists(solution_path / PurePath(".solution.sol")):
                print("You must create a project in a solution!  Use the command 'make' to make a solution")
                exit(-1)
            solution = Solution(solution_path / PurePath(".solution.sol"))
            solution.new(project_name)
            solution.save(solution_path / PurePath(".solution.sol"))
            create_project(project_path, kw)
            exit(0)
        elif cli_args[1] == 'remove':
            if len(cli_args) < 3:
                print("You must enter a project name after 'remove'")
                quit(-1)
            project_path = wd / PurePath(cli_args[2])
            project_name = project_path.name
            solution_path = project_path.parent
            if len(cli_args)>2:
                kw = parse_kw(cli_args[3:])
            else:
                kw = {}
            if not os.path.exists(solution_path / PurePath(".solution.sol")):
                print("The specified path does not belong to any solution.  It must be a project in a solution!")
                exit(-1)
            if not os.path.exists(project_path):
                print("The specified project does not exist!  It must exist to delete it.")
                exit(-1)
            solution = Solution(solution_path / PurePath(".solution.sol"))
            solution.remove(project_name)
            solution.save(solution_path / PurePath(".solution.sol"))
            shutil.rmtree(project_path)
            exit(0)
        else:
            print(f"Error, invalid argument: {cli_args[1]} ")
            exit(-1)