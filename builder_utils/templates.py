from .color import Color, ResetColor
from .compiler import Compiler
from .utils import eprint
from .color import Color, ResetColor
import shutil
import re
import tarfile

import os
from pathlib import PurePath

def show(*args, **kwargs):
    # Step 1: Verofy input
    if len(args) != 1:
        eprint("Wrong syntax.  The good syntax is: torchbuilder show-template <name>")
    name = args[0]
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
    os.chdir(torchbuilder_path)
    if not os.path.exists(f"./Templates/{name}"):
         eprint("The template does not exists")

    if not os.path.exists(f"./Templates/{name}/template_format.txt"):
        eprint("The template is not correctly configured: it does not have any 'template_format.txt' file")
    with open(f"./Templates/{name}/template_format.txt", 'r') as file:
        txt = file.read()
        filtered = re.sub(r' *\[.*]\n', "", txt)
    print(filtered)


def compile(*args, **kwargs):
    # Step 1: Verify input
    if len(args) != 2:
        eprint("Wrong syntax.  The good syntax is: torchbuilder compile <name> <source_dir>")

    name, source = args
    if source[0:2] == "./":
        absolute = False
        source = source[1:]
    elif source[0] != "/":
        absolute = False
        source = "/" + source
    else:
        absolute = True
    if not absolute:
        source = os.getcwd() + source
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
    os.chdir(torchbuilder_path)
    if not name.replace("-", '').isalnum():
        eprint(f"Only alphabet character, digits and hyphens are allowed for Template names! Got: {name}")

    ignore = kwargs.get("ignore", [])    # Regex expression to ignore files and directories
    ignore_dir = [i for i in ignore if i[-1] == "/"]
    ignore_files = [i for i in ignore if i[-1] != "/"]
    #Step 2: compile
    compiler = Compiler()
    if os.path.exists(f"./Templates/{name}"):
         eprint("The template already exists.  You cannot create a template with the same name as an already "
                "existing template.  Remove the old one before creating a new one.")
    compiler(name, source, ignore_files, ignore_dir)

def ls_templates(*args, **kwargs):
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
    os.chdir(torchbuilder_path)
    templates = [PurePath(f.path).name for f in os.scandir("./Templates") if f.is_dir()]
    for template in templates:
        print(f"-> {template}")

def rm_template(*args, **kwargs):
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
    os.chdir(torchbuilder_path)
    # Step 1: Verify input
    if len(args) != 1:
        eprint("Wrong syntax.  The good syntax is: torchbuilder rm-template <name>")
    name = args[0]
    if not name.replace("-", "").isalnum():
        eprint("Wrong template.  Template names must be composed of alphabet character or digits.")
    if not os.path.exists(f"./Templates/{name}"):
        eprint("Wrong template.  The template does not exist.")

    if name == "default":    # Take special care of default template to avoid undefined behavior
        ans = input(f"{Color(220)}Are you sure you want to delete the default template  You won't be able to properly use the "
                    f"app when not giving explicitly a template?  This might result in buggy or undefined behavior!  "
                    f"If you really want to remove the default template, it is strongly recommended that you create a "
                    f"new default template to replace the old one.  Are you sure to remove the default template and "
                    f"risk buggy and undefined behavior? [YES-Y, NO-N]{ResetColor()}")
    else:
        ans = input(f"Are you sure you want to delete the template {name}? [YES-Y, NO-N]")
    if ans.upper() == "YES" or ans.upper() == "Y":
        shutil.rmtree(f"./Templates/{name}")
    else:
        print("aborted")


def export_template(*args, **kwargs):
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent

    # Step 1: Verify input
    if len(args) != 2:
        eprint("Wrong syntax.  The good syntax is: torchbuilder export-template <name> <destination>")
    name, destination = args
    if destination[0:2] == "./":
        absolute = False
        destination = destination[1:]
    elif destination[0] != "/":
        absolute = False
        destination = "/" + destination
    else:
        absolute = True
    if not absolute:
        destination = os.getcwd() + destination

    os.chdir(torchbuilder_path)

    if not name.replace("-", "").isalnum():
        eprint("Wrong template.  Template names must be composed of alphabet character or digits.")

    if not os.path.exists(f"./Templates/{name}"):
        eprint("Wrong template.  The template does not exist.")

    if not os.path.exists(PurePath(destination).parent):
        eprint("The destination directory does not exist.")

    if not os.path.exists(destination):
        os.mkdir(destination)

    # Compress the template
    with tarfile.open(f"{destination}/{name}.tar.gz", mode="w:gz") as tar:
        tar.add(f"./Templates/{name}", arcname="template")

    print(f"Template {name} successfully exported to {destination}/{name}.tar.gz")
    exit(0)

def import_template(*args, **kwargs):
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent

    # Step 1: Verify input
    if len(args) != 1:
        eprint("Wrong syntax.  The good syntax is: torchbuilder import-template <source>")
    source = args[0]
    if source[0:2] == "./":
        absolute = False
        source = source[1:]
    elif source[0] != "/":
        absolute = False
        source = "/" + source
    else:
        absolute = True
    if not absolute:
        source = os.getcwd() + source


    os.chdir(torchbuilder_path)

    if not os.path.exists(source):
        eprint("The source path does not exist.")

    matchs = re.findall(r'[A-Za-z0-9-]*\.', PurePath(source).name)
    if len(matchs) == 0:
        eprint("The source file is not a valid template file. (Invalid filename)")
    name = matchs[0].rstrip(".")

    if not name.replace("-", "").isalnum():
        print(name)
        eprint("Wrong template.  Template names must be composed of alphabet character, digits or hyphen.")

    available_templates = [PurePath(f.path).name for f in os.scandir("./Templates") if f.is_dir()]

    if name in available_templates:
        eprint("The template already exists.  You cannot create a template with the same name as an already "
               "existing template.  Remove the old one before creating a new one.")

    shutil.rmtree(f"./tmp", ignore_errors=True)

    # Extract the template
    with tarfile.open(source, mode="r:gz") as tar:
        tar.extractall(f"./tmp")

    # Move it with the goog name
    shutil.move(f"./tmp/template", f"./Templates/{name}")

    print(f"Template successfully imported from {source}")
    exit(0)