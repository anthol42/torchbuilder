# Made by: Anthony Lavertu
# Initial release: 2023-06-05
# File: main.py
"""
Class that represent a file in the filetree
"""
class File:
    def __init__(self, content="", fileToCopy=None):
        """
        :param content: The content to wright to the file.
        :param fileToCopy: The content to wright to the file from an other file

        Note: If you pass a fileToCopy and a content, the content will be append to the end of the file with two \n
              between.
        """
        if fileToCopy:
            with open(fileToCopy, 'r') as file:
                self.content = file.read() + "\n\n" + content
        else:
            self.content = content

filetree = {
    "data":{
        "datasets":{"dataset.py":File(fileToCopy="ressources/dataset.py"),"__init__.py":File()},
        "dataloader.py":File(fileToCopy="ressources/dataloader.py"),
        "__init__.py":File()
    },
    "models":{
        "model.py":File(fileToCopy="ressources/model.py"),
        "__init__.py":File()
    },
    "losses":{
        "loss.py":File(fileToCopy="ressources/loss.py"),
        "__init__.py":File()
    },
    "schedulers":{
        "scheduler.py": File(fileToCopy="ressources/scheduler.py"),
        "__init__.py": File()
    },
    "logs": {
    },
    "scripts":{
        "train.sh":File(fileToCopy="ressources/train.sh")
    },
    "configs":{
        "config.yml":File(fileToCopy="ressources/config.yml")
    },
    "optimizers":{
        "optimizer.py":File(fileToCopy="ressources/optimizer.py"),
        "__init__.py":File()
    },
    "metrics":{
        "metric.py":File(),
        "dynamicMetric.py":File(fileToCopy="ressources/dynamicMetric.py"),
        "__init__.py":File()
    },
    "training":{
        "train_one_epoch.py":File(fileToCopy="ressources/train_one_epoch.py"),
        "validation_step.py":File(fileToCopy="ressources/validation_step.py"),
        "train.py":File(fileToCopy="ressources/train.py"),
        "__init__.py":File()
    },
    "experiments":{
        "experiment1.py":File(fileToCopy="ressources/experiment1.py"),
        "experiment1.md":File(fileToCopy="ressources/experiment1.md"),
        "__init__.py":File()
    },
    "utils":{
        "feedback.py":File(fileToCopy="ressources/feedback.py"),
        "checkpoint.py":File(fileToCopy="ressources/checkpoint.py"),
        "resultTable.py":File(fileToCopy="ressources/resultTable.py"),
        "color.py":File(fileToCopy="ressources/color.py"),
        "__init__.py":File(fileToCopy="ressources/utils_init.py")
    },
    "results":{
        "resultTable.json":File(fileToCopy="ressources/resultTable.json")
    },
    "notebooks":{},
    "saved_models":{},
    "buildResultTable.py": File(fileToCopy="ressources/buildResultTable.py"),
    "main.py":File(fileToCopy="ressources/main.py"),
    "requirements.txt":File(fileToCopy="ressources/requirements.txt"),
    "README.md":File(),
    "make_computeCan_venv.sh":File(fileToCopy="ressources/make_computecan_venv.sh"),
    ".gitignore": File(fileToCopy="ressources/gitignore.txt"),
}