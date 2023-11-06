import torch
import torchvision
import numpy as np

from .train_one_epoch import train_one_epoch
from .validation_step import validation_step
import utils
from utils import State
from utils import Color


def train(model, optimizer, train_loader, val_loader, criterion, num_epochs, device, config, scheduler=None):
    State.global_step = 0
    # Checkpoints
    save_best_model = utils.SaveBestModel(
        config["model"]["model_dir"], metric_name="validation accuracy", model_name=config["model"]["model_name"],
        best_metric_val=float('-inf'), evaluation_method='MAX')
    if str(device) == "cuda":
        # For mixed precision training
        scaler = torch.cuda.amp.GradScaler()
    else:
        # We cannot do mixed precision on cpu or mps
        scaler = None

    n_step = len(train_loader)
    State.train_loss = np.empty((num_epochs, n_step))
    State.val_loss = np.empty((num_epochs, ))
    State.train_accuracy = np.empty((num_epochs, n_step))
    State.val_accuracy = np.empty((num_epochs, ))

    for epoch in range(num_epochs):
        # Setup
        print(f"Epoch {epoch + 1}/{num_epochs}")
        output_rate = 25 if str(device) == 'cuda' else 1
        feedback = utils.FeedBack(len(train_loader), output_rate=output_rate, color=Color(112))

        # Train the epoch and validate
        train_one_epoch(
            train_loader, model, optimizer, criterion, epoch, device, feedback, scheduler, scaler
        )
        validation_step(
            model, val_loader, criterion, epoch, device, feedback
        )

        State.writer.add_scalar('Loss/train', State.train_loss[epoch].mean(), epoch)
        State.writer.add_scalar('Loss/Validation', State.val_loss[epoch], epoch)

        State.writer.add_scalar('Accuracy/train', State.train_accuracy[epoch].mean(), epoch)
        State.writer.add_scalar('Accuracy/Validation', State.val_accuracy[epoch], epoch)

        # Checkpoint
        save_best_model(State.val_accuracy[epoch], epoch, model, optimizer, criterion)




