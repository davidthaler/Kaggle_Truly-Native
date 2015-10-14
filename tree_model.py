import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import roc_auc_score
from datetime import datetime
import os
import argparse
import paths
import util


def train_extra_trees(data, n_trees=100):
  start = datetime.now()
  extra = ExtraTreesClassifier(n_estimators=n_trees, n_jobs=-1)
  extra.fit(data.drop(['file', 'sponsored'], 1), data.sponsored)
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return extra


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
  
  
def predict(model, data):
  start = datetime.now()
  dv = model.predict_proba(data.drop(['file', 'sponsored'], 1))[:, 1]
  out = data[['file', 'sponsored']].copy()
  out['sponsored'] = dv
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return out  


def run_model(train_data, test_data, n_trees, submit_id, model):
  start = datetime.now()
  train = util.load_features(train_data)
  drops = util.get_drop_cols(train)
  train.drop(drops, axis=1, inplace=True)
  print 'Training...'
  if model == 'rf':
    model = train_rf(train, n_trees)
  else:
    model = train_extra_trees(train, n_trees)
  del train
  print 'Predicting...'
  test = util.load_features(test_data)
  test.drop(drops, axis=1, inplace=True)
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
  parser.add_argument('--submit', type=str, required=True, help=
          'submission is written at submissions/submission_[submit].csv')
  args = parser.parse_args()
  run_model(args.train, args.test, args.ntrees, args.submit, args.model)

    












