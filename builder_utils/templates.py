from .color import Color, ResetColor
from .compiler import Compiler
from .utils import eprint
import shutil

import os
from pathlib import PurePath
def compile(*args, **kwargs):
    # Step 1: Verify input
    if len(args) != 2:
        eprint("Wrong syntax.  The good syntax is: torchbuilder compile <name> <source_dir>")

    name, source = args
    if source[0:2] == "./":
        source = source[1:]
    elif source[0] != "/":
        source = "/" + source
    source = os.getcwd() + source
    torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
    os.chdir(torchbuilder_path)
    assert name.isalnum(), f"Only alphabet character and digits are allowed for Template names! Got: {name}"
    #Step 2: compile
    compiler = Compiler()
    if os.path.exists(f"./Templates/{name}"):
        raise ValueError("You cannot create a template that already exists.  Remove the old one before "
                         "creating a new one.")
    compiler(name, source)

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
    if not name.isalnum():
        eprint("Wrong template.  Template names must be composed of alphabet character or digits.")
    if not os.path.exists(f"./Templates/{name}"):
        eprint("Wrong template.  The template does not exist.")
    ans = input(f"Are you sure you want to delete the template {name}? [YES-Y, NO-N]")
    if ans.upper() == "YES" or ans.upper() == "Y":
        shutil.rmtree(f"./Templates/{name}")
    else:
        print("aborted")

