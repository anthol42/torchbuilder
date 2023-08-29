import argparse
from utils.color import TraceBackColor, Color
import sys
from datetime import datetime
sys.excepthook = TraceBackColor()
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
parser.add_argument("--debug", required=False, type=str, default="False")


# ######################################################################################################################
# ------------------------------------------ Register you experiments here ------------------------------------------- #
# ######################################################################################################################
experiments = {
    "experiment1":experiment1,
}







if __name__ == "__main__":
    start = datetime.now()
    args = parser.parse_args()
    experiment = experiments.get(args.experiment)
    if experiment is None:
        raise ValueError(f"Invalid experiment name!  Available experiments are: \n{list(experiments.keys())}")
    experiment(args)
    end = datetime.now()
    print(f"Done!  Total time: {(end - start)}")

