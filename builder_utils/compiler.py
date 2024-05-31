import os
import sys
import glob
from pathlib import PurePath
import json
from typing import Union, Tuple, List
import re

IGNORED_DIR = {"__pycache__", ".git", ".idea", ".vscode", ".config", ".cache", "venv", "env", ".venv", ".env"}
HIDDEN_FILE_KEPT = {".gitignore", ".gitkeep", ".env"}


def isMatch(s: str, regex: List[str]):
    regex = [re.compile(r) for r in regex]
    for r in regex:
        if r.match(s):
            return True
    return False

class _Project:
    def __init__(self, name: str, path: Union[str, PurePath],
                 ignore_files: List[str], ignore_dirs: List[str]):
        ignore_dirs = [i[:-1] for i in ignore_dirs]    # Remove the trailing '/'
        ignore_dirs += list(ignore_dirs)
        self.name = name
        self.path = path

        child_dirs = [PurePath(f.path) for f in os.scandir(path) if f.is_dir()]
        self._childs = {}
        if len(child_dirs) > 0:
            for child_dir in child_dirs:
                if not child_dir.name in IGNORED_DIR and not isMatch(child_dir.name, ignore_dirs):
                    self._childs[child_dir.name] = _Project(child_dir.name, str(child_dir), ignore_files, ignore_dirs)
        self.files = {}
        for f in os.scandir(path):
            if f.is_file():
                if isMatch(f.name, ignore_files):
                    continue
                if not f.name.startswith(".") or f.name in HIDDEN_FILE_KEPT:
                    self.files[PurePath(f.path).name] = f.path
    @staticmethod
    def _increment_name(name):
        # First, extract extension
        ext_parts = name.split(".")
        extension = ext_parts[-1]
        name = name.replace(f".{extension}", "")
        # Extract id and increment it.
        parts = name.split("_")
        sidx: str = parts[-1]
        if sidx.isdigit():
            idx: int = int(sidx) + 1
            text: str = "_".join(parts[:-1])
        else:
            idx: int = 1
            text: str = "_".join(parts)

        return text + f"_{idx}.{extension}"

    def flatten(self, data: dict = {}):
        """
        Returns a dictionary with each key, the id of the file (alias), and the value its real name and relative path.
        :param data: The previously flatten data
        :return: data with new entries added
        """
        for file in self.files:
            alias = file
            # Make sure id is unique
            while alias in data:
                alias = self._increment_name(alias)
            data[alias] = f"{self.path}/{file}"

        for child_name, child in self._childs.items():
            data = child.flatten(data)

        return data

    def info(self) -> Tuple[int, int]:
        """
        This method will give info about the current project:
        it will return the total number of files and directories.
        :return: n files, n dir
        """
        n_files = len(self.files)
        n_dirs = len(self._childs)

        for child in self._childs.values():
            files, dirs = child.info()
            n_files += files
            n_dirs += dirs

        return n_files, n_dirs

    def _toStr(self, offset: int = 0):
        spacing = "  "
        s = f"{spacing*offset}{self.name}:\n"
        n_files, n_dir = self.info()
        dir_name = "directory" if n_dir == 0 or n_dir == 1 else "directories"
        file_name = "file" if n_files == 0 or n_files== 1 else "files"
        s += f"{spacing*offset}[<{n_files} {file_name}>--<{n_dir} {dir_name}>]\n"
        for file in self.files:
            s += f"{spacing*offset + spacing}{file}\n"

        for child in self._childs.values():
            s += child._toStr(offset+1)

        return s

    def __str__(self):
        return self._toStr()

    def dict(self):
        d = {}
        for filename, path in self.files.items():
            d[filename] = path

        for directory, child in self._childs.items():
            d[directory] = child.dict()

        return d




class Compiler:
    """
    This class contains the engine to compile a project structure with boilerplates to a torchbuiler template
    """

    def __init__(self):
        pass

    @staticmethod
    def extract_tree(template_name: str, base_path: Union[str, PurePath],
                     ignore_files: List[str], ignore_dirs: List[str]) -> Tuple[dict, str, dict]:
        """
        This method will flatten the project's complex tree structure and convert it to a non-nested dictionary.
        In addition, it will convert the nested tree structure to a string for easy visualization
        :param template_name: The name of the template
        :param base_path: The base path of the project
        :param ignore_files: The list of regex expression defining the files to ignore
        :param ignore_dirs: The list of regex expression defining the directories to ignore (Expression ends by '/')
        :return: The flatten tree, the tree as a string, and the tree mapped as a nested dict
        """
        project = _Project(template_name, base_path , ignore_files, ignore_dirs)
        return project.flatten(), str(project), project.dict()

    @staticmethod
    def write_files(out_path: Union[str, PurePath], flatten_project: dict, txt_project: str = None):
        """
        This method follow the extract_tree method and needs the project flatten: dict{alias: filepath}
        :param out_path: The path where to save the files.
        :param flatten_project: The project flatten as a dict in the shape: dict{alias: filepath}
        :param txt_project: The project in a text format (like output by extract_tree).
                            It will be saved as template_format.txt
        :return: None
        """
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        for filename, in_path in flatten_project.items():
            # Step 1: Read the source file
            with open(in_path, "rb") as infile:
                content = infile.read()

            with open(f"{out_path}/{filename}", "wb") as oufile:
                oufile.write(content)

        if txt_project:
            with open(f"{out_path}/template_format.txt", "w") as oufile:
                oufile.write(txt_project)

    def _recursive_link(self, project: dict, project_flatten_inv: dict, outpath: str):
        """
        This function will recursively assign the good alias to each leaf of the project dict.
        :param project: The project structure as a dict
        :param project_flatten_inv: The inverted flatten project: the path are the keys, and the alias the value.
        :param outpath: The root of where the template is stores
        :return: Linked project
        """
        data = {}
        for key, value in project.items():
            if isinstance(value, dict):
                data[key] = self._recursive_link(project[key], project_flatten_inv, outpath)
            else:
                data[key] = f"{outpath}/{project_flatten_inv[value]}"
        return data


    def link(self, project: dict, project_flatten: dict, out_path: Union[str, PurePath]):
        """
        This function will link every file together in an .index.json file in the .config directory
        :param out_path: The output path
        :param project: The nested dict representing the project structure
                :param outpath: The root of where the template is stores
        :return: None
        """

        # Step 1: Invert the project_flatten
        project_flatten_inv = {value: key for key, value in project_flatten.items()}

        linked = self._recursive_link(project, project_flatten_inv, out_path)

        if not os.path.exists(f"Templates/{out_path}/.config"):
            os.makedirs(f"Templates/{out_path}/.config")

        with open(f"Templates/{out_path}/.config/.index.json", "w") as file:
            json.dump(linked, file)

    def __call__(self, template_name: str, source_project: Union[str, PurePath], ignore_files: List[str], ignore_dirs: List[str]):
        """
        This function implement the whole pipeline to extract the tree of the project, write the files in the
        Template's folder, then link files
        :param template_name: The name to use for the template
        :param source_project: The ABSOLUTE PATH of the source project to use as a template
        :param ignore_files: The list of regex expression defining the files to ignore
        :param ignore_dirs: The list of regex expression defining the directories to ignore (Expression ends by '/')
        :return: None
        """
        torchbuilder_path = PurePath(os.path.dirname(__file__)).parent
        proj_flatten, txt, project = self.extract_tree(template_name,
                                                           source_project,
                                                           ignore_files,
                                                           ignore_dirs)
        self.write_files(f"{torchbuilder_path}/Templates/{template_name}", proj_flatten, txt)
        self.link(project, proj_flatten, f"{template_name}")






if __name__ == "__main__":
    compiler = Compiler()
    compiler("Test", "/media/anthony/Documents/WD/activeAnomalyDetection/mnist1")