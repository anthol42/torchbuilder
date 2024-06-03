# DynamicMetric API

## Description
Class that facilitate keeping track of metrics and display it.  Works well with the Feedback class.

## How to use
1. Create a DynamicMetric object
2. Call the object when a new value comes to update the metric.

**Values are stored in attributes:**
- **values**: list of every recorded values
- **count**: number of values
- **sum**: sum of every values
- **avg**: mean of every values

## Examples
```python
loss = DynamicMetric(name="loss")

# Do training steps stuff
loss(step_loss)
```