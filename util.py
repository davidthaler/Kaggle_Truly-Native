import pandas as pd
import numpy as np
import os
import gzip
from math import log
from datetime import datetime
from sklearn.datasets import load_svmlight_file
from sklearn.preprocessing import normalize
from sklearn.preprocessing import scale
from sklearn.externals import joblib
import artifacts
import paths

# This module imports pandas and sklearn, so it can't run under pypy

def load_sparse(feature_set_name,
                n_features, 
                log_transform=True, 
                row_normalize=True):
  '''
  Utility function to load a sparse feature set for linear models.
  Features must be in LibSVM format. 
  Must be located at data/processed<feature_set_name>.libsvm
  
  Args:
    feature_set_name - just the filename, w/o path or extension
    n_features - probably 2**20, see sparse_features.py
    log_transform - if True, transform counts with log1p
    row_normalize - if True, L2 normalize rows after log transform (if used)
    
  Returns:
    x - scipy.sparse.csr matrix of features
    y - numpy 1-D array of labels
  '''
  start = datetime.now()
  cached = os.path.join(paths.TMP, feature_set_name + '.job')
  if os.path.isfile(cached):
    x, y = joblib.load(cached)
  else:
    path = os.path.join(paths.PROCESSED, feature_set_name + '.libsvm')
    x, y = load_svmlight_file(path, n_features=n_features)
    joblib.dump((x, y), cached)
  if log_transform:
    x = x.log1p()
  if row_normalize:
    x = normalize(x)
  finish = datetime.now()
  print 'elapsed time: %d sec.' % (finish - start).seconds
  return x, y


def load_features(feature_set_name):
  '''
  Utility function to load a feature set with filename <feature_set_name.csv>
  at path data/processed.
  '''
  path = os.path.join(paths.PROCESSED, feature_set_name + '.csv')
  out = pd.read_csv(path)
  out.fillna(0, inplace=True)
  return out


def load_train(as_dict):
  '''
  Loads full training set, including labels, as either a data frame or a dict.
  Rewrites label to a python int (it comes in as numpy.int64) so that we can 
  use this dict with pypy, if as_dict is True.
  
  Args:
    as_dict - If True, return a dict from filenames to labels
        instead of a data frame.

  Returns:
    the training data either as a data frame, 
    or as a dict from filenames to labels.
  '''
  tr = pd.read_csv(paths.TRAIN)
  if as_dict:
    # prevents numpy.int64 from getting into the dict and killing pypy
    labels = [int(x) for x in tr.sponsored]
    return dict(zip(tr.file, labels))
  else:
    return tr


def test_dict():
  '''
  Makes a dict with label of 0 (as python int) for use in some routines.
  '''
  test = sample_submission()
  labels = [0] * len(test.file)
  return dict(zip(test.file, labels))


def train_ids():
  '''
  Loads the training set ids into a set.
  '''
  tr = pd.read_csv(paths.TRAIN)
  return set(tr.file)


def create_sample(outfile, n_pos, n_neg):
  '''
  Creates a dict describing a specific sample of rows and saves 
  it at ARTIFACTS with form {filename : label}. Rewrites label 
  to a python int (it comes in as numpy.int64) so that we can 
  use this dict with pypy.
  
  args:
    outfile - the dict is written at ARTIFACTS/<outfile>.pkl
    n_pos - approximate number of positive instances in sample
    n_neg - approximate number of negative instances in sample
    
  return:
    nothing, but dict is pickled at ARTIFACT/<outfile>.pkl
  '''
  tr = load_train(False)
  tr_pos = tr[tr.sponsored == 1]
  tr_pos = tr_pos.sample(n_pos)
  tr_neg = tr[tr.sponsored == 0]
  tr_neg = tr.sample(n_neg)
  sample_df = tr_pos.append(tr_neg)
  # We need this to prevent the pickled sample dict from containing a 
  # numpy.int64, which prevents using pypy
  labels = [int(x) for x in sample_df.sponsored]
  sample = dict(zip(sample_df.file, labels))
  artifacts.put_artifact(sample, outfile)


def write_submission(pred, submit_id):
  s1 = os.path.join(paths.SUBMIT, 'submission_1.csv.gz')
  result = pd.read_csv(s1, compression='gzip')
  result.sponsored = pred
  submission_name = 'submission_%s.csv' % str(submit_id)
  submission = os.path.join(paths.SUBMIT, submission_name)
  result.to_csv(submission, index=False)


def combine_dvs(dv_subs, prob_subs, clip_at, submit_id):
  '''
  Take lists of filenames of submissions in .csv or .csv.gz format and 
  combine them into one submission. 
  Outputs of models that output probabilities are clipped and converted 
  to log-odds and then averaged together. 
  Outputs of models that output log-odds or decision values are just averaged. 
  The two averaged predictions are then standard-scaled and added.
  Filenames should be with extension but without path.
  The files must be at BASE/submissions
  
  Args:
    prob_subs - list of str. - filenames of probability-scale submissions
    dv_subs - list of str. - filenames of log-odds scale (or dv) entries
    clip_at - the probabilities are clipped at [clip_at, 1 - clip_at]
    submit_id - the result is written as submissions/submission_<submit_id>.csv
  '''
  logodds = lambda x : log(x/(1 - x))
  all_odds = None
  for sub_name in prob_subs:
    path = os.path.join(paths.SUBMIT, sub_name)
    if sub_name.endswith('.gz'):
      sub = pd.read_csv(path,  compression='gzip')
    else:
      sub = pd.read_csv(path)
    pred = sub.sponsored.clip(lower = clip_at, upper = 1 - clip_at)
    pred = pred.apply(logodds)
    if all_odds is None:
      all_odds = pred
    else:
      all_odds += pred
  all_odds = all_odds / len(prob_subs)
  all_odds = scale(all_odds)
  
  all_dvs = None
  for sub_name in dv_subs:
    path = os.path.join(paths.SUBMIT, sub_name)
    if sub_name.endswith('.gz'):
      sub = pd.read_csv(path,  compression='gzip')
    else:
      sub = pd.read_csv(path)
    if all_dvs is None:
      all_dvs = sub.sponsored
    else:
      all_dvs += sub.sponsored
  all_dvs = all_dvs / len(dv_subs)
  all_dvs = scale(all_dvs)
  
  result = all_dvs + all_odds
  write_submission(result, submit_id)








