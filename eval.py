import numpy as np
from sklearn.metrics import roc_auc_score

def score(y_true, y_pred):
  '''
  Args:
    y_true - an ndarray of ground truth labels.
    y_pred - an ndarray of predictions.

  Returns:
    AUC score
  '''
  return roc_auc_score(y_true, y_pred)