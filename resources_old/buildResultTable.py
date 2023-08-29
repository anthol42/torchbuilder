from .resultTable import TableBuilder
from pathlib import PurePath

if __name__ == "__main__":
    TableBuilder(["accuracy", "crossEntropy"], PurePath("results/resultTable.json")).build()