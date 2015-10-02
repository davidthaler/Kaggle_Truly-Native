import pandas as pd
import cPickle
import os
import paths

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
  tr = pd.read_csv(paths.TRAIN)
  if as_dict:
    return dict(zip(tr.file, tr.sponsored))
  else:
    return tr


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


def put_artifact(obj, artifactfile):
  '''
  Pickles an object at ARTIFACTS/artifactfile
  
  args:
    obj - an intermediate result to pickle
    artifactfile - obj is pickled at ARTIFACT/artifactfile
  
  return:
    nothing, but obj is pickled at ARTIFACT/artifactfile.pkl
  '''
  artifactpath = os.path.join(paths.ARTIFACTS, artifactfile + '.pkl')
  with open(artifactpath, 'w') as f:
    cPickle.dump(obj, f)


def get_artifact(artifactfile):
  '''
  Recovers a pickled intermediate result (artifact) from ARTIFACTS/
  
  args:
    artifactfile - an object is loaded from ARTIFACTS/artifactfile 
    
  return:
    the reloaded intermediate object
  '''
  artifactpath = os.path.join(paths.ARTIFACTS, artifactfile + '.pkl')
  with open(artifactpath) as f:
    artifact = cPickle.load(f)
  return artifact


def create_sample(outfile, n_pos, n_neg):
  '''
  Creates a dict describing a specific sample of rows and saves 
  it at ARTIFACTS with form {filename : label}.
  
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
  sample = dict(zip(sample_df.file, sample_df.sponsored))
  put_artifact(sample, outfile)





