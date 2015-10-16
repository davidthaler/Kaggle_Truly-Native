from sklearn.metrics import roc_auc_score
from sklearn.cross_validation import cross_val_score
from datetime import datetime

def cv_sparse(model, x, y):
  '''
  Cross-validation for sparse-type features used in linear models.
  
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
  
