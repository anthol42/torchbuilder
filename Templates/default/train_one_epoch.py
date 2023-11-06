import torch
import torchvision
import numpy as np
from metrics.dynamicMetric import DynamicMetric
from sklearn.metrics import accuracy_score
from utils import State


def train_one_epoch(dataloader, model, optimizer, criterion, epoch, device, feedback, scheduler=None, scaler=None):
    model.train()
    lossCounter = DynamicMetric(name="loss")
    accCounter = DynamicMetric(name="accuracy")
    for X, y in dataloader:
        # Setup - Copying to gpu if available
        X, y = X.to(device), y.to(device)

        # Training with possibility of mixed precision
        if scaler:
            with torch.autocast(device_type=str(device), dtype=torch.float16):
                pred = model(X)
                loss = criterion(pred, y)
            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            pred = model(X)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        State.global_step += 1

        if scheduler:
            scheduler.step()

        # Calculate metrics
        accuracy = accuracy_score(y.cpu(), torch.argmax(pred, dim=1).detach().cpu().numpy())
        lossCounter(loss.item())
        accCounter(accuracy)

        State.writer.add_scalar('Step_Loss', loss.item(), State.global_step)
        State.writer.add_scalar('Step_Accuracy', accuracy, State.global_step)

        #Display metrics
        feedback(
            loss=lossCounter,
            accuracy=accCounter
        )

    State.train_loss[epoch] = lossCounter.values()
    State.train_accuracy[epoch] = accCounter.values()




