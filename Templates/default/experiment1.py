import torch
from torch.utils.tensorboard import SummaryWriter
import torchvision
import numpy as np
import os
from data.dataloader import make_dataloader
from models import Classifier
from optimizers.optimizer import make_optimizer
from training.train import train, evaluate
from losses.loss import make_loss
from schedulers.scheduler import make_scheduler
import sys
import shutil
from utils.resultTable import Table
import utils
from utils.bin import *
from utils import State
import matplotlib.pyplot as plt
from metrics import accuracy
from torchinfo import summary
# To verify if the config has the good format
from configs.formats import config_format

metrics = {
    "accuracy": accuracy,
}


def experiment1(args, kwargs):
    # Setup
    device = utils.get_device()
    plt.style.use('torchbuilder_theme.mplstyle')
    hyper = utils.clean_dict(vars(args).copy())

    DEBUG = args.debug

    # Loading the config file
    config = utils.ConfigFile(args.config, config_format, verify_path=True)
    config.override_config(kwargs)

    # Preparing Result Table
    rtable = Table("results/resultTable.json")
    sys.excepthook = rtable.handle_exception(sys.excepthook)
    if DEBUG:
        run_id = "DEBUG"
        log(f"Running in {Color(203)}DEBUG{ResetColor()} mode!")
    else:
        resultSocket = rtable.registerRecord(__name__, args.config, category=None, **hyper)
        run_id = resultSocket.get_run_id()

    config["model"]["model_dir"] = f'{config["model"]["model_dir"]}/{run_id}'

    comment = '' if hyper.get("comment") is None else hyper.get("comment")
    if os.path.exists(f'runs/{run_id}'):
        log(f"Clearing tensorboard logs for id: {run_id}")
        shutil.rmtree(f'runs/{run_id}')
    State.writer = SummaryWriter(log_dir=f'runs/{run_id}', comment=comment)
    # Loading the data
    train_loader, val_loader, test_loader = make_dataloader(config=config)
    log("Data loaded successfully!")

    # Loading the model
    model = Classifier(config)
    model.to(device)
    summary(model, input_size=(config["data"]["batch_size"], 1, 28, 28), device=device)
    log("Model loaded successfully!")

    # Loading optimizer, loss and scheduler
    optimizer = make_optimizer(model.parameters(), config)
    loss = make_loss(config)
    scheduler = make_scheduler(optimizer, config)

    # Training
    # Prepare the path of input sampling if flag is set
    if args.sample_inputs:
        sample_inputs = f"{config['model']['model_dir']}/inputs.pth"
    else:
        sample_inputs = None
    log("Begining training...")
    try:
        train(
            model=model,
            optimizer=optimizer,
            train_loader=train_loader,
            val_loader=val_loader,
            criterion=loss,
            num_epochs=config["training"]["num_epochs"],
            device=device,
            scheduler=scheduler,
            config=config,
            metrics=metrics,
            watch=args.watch,
            sample_inputs=sample_inputs
        )
    except KeyboardInterrupt:
        log("Keyboard Interrupt detected. Ending training...", start="\n", end="\n\n")

    log("Training done!  Saving...")

    # Load best model
    log("Loading best model")
    weights = torch.load(f'{config["model"]["model_dir"]}/{config["model"]["name"]}.pth', weights_only=False)[
        "model_state_dict"]
    model.load_state_dict(weights)
    # Test
    results = evaluate(model, test_loader, loss, device, metrics=metrics)
    log("Training done!  Saving...")

    save_dict = {
        "epoch": config["training"]["num_epochs"],
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "test_loss": results["loss"],
        "test_acc": results["accuracy"]
    }
    torch.save(
        save_dict, f"{config['model']['model_dir']}/final_{config['model']['name']}.pth")
    # Copy config file to model dir
    shutil.copy(args.config, config['model']["model_dir"])

    # Print stats of code
    print(config.stats())
    print(f"{utils.Color(11)}{State.warning()}{utils.ResetColor()}")

    State.writer.flush()
    State.writer.close()

    # Save results
    if not DEBUG:
        resultSocket.write(accuracy=results["accuracy"], crossEntropy=results["loss"])
        rtable.toTxt()




