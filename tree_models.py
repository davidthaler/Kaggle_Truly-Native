import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.externals import joblib
from sklearn.metrics import roc_auc_score
from datetime import datetime
import os
import argparse
import paths
import util

# This module imports pandas and sklearn, so it can't run under pypy.

def train_extra_trees(data, n_trees=100):
  '''
  Trains an sklearn ExtraTreesClassifier on the provided data.
  
  Args:
    data - a Pandas data frame with the filename, label, and features
    n_trees - number of trees to use in model
    
  Returns:
    ExtraTreesClassifier trained on provided data
  '''
  start = datetime.now()
  extra = ExtraTreesClassifier(n_estimators=n_trees, n_jobs=-1)
  extra.fit(data.drop(['file', 'sponsored'], 1), data.sponsored)
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return extra


def train_rf(data, n_trees=100):
  '''
  Trains an sklearn RandomForestClassifier on the provided data.
  
  Args:
    data - a Pandas data frame with the filename, label, and features
    n_trees - number of trees to use in model
    
  Returns:
    RandomForestClassifier trained on provided data
  '''
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
  
  
def predict(model, data):
  '''
  Make predictions from a provided ExtraTrees/RandomForest model and 
  return them in a data frame.
  
  Args:
    model - the model to use to make predictions
    data - a Pandas data frame with same structure as training data
  Returns:
    a Pandas data frame with columns used in submission: 'file' and 'sponsored'
  '''
  start = datetime.now()
  dv = model.predict_proba(data.drop(['file', 'sponsored'], 1))[:, 1]
  out = data[['file', 'sponsored']].copy()
  out['sponsored'] = dv
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return out  


def run_model(train_data, test_data, n_trees, submit_id, model, save_model=False):
  '''
  Trains a model of the specified type and size on the training data,
  then predicts on the test data and writes out a submission.
  
  Args:
    train_data - bare training feature set name without path or extension 
    test_data - bare test feature set name without path or extension
    n_trees - number of trees to use in model
    submit_id - the result is written as submissions/submission_<submit_id>.csv
    model - a string...either 'rf' or 'extra'
    save_model - default False. If true, use joblib to dump the model at:
      paths.MODELS/<submit_id>_model.job

  Writes:
    A submission at paths.SUBMIT/submisssion_<submit_id>.csv
  '''
  start = datetime.now()
  train = util.load_features(train_data)
  drops = util.get_drop_cols(train)
  train.drop(drops, axis=1, inplace=True)
  print 'training set size: (%d, %d)' % train.shape
  print 'Training...'
  if model == 'rf':
    model = train_rf(train, n_trees)
  else:
    model = train_extra_trees(train, n_trees)
  if save_model:
    model_path = os.path.join(paths.MODELS, submit_id + '_model.job')
    joblib.dump(model, model_path)
  del train
  print 'Predicting...'
  test = util.load_features(test_data)
  test.drop(drops, axis=1, inplace=True)
  print 'test set size: (%d, %d)' % test.shape
  result = predict(model, test)
  submission_name = 'submission_%s.csv' % str(submit_id)
  submission = os.path.join(paths.SUBMIT, submission_name)
  result.to_csv(submission, index=False)
  finish = datetime.now()
  print 'Run finished: %d sec.' % (finish - start).seconds


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 
          'Train an RF/ExtraTrees model, predict, and write a submission.')
  parser.add_argument('--train', type=str, required=True, help=
          'name of training feature file at data/processed w/o extension')
  parser.add_argument('--test', type=str, required=True, help=
          'name of test feature file at data/processed w/o extension')
  parser.add_argument('--model', type=str, required=True, 
          choices = ['rf','extra'], 
          help='type of model to train: rf or etxra(trees classifier)')
  parser.add_argument('--ntrees', type=int, required=True, help=
          'number of trees to use in model')
  parser.add_argument('--submit_id', type=str, required=True, help=
          'submission is written at submissions/submission_[submit].csv')
  args = parser.parse_args()
  run_model(args.train, args.test, args.ntrees, args.submit_id, args.model)

    












