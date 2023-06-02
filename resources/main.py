import argparse
from utils.color import TraceBackColor, Color
import sys
sys.excepthook = TraceBackColor() # For better colors in Pycharm terminal: use parameter: tb_color=Color(203)
parser = argparse.ArgumentParser()

# ######################################################################################################################
# ------------------------------------------- Import here your experiments ------------------------------------------- #
# ######################################################################################################################
from experiments.experiment1 import experiment1



# ######################################################################################################################
# --------------------------------- Add here your arguments to pass to the experiment -------------------------------- #
# ######################################################################################################################
parser.add_argument("--experiment", required=True, type=str)
parser.add_argument("--config", required=True, type=str)


# ######################################################################################################################
# ------------------------------------------ Register you experiments here ------------------------------------------- #
# ######################################################################################################################
experiments = {
    "experiment1":experiment1,
}







if __name__ == "__main__":
    args = parser.parse_args()
    experiment = experiments.get(args.experiment)
    if experiment is None:
        raise ValueError(f"Invalid experiment name!  Available experiments are: \n{list(experiments.keys())}")
    experiment(args)
    print("Done!")