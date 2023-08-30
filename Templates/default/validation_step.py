import torch
import torchvision
import numpy as np
from metrics.dynamicMetric import DynamicMetric
from sklearn.metrics import accuracy_score
from utils import State
import torch.nn.functional as F
@torch.inference_mode()
def validation_step(model, dataloader, criterion, epoch, device, feedback):
    model.eval()
    lossCounter = DynamicMetric(name='valid_loss')
    accCounter = DynamicMetric(name="accuracy")


    for X, y in dataloader:
        # Setup - Copying to gpu if available
        X, y = X.to(device), y.to(device)

        # Evaluating
        pred = model(X)
        loss = criterion(pred, y)

        # Calculate metrics
        lossCounter(loss.item())
        accCounter(accuracy_score(y.cpu(), torch.argmax(F.softmax(pred, dim=1), dim=1).detach().cpu().numpy()))

    # Display metrics
    feedback(
        valid=True,
        loss=lossCounter,
        accuracy=accCounter
    )

    # To add a distance between loading bar from feedback and other print
    print()

    State.val_loss[epoch] = lossCounter.avg
    State.val_accuracy[epoch] = accCounter.avg



