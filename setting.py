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
        "datasets":{"dataset.py":File(fileToCopy="resources/dataset.py"),"__init__.py":File()},
        "dataloader.py":File(fileToCopy="resources/dataloader.py"),
        "__init__.py":File()
    },
    "models":{
        "model.py":File(fileToCopy="resources/model.py"),
        "__init__.py":File()
    },
    "losses":{
        "loss.py":File(fileToCopy="resources/loss.py"),
        "__init__.py":File()
    },
    "schedulers":{
        "scheduler.py": File(fileToCopy="resources/scheduler.py"),
        "__init__.py": File()
    },
    "logs": {
    },
    "scripts":{
        "train.sh":File(fileToCopy="resources/train.sh")
    },
    "configs":{
        "config.yml":File(fileToCopy="resources/config.yml")
    },
    "optimizers":{
        "optimizer.py":File(fileToCopy="resources/optimizer.py"),
        "__init__.py":File()
    },
    "metrics":{
        "metric.py":File(),
        "dynamicMetric.py":File(fileToCopy="resources/dynamicMetric.py"),
        "__init__.py":File()
    },
    "training":{
        "train_one_epoch.py":File(fileToCopy="resources/train_one_epoch.py"),
        "validation_step.py":File(fileToCopy="resources/validation_step.py"),
        "train.py":File(fileToCopy="resources/train.py"),
        "__init__.py":File()
    },
    "experiments":{
        "experiment1.py":File(fileToCopy="resources/experiment1.py"),
        "experiment1.md":File(fileToCopy="resources/experiment1.md"),
        "__init__.py":File()
    },
    "utils":{
        "feedback.py":File(fileToCopy="resources/feedback.py"),
        "checkpoint.py":File(fileToCopy="resources/checkpoint.py"),
        "resultTable.py":File(fileToCopy="resources/resultTable.py"),
        "color.py":File(fileToCopy="resources/color.py"),
        "__init__.py":File(fileToCopy="resources/utils_init.py")
    },
    "results":{
        "resultTable.json":File(fileToCopy="resources/resultTable.json")
    },
    "notebooks":{},
    "saved_models":{},
    "buildResultTable.py": File(fileToCopy="resources/buildResultTable.py"),
    "main.py":File(fileToCopy="resources/main.py"),
    "requirements.txt":File(fileToCopy="resources/requirements.txt"),
    "README.md":File(),
    "make_computeCan_venv.sh":File(fileToCopy="resources/make_computecan_venv.sh")
    ".gitignore": File(fileToCopy="resources/gitignore.txt"),
}