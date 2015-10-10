import os

# Do not import pandas/numpy/scipy into this module.
# It gets imported by stuff that runs under pypy.

HOME = os.path.expanduser('~')
BASE = os.path.join(HOME, 'Documents', 'Kaggle', 'dato')
DATA = os.path.join(BASE, 'data')
TRAIN = os.path.join(DATA, 'train_v2.csv')
ARTIFACTS =  os.path.join(BASE, 'artifacts')
PROCESSED = os.path.join(DATA, 'processed')
SUBMIT = os.path.join(BASE, 'submissions')
TMP = os.path.join(BASE, 'tmp')

