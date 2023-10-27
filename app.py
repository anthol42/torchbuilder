import os
import sys
from pathlib import PurePath
from builder_utils.color import Color, ResetColor
from builder_utils.templates import compile, ls_templates, rm_template, show
from builder_utils.sol_builder import make, new_proj
from builder_utils.utils import enum_input, std_in, bool_input

def interactive():
    # Reading templates:
    torchbuilder_path = PurePath(os.path.dirname(__file__))
    templates = [PurePath(f.path).name for f in os.scandir(f"{torchbuilder_path}/Templates") if f.is_dir()]
    choices = {
        "Compile Template": "compile",
        "New Solution": "make",
        "New Project": "new"
    }
    ans = enum_input("Welcome to the interactive Torchbuilder!\nWhat do you want to do?", "Wrong input", choices)
    if ans == "make":
        name = std_in("What is the name of the solution?",
                      "Name cannot be empty and cannot contain special characters.",
                      lambda s: s != "" and s.isalnum())
        project = std_in("What is the name of the project?",
                      "Project names cannot be empty and cannot contain special characters.",
                      lambda s: s != "" and s.isalnum())

        venv = bool_input("Do you want to create automatically a virtual environment?")

        # Templates
        choices = {template: template for template in templates}
        choices["default"] = ""

        template = enum_input("Which template do you want to use?", "The template does not exists", choices)
        if template == "":
            template = "default"

        repo = input("Do you want to push the created solution to a repo?  If yes, paste the url of the repo.  "
                     "If no, press enter\n> ")
        kwargs = {}
        kwargs["project"] = project
        kwargs["venv"] = str(venv)
        kwargs["template"] = template
        if repo != "":
            kwargs["repo"] = repo
        make(name, **kwargs)
    elif ans == "new":
        project = std_in("What is the name of the project?",
                      "Project names cannot be empty and cannot contain special characters.",
                      lambda s: s != "" and s.isalnum())

        venv = bool_input("Do you want to create automatically a virtual environment?")

        # Templates
        choices = {template: template for template in templates}
        choices["default"] = ""
        template = enum_input("Which template do you want to use?", "The template does not exists", choices)
        if template == "":
            template = "default"

        kwargs = {}
        kwargs["venv"] = str(venv)
        kwargs["template"] = template
        new_proj(project, **kwargs)

    elif ans == "compile":
        name = std_in("What is the name of the template you want to create?",
                      "Templates names cannot be empty, cannot contain special characters and cannot have the same "
                      "name as another template.",
                      lambda s: s != "" and s.isalnum() and s not in templates)
        source = std_in("What is the source directory to compile and use as a template?",
                        "The corresponding path does not exists.",
                        lambda s: os.path.exists(s))
        compile(name, source)

    else:
        raise KeyError("Unexpected keyword.")

class App:
    def __init__(self, commands: dict):
        self.commands = commands
        self.commands["help"] = self.help
        self.commands["version"] = self.version

    def __call__(self):
        args = sys.argv[1:]
        if len(args) < 1:
            interactive()
        else:
            command = args[0]
            if command not in self.commands:
                print(f"{Color(203)}The requested command: {command} does not exists.  See 'torchbuilder help'"
                      f" for more info.{ResetColor()}")
                exit(-1)
            args, kwargs = self._command_parser(args[1:])
            self.commands[command](*args, **kwargs)

    @staticmethod
    def _command_parser(commands):
        """
        Extract args and kwargs from the given commands
        Kw args must be defined as follows to be interpreted as kwargs:
                --<key>=<value>
            example:
                --venv=True
        :param commands:
        :return:
        """
        args = []
        kwargs = {}
        for arg in commands:
            if arg.startswith("--") and "=" in arg:
                idx = arg.find("=")
                key, value = arg[:idx].replace("--", ""), arg[idx + 1:]
                kwargs[key] = value
            else:
                args.append(arg)
        return args, kwargs

    def version(self, *args, **kwargs):
        base_path = os.path.dirname(__file__)
        with open(f"{base_path}/ressources/version.txt") as file:
            content = file.read().split("\n")
            version, date = content[0], content[1]
        print(f"Torchbuilder {date} version {version}")
    def help(self, *args, **kwargs):
        print(
"""Welcome to TorchBuilder!
This utility program aims at helping researchers to develop faster and cleaner projects, so they can test as
fast as their ideas flows.  The main purpose of Torchbuilder is to build the project structure, the file tree
and boilerplates in the Pytorch's framework following a given template.  Templates are like a cooking recipe for 
Torchbuilder that tells it which files it should create and what it should write in those files.  In this new 
version of TorchBuilder, the templates are customizable!
Commands:
    >>> make <sol_name> --project=<proj_name> --venv=True --repo=<repo_link> --template=default
        ↳ This function will create a solution with a project.
    
    >>> new <proj_name> --venv=True --template=default
        ↳ This function will create a new project.
    
    >>> compile <name> <source>
        ↳ This function will build a template from a project (source).
    
    >>> ls-templates
        ↳ This function will print every templates available.
    
    >>> rm-template <name>
        ↳ This function will remove the given template.
        
    >>> show-template <name>
        ↳ This will show the file tree that the template will build.
    
    >>> help
        ↳ This function will show this.
    
    >>> version
        ↳ This function will show the version of the app and its release date.
        """)



if __name__ == "__main__":
    commands = {
        "compile": compile,
        "ls-templates": ls_templates,
        "rm-template": rm_template,
        "show-template": show,
        "make": make,
        "new" : new_proj
    }
    app = App(commands)
    app()