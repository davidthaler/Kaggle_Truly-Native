from sklearn.metrics import roc_auc_score
from sklearn.cross_validation import cross_val_score
from datetime import datetime

def cv_sparse(model, x, y):
  '''
  Cross-validation for sparse-type features.
  
  Args:
    model - the model to train and validate
    x - a scipy.sparse matrix or numpy ndarray of features
    y - numpy 1-D array of class labels
  
  Returns:
    mean k-fold cv estimate for roc auc score
    an array of scores by fold
  '''
  start = datetime.now()
  scores = cross_val_score(model, x, y, scoring='roc_auc')
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return scores.mean(), scores
  

def score(y_true, y_pred):
  '''
  Args:
    y_true - an ndarray of ground truth labels.
    y_pred - an ndarray of predictions.

  Returns:
    AUC score
  '''
  return roc_auc_score(y_true, y_pred)