import numpy as np
from sklearn.metrics import accuracy_score
def accuracy(targets, pred):
    hard_pred = np.argmax(pred, axis=1)
    return accuracy_score(targets, hard_pred)