import torch
import torchvision
import numpy as np
from metrics.dynamicMetric import DynamicMetric
from sklearn.metrics import accuracy_score


def train_one_epoch(dataloader, model, optimizer, criterion, device, feedback, scheduler=None):
    model.train()
    lossCounter = DynamicMetric(name="loss")
    accCounter = DynamicMetric(name="accuracy")
    for X, y in dataloader:
        # Setup - Copying to gpu if available
        X, y = X.to(device), y.to(device)

        # Training
        optimizer.zero_grad()
        pred = model(X)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()
        if scheduler:
            scheduler.step()

        # Calculate metrics
        lossCounter(loss)
        accCounter(accuracy_score(y.cpu(), torch.argmax(pred.cpu(), dim=1).detach().cpu().numpy()))

        #Display metrics
        feedback(
            loss=lossCounter,
            accuracy=accCounter
        )

    return lossCounter.values, accCounter.values


