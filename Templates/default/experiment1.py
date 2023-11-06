import torch
from torch.utils.tensorboard import SummaryWriter
import torchvision
import numpy as np
from data.dataloader import make_dataloader
from models import Classifier
from optimizers.optimizer import make_optimizer
from training.train import train
from losses.loss import make_loss
from schedulers.scheduler import make_scheduler
import sys
import shutil
from utils.resultTable import Table
import utils
from utils import State
import matplotlib.pyplot as plt

# To verify if the config has the good format
from configs.formats import config_format

def experiment1(args):
    # Setup
    device = utils.get_device()
    plt.style.use('torchbuilder_theme.mplstyle')
    hyper = utils.clean_dict(vars(args).copy())

    DEBUG = args.debug.upper().startswith("T")

    # Loading the config file
    config = utils.ConfigFile(args.config, config_format, verify_path=True)

    # Preparing Result Table
    rtable = Table("results/resultTable.json")
    sys.excepthook = rtable.handle_exception(sys.excepthook)
    resultSocket = rtable.registerRecord(__name__, args.config, category=None, **hyper)
    run_id = resultSocket.get_run_id()
    config["model"]["model_dir"] = f'{config["model"]["model_dir"]}/{run_id}'

    comment = '' if hyper.get("comment") is None else hyper.get("comment")
    State.writer = SummaryWriter(comment)
    # Loading the data
    train_loader, val_loader, test_loader = make_dataloader(config=config)
    print("Data loaded successfully!")

    # Loading the model
    model = Classifier(config)
    model.to(device)
    print("Model loaded successfully!")

    # Loading optimizer, loss and scheduler
    optimizer = make_optimizer(model.parameters(), config)
    loss = make_loss(config)
    scheduler = make_scheduler(optimizer, config)

    # Training
    print("Begining training...")
    train(
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

    save_dict = {
        "epoch": config["training"]["num_epochs"],
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": State.train_loss,
        "train_acc": State.train_accuracy,
        "val_loss": State.val_loss,
        "val_acc": State.val_accuracy
    }
    torch.save(
        save_dict, f"{config['model']['model_dir']}/final_{config['model']['model_name']}.pth")
    # Copy config file to model dir
    shutil.copy(args.config, config['model']["model_dir"])

    # Print stats of code
    print(config.stats())
    print(f"{utils.Color(11)}{State.warning()}{utils.ResetColor()}")

    State.writer.flush()
    State.writer.close()

    # Save results
    if DEBUG:
        resultSocket.ignore()
    else:
        best_idx = State.val_accuracy.argmax()
        resultSocket.write(accuracy=float(State.val_accuracy[best_idx]), crossEntropy=float(State.val_loss[best_idx]))
        rtable.toTxt()




