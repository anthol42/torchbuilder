import torch
import torchvision
import numpy as np
from data.dataloader import make_dataloader
from models.model import Classifier
from optimizers.optimizer import make_optimizer
from training.train import train
from losses.loss import make_loss
from schedulers.scheduler import make_scheduler
import yaml
import shutil
from utils.resultTable import Table

def experiment1(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rtable = Table("results/resultTable.json")
    resultSocket = rtable.registerRecord("experiment1", args.config, category=None)
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    train_loader, val_loader, test_loader = make_dataloader(config=config)
    print("Data loaded successfully!")

    model = Classifier(config=config)
    model.to(device)
    print("Model loaded successfully!")

    optimizer = make_optimizer(model.parameters(), config)
    loss = make_loss(config)
    scheduler = make_scheduler(config)

    print("Begining training...")
    train_loss, val_loss, train_accuracy, val_accuracy = train(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=loss,
        num_epochs=config["training_config"]["num_epochs"],
        device=device,
        scheduler=scheduler,
        config=config
    )
    print("Training done!  Saving...")
    resultSocket.write(accuracy=float(np.array(val_accuracy).mean()), crossEntropy=float(np.array(val_loss).mean()))
    rtable.toTxt()
    save_dict = {
        "epoch": config["training_config"]["num_epochs"],
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": train_loss,
        "val_loss": val_loss,
    }
    torch.save(
        save_dict, f"{config['model_dir']}/final_{config['model_name']}.pth")
    # Copy config file to model dir
    shutil.copy(args.config, config["model_dir"])


