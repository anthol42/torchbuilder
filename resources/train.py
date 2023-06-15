import torch
import torchvision
import numpy as np

from .train_one_epoch import train_one_epoch
from .validation_step import validation_step
from utils import RGBColor, eprint, FeedBack
import utils



def train(model, optimizer, train_loader, val_loader, criterion, num_epochs, device, config, scheduler=None):
    save_best_model = utils.SaveBestModel(
        config["model_dir"], metric_name="validation loss", model_name=config["model_name"], best_metric_val=float('inf'),
        evaluation_method='MIN')
    train_loss = []
    val_loss = []
    train_accuracy = []
    val_accuracy = []

    for epoch in range(num_epochs):
        # Setups
        eprint(f"Epoch {epoch + 1}/{num_epochs}", color=RGBColor(200,200,200))
        feedback = FeedBack(len(train_loader), output_rate=1, color=RGBColor(106,206,92))

        # Train the epoch and validate
        t_loss, t_acc = train_one_epoch(
            train_loader, model, optimizer, criterion, device, feedback, scheduler
        )
        v_loss, v_acc = validation_step(
            model, val_loader, criterion, device, feedback
        )

        # Save stats
        train_loss.append(t_loss)
        val_loss.append(v_loss)
        train_accuracy.append(t_acc)
        val_accuracy.append(v_acc)

        # Checkpoint
        save_best_model(np.array(v_loss).mean(), epoch, model, optimizer, criterion)

    return train_loss, val_loss, train_accuracy, val_accuracy


