import torch
import torchvision
import numpy as np
from data.dataloader import make_dataloader
from models.model import Classifier
from optimizers.optimizer import make_optimizer
from training.train import train
from losses.loss import make_loss
from schedulers.scheduler import make_scheduler
import sys
import shutil
from utils.resultTable import Table
import utils
import matplotlib.pyplot as plt

config_format = {
    "data":{
        "batch_size": int,
        "shuffle": bool
    },
    "training":{
        "num_epochs": int,
        "learning_rate": float,
        "weight_decay": float,
    },
    "model_dir": "opath",
    "model_name": "opath"
}

def experiment1(args):
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    plt.style.use('torchbuilder_theme.mplstyle')
    hyper = vars(args).copy()
    hyper.pop("config")
    hyper.pop("experiment")
    hyper.pop("debug")
    hyper = utils.clean_dict(hyper)
    DEBUG = args.debug.upper().startswith("T")

    # Loading the config file
    config = utils.ConfigFile(args.config, config_format, verify_path=True)

    # Preparing Result Table
    rtable = Table("results/resultTable.json")
    sys.excepthook = rtable.handle_exception(sys.excepthook)
    resultSocket = rtable.registerRecord("experiment1", args.config, category=None, **hyper)

    # Loading the data
    train_loader, val_loader, test_loader = make_dataloader(config=config)
    print("Data loaded successfully!")

    # Loading the model
    model = Classifier(config=config)
    model.to(device)
    print("Model loaded successfully!")

    # Loading optimizer, loss and scheduler
    optimizer = make_optimizer(model.parameters(), config)
    loss = make_loss(config)
    scheduler = make_scheduler(config)

    # Training
    print("Begining training...")
    train_loss, val_loss, train_accuracy, val_accuracy = train(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=loss,
        num_epochs=config["training"]["num_epochs"],
        device=device,
        scheduler=scheduler,
        config=config
    )
    print("Training done!  Saving...")

    # Evaluating
        # For this demo, we did not provide any evaluation process

    # Save results
    if DEBUG:
        resultSocket.ignore()
    else:
        resultSocket.write(accuracy=float(np.array(val_accuracy).mean()), crossEntropy=float(np.array(val_loss).mean()))
        rtable.toTxt()
    save_dict = {
        "epoch": config["training"]["num_epochs"],
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": train_loss,
        "val_loss": val_loss,
    }
    torch.save(
        save_dict, f"{config['model_dir']}/final_{config['model_name']}.pth")
    # Copy config file to model dir
    shutil.copy(args.config, config["model_dir"])

    # Print stats of config to see if there are any keys that aren't necessary anymore.
    print(config.stats())




