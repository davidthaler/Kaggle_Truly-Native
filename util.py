import pandas as pd
import os

HOME = os.path.expanduser('~')
BASE = os.path.join(HOME, 'Documents', 'Kaggle', 'dato')
DATA = os.path.join(BASE, 'data')
TRAIN = os.path.join(DATA, 'train_v2.csv')
SAMPLE = os.path.join(DATA, 'sampleSubmission_v2.csv')


def load_train(as_dict):
  '''
  Loads full training set, including labels, as either a data frame or a dict.
  
  Args:
    as_dict - If True, return a dict from filenames to labels
        instead of a data frame.

  Returns:
    the training data either as a data frame, 
    or as a dict from filenames to labels.
  '''
  tr = pd.read_csv(TRAIN)
  if as_dict:
    return dict(zip(tr.file, tr.sponsored))
  else:
    return tr


def train_ids():
  '''
  Loads the training set ids into a set.
  '''
  tr = pd.read_csv(TRAIN)
  return set(tr.file)

  
def sample_submission():
  '''
  Loads the sample submission as a Pandas data frame.
  '''
  return pd.read_csv(SAMPLE)





