import torch
import utils
from utils import State, Color, DynamicMetric
import torchvision
from typing import *

def train_one_epoch(dataloader, model, optimizer, criterion, epoch, device, feedback, scheduler=None, scaler=None,
                    metrics: dict = None, sample_inputs: Optional[str] = None):
    if metrics is None:
        metrics = {}
    model.train()
    lossCounter = DynamicMetric(name="loss")
    metrics_counter = {k: DynamicMetric(name=k) for k in metrics.keys()}
    for i, (X, y) in enumerate(dataloader):
        if epoch == 0 and i == 0 and sample_inputs is not None:
            print(f"Saving sample inputs at {sample_inputs}")
            torch.save((X, y), sample_inputs)
        # Setup - Copying to gpu if available
        X, y = X.to(device), y.to(device)
        # for i in range(10_000):
        optimizer.zero_grad()
        # Training with possibility of mixed precision
        if scaler:
            with torch.autocast(device_type=str(device), dtype=torch.float16):
                pred = model(X)
                loss = criterion(pred, y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            pred = model(X)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()

        State.global_step += 1

        if scheduler:
            scheduler.step()

        # Calculate metrics
        metr = {}
        targets = y.detach().cpu().numpy()
        pred = pred.detach().cpu().numpy()
        if metrics is not None:
            for metric_name, metric_fn in metrics.items():
                metr[metric_name] = metric_fn(targets, pred)

            # print(f"{i} - Loss: {loss.item()}; {','.join(f'{metric}: {fn(targets, pred)}' for metric, fn in metrics.items())}")
        metr["loss"] = loss.item()

        # Report metrics
        State.writer.add_scalar('Step/Loss', metr["loss"], State.global_step)
        lossCounter(metr["loss"])
        for metric_name, value in metr.items():
            if metric_name in metrics_counter:
                metrics_counter[metric_name](value)
                State.writer.add_scalar(f'Step/{metric_name}', value, State.global_step)

        #Display metrics
        feedback(
            loss=lossCounter,
            **metrics_counter
        )

    # Report epochs metrics
    for metric_name, counter in metrics_counter.items():
        State.writer.add_scalar(f'Train/{metric_name}', counter.values().mean(), epoch)
    State.writer.add_scalar(f'Train/Loss', lossCounter.values().mean(), epoch)

@torch.inference_mode()
def validation_step(model, dataloader, criterion, epoch, device, feedback, metrics: dict = None):
    if metrics is None:
        metrics = {}
    model.eval()
    lossCounter = DynamicMetric(name="valid_loss")
    metrics_counter = {k: DynamicMetric(name=k) for k in metrics.keys()}

    for X, y in dataloader:
        # Setup - Copying to gpu if available
        X, y = X.to(device), y.to(device)

        # Evaluating
        pred = model(X)
        loss = criterion(pred, y)

        # Calculate metrics
        metr = {}
        targets = y.detach().cpu().numpy()
        pred = pred.detach().cpu().numpy()
        if metrics is not None:
            for metric_name, metric_fn in metrics.items():
                metr[metric_name] = metric_fn(targets, pred)
        metr["loss"] = loss.item()

        # Report metrics
        lossCounter(metr["loss"])
        for metric_name, value in metr.items():
            if metric_name in metrics_counter:
                metrics_counter[metric_name](value)

    # Display metrics
    feedback(
        valid=True,
        loss=lossCounter,
        **metrics_counter
    )

    # To add a distance between loading bar from feedback and other print
    print()

    # Report epochs metrics
    last_valid = {}
    for metric_name, counter in metrics_counter.items():
        State.writer.add_scalar(f'Valid/{metric_name}', counter.values().mean(), epoch)
        last_valid[metric_name] = counter.values().mean()
    State.writer.add_scalar(f'Valid/Loss', lossCounter.values().mean(), epoch)
    last_valid["loss"] = lossCounter.values().mean()
    State.last_valid = last_valid

def train(model, optimizer, train_loader, val_loader, criterion, num_epochs, device, config, scheduler=None,
          metrics: dict = None, noscaler: bool = False, watch: str = "accuracy", sample_inputs: Optional[str] = None):
    State.global_step = 0
    # Checkpoints
    m, b = ("MIN", float("inf")) if watch == "loss" else ("MAX", float('-inf'))
    print(f"Watching: {watch}")
    save_best_model = utils.SaveBestModel(
        config["model"]["model_dir"], metric_name=f"validation {watch}", model_name=config["model"]["name"],
        best_metric_val=b, evaluation_method=m)
    if str(device) == "cuda" and not noscaler:
        # For mixed precision training
        scaler = torch.amp.GradScaler()
    else:
        # We cannot do mixed precision on cpu or mps
        scaler = None

    for epoch in range(num_epochs):
        # Setup
        print(f"Epoch {epoch + 1}/{num_epochs}")
        output_rate = 25 if str(device) == 'cuda' else 1
        feedback = utils.FeedBack(len(train_loader), output_rate=output_rate, color=Color(112))

        # Train the epoch and validate
        train_one_epoch(
            train_loader, model, optimizer, criterion, epoch, device, feedback, scheduler, scaler, metrics, sample_inputs=sample_inputs
        )
        validation_step(
            model, val_loader, criterion, epoch, device, feedback, metrics
        )

        # Checkpoint
        save_best_model(State.last_valid[watch], epoch, model, optimizer, criterion)

@torch.inference_mode()
def evaluate(model, dataloader, criterion, device, metrics: dict = None):
    if metrics is None:
        metrics = {}
    model.eval()
    lossCounter = DynamicMetric(name="loss")
    metrics_counter = {k: DynamicMetric(name=k) for k in metrics.keys()}

    output_rate = 25 if str(device) == 'cuda' else 1
    feedback = utils.FeedBack(len(dataloader), output_rate=output_rate, color=Color(12))
    for X, y in dataloader:
        # Setup - Copying to gpu if available
        X, y = X.to(device), y.to(device)

        # Evaluating
        pred = model(X)
        loss = criterion(pred, y)

        # Calculate metrics
        metr = {}
        targets = y.detach().cpu().numpy()
        pred = pred.detach().cpu().numpy()
        if metrics is not None:
            for metric_name, metric_fn in metrics.items():
                metr[metric_name] = metric_fn(targets, pred)
        metr["loss"] = loss.item()

        # Report metrics
        lossCounter(metr["loss"])
        for metric_name, value in metr.items():
            if metric_name in metrics_counter:
                metrics_counter[metric_name](value)
        # Display metrics
        feedback(
            loss=lossCounter,
            **metrics_counter
        )

    # To add a distance between loading bar from feedback and other print
    print()

    # Report epochs metrics
    return dict(loss=lossCounter.values().mean(), **{k: v.values().mean() for k, v in metrics_counter.items()})
