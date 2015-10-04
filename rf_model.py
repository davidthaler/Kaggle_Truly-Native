import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from datetime import datetime
import os
import paths

# Question: Do we want to save this RF?
def train_rf(data, n_trees=100):
  start = datetime.now()
  rf = RandomForestClassifier(n_estimators=n_trees,
                              n_jobs=-1,
                              oob_score=True)
  rf.fit(data.drop(['file', 'sponsored'], 1), data.sponsored)
  oob_auc = roc_auc_score(data.sponsored, rf.oob_decision_function_[:, 1])
  print 'auc score: %.5f' % oob_auc
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return rf
  
  
def predict_rf(rf, data):
  start = datetime.now()
  dv = rf.predict_proba(data.drop(['file', 'sponsored'], 1))[:, 1]
  out = data[['file', 'sponsored']].copy()
  out['sponsored'] = dv
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return out  


def run_rf(train_data, test_data, n_trees, submit_id):
  start = datetime.now()
  train_path = os.path.join(paths.PROCESSED, train_data + '.csv')
  train = pd.read_csv(train_path)
  rf = train_rf(train, n_trees)
  train_finish = datetime.now()
  print 'Training completed: %d sec.' % (train_finish - start).seconds
  test_path = os.path.join(paths.PROCESSED, test_data + '.csv')
  
  test = pd.read_csv(test_path)
  result = predict_rf(rf, test)
  submission_name = 'submission_%s.csv' % str(submit_id)
  submission = os.path.join(paths.SUBMIT, submission_name)
  result.to_csv(submission, index=False)
  finish = datetime.now()
  print 'Run finished: %d sec.' % (finish - start).seconds

