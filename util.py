import pandas as pd
import os
import paths

# This module imports pandas

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

  
def sample_submission():
  '''
  Loads the sample submission as a Pandas data frame.
  '''
  return pd.read_csv(paths.SAMPLE)


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
  put_artifact(sample, outfile)





