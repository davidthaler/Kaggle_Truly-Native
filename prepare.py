import os
import util
import artifacts

# This script must run in Python, not Pypy.

# This creates a dict like {filename: label} for the whole training set.
train = util.load_train(True)
artifacts.put_artifact(train, 'train_dict')

# This makes a similar dict, holding a sample of 20k positive 
# and 20k negative instances. 
# This is used for determining frequent tags, tokens, etc. for features.
# The dict is saved as artifacts/sample_20_20.pkl.
sample = util.create_sample('sample_20_20', 20000, 20000)
