import torch
import torchvision
import numpy as np
from metrics.dynamicMetric import DynamicMetric
from sklearn.metrics import accuracy_score

def validation_step(model, dataloader, criterion, device, feedback):
    model.eval()
    lossCounter = DynamicMetric(name='valid_loss')
    accCounter = DynamicMetric(name="accuracy")

    with torch.inference_mode():
        for X, y in dataloader:
            # Setup - Copying to gpu if available
            X, y = X.to(device), y.to(device)

            # Evaluating
            pred = model(X)
            loss = criterion(pred, y)

            # Calculate metrics
            lossCounter(loss)
            accCounter(accuracy_score(y, torch.argmax(pred, dim=1).detach().numpy()))

        # Display metrics
        feedback(
            valid=True,
            loss=lossCounter,
            accuracy=accCounter
        )

        # To add a distance between loading bar from feedback and other print
        print()

    return lossCounter.values, accCounter.values

