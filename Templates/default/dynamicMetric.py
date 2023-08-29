import numpy as np


class DynamicMetric:
    """
    Class that facilitate keeping track of metrics and display it.  Works well with the Feedback class.

    How to use:
        1. Create a DynamicMetric object
        2. Call the object when a new value comes to update the metric.

    Values are stored in attributes:
        - values: list of every recorded values
        - count: number of values
        - sum: sum of every values
        - avg: mean of every values

    Examples:
        >>> loss = DynamicMetric(name="loss")

        >>> # Do training steps stuff

        >>> loss(step_loss)
    """
    def __init__(self, name="metric"):
        """
        Initiate the metric value
        :param name: Name of the metric
        """
        self.name=name
        self._values = []
        self.count = 0
        self.sum = 0
        self.avg = 0

    def __call__(self, value):
        """
        This method updates the the counter
        :param value: value of the step
        :return: None
        """
        self._values.append(value)
        self.count += 1
        self.sum += value
        self.avg = self.sum / self.count

    def values(self) -> np.ndarray:
        """
        return values as numpy array
        :return: values
        """
        return np.array(self._values)
    def __str__(self):
        return str(self.avg)

if __name__ == "__main__":
    import time
    loss = DynamicMetric(name="loss")
    for i in range(100):
        loss(i)
        print(f"\r{loss}", end="")
        time.sleep(0.1)


