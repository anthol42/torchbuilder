# Checkpoint API
## Description
This class implement an easy to implement checkpoint to only save the best model.

## How it works
1. Initiate a SaveBestModel object with desired parameters.
2. Call the object after each epoch and the class will determine based on initial setup parameters whether the
   model is good enough to be saved.  (Better than previous ones)

It's that easy!

## Examples
```python
# Before the training loop:
save_best_model = SaveBestModel(
    "saved_models", 
    metric_name="validation loss",
    model_name="model_name", 
    best_metric_val=float('inf'),
    evaluation_method='MIN')

# In the training loop after each epoch:
save_best_model(np.array(v_loss).mean(), epoch, model, optimizer, criterion)
```

## Methods

```python
__init__(save_dir, metric_name, model_name, best_metric_val, evaluation_method='MAX')
```
     Setup the SaveBestModel object
     :param save_dir: directory where to save the checkpoints
     :param metric_name: The name of the metric that we are using to measure the best model
     :param model_name: The name of the model to be saved
     :param best_metric_val: Initial metric that needs to be beaten in order to save the model.  Usually inf or -inf
     :param evaluation_method: 'MAX' or 'MIN' Whether the goal is to maximise the metric or minimize it.
```python
__call__(self, current_val, epoch, model, optimizer, criterion=None, outputMessage="")
```
     Call after each epoch
     :param current_val: Current metric value
     :param epoch: the current epoch
     :param model: the model to save
     :param optimizer: the optimizer
     :param criterion: the loss object
     :param outputMessage: the message to output when the model is saved.