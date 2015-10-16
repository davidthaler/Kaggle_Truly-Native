import numpy as np
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import roc_auc_score
import os
import argparse
from datetime import datetime
import util
import artifacts
import paths
import random

# This module imports pandas and sklearn, so it can't run under pypy.

def avg_run_all(n_models, base_model, infile_base, passes, bits, submit_id):
  '''
  Runs a batch of linear models over the data, with the input files presented
  to each in a random order. Writes a submission based on the models averaged
  predictions.
  
  Args:
    n_models - the number of models to produce
    base_model - a model that is cloned to produce the models
    infile_base - bare input data name without path or extension
    pases - number of passes over data in training
    bits - the feature space shoul be of dimension 2**bits
    submit_id - the result is written as submissions/submission_<submit_id>.csv

  Writes:
    A submission at paths.SUBMIT/submisssion_<submit_id>.csv
  '''
  models = []
  orders = []
  l = range(5)
  for k in range(n_models):
    model_k = base_model.__class__()
    model_k.set_params(**base_model.get_params())
    models.append(model_k)
    random.shuffle(l)
    orders.append(l[:])
  model_orders = zip(models, orders)
    
  for k in range(passes):
    print 'Pass %d' % k
    for (m, order) in model_orders:
      for file_num in order:
        train_set_name = '%s.%d' % (infile_base, file_num)
        print 'loading training file: ' + train_set_name
        x, y = util.load_sparse(train_set_name, n_features=2**bits, verbose=False)
        m.partial_fit(x, y, classes=[0., 1.])
        
  test_set_name = infile_base + '.5'
  print 'loading test set...'
  x, y = util.load_sparse(test_set_name, n_features=2**bits, verbose=False)
  dvs = np.zeros((len(y), n_models))
  for (k, m) in enumerate(models):
    dvs[:, k] = m.decision_function(x)
  dv = dvs.mean(axis=1)
  util.write_submission(dv, submit_id)


def avg_validate(n_models, base_model, infile_base, passes, bits):
  '''
  Runs a batch of linear models over 0.zip to 3.zip, with the input files 
  presented to each in a random order. Produces a prediction by averaging.
  Prints out the AUC score of the average prediction on 4.zip.
  
  Args:
    n_models - the number of models to produce
    base_model - a model that is cloned to produce the models
    infile_base - bare input data name without path or extension
    pases - number of passes over data in training
    bits - the feature space shoul be of dimension 2**bits
    
  Output:
    prints AUC score on 4.zip
  '''
  models = []
  orders = []
  l = range(4)
  for k in range(n_models):
    model_k = base_model.__class__()
    model_k.set_params(**base_model.get_params())
    models.append(model_k)
    random.shuffle(l)
    orders.append(l[:])
  model_orders = zip(models, orders)
    
  for k in range(passes):
    print 'Pass %d' % k
    for (m, order) in model_orders:
      for file_num in order:
        train_set_name = '%s.%d' % (infile_base, file_num)
        print 'loading training file: ' + train_set_name
        x, y = util.load_sparse(train_set_name, n_features=2**bits, verbose=False)
        m.partial_fit(x, y, classes=[0., 1.])
        
  val_set_name = infile_base + '.4'
  print 'loading validation set...'
  x, y = util.load_sparse(val_set_name, n_features=2**bits, verbose=False)
  dvs = np.zeros((len(y), n_models))
  for (k, m) in enumerate(models):
    dvs[:, k] = m.decision_function(x)
  dv = dvs.mean(axis=1)
  score = roc_auc_score(y, dv)
  print 'AUC: %.4f' % score
  
  
def validate(model, infile_base, passes, bits):
  '''
  Trains a model on 0.zip...3.zip and evaluates it on 4.zip.
  
  Args:
    model - the model to validate with
    infile_base - bare input data name without path or extension
    pases - number of passes over data in training
    bits - the feature space shoul be of dimension 2**bits
    
  Output:
    prints AUC score on 4.zip
  '''
  for k in range(passes):
    print 'Pass %d' % k
    for file_num in range(4):
      train_set_name = '%s.%d' % (infile_base, file_num)
      print 'loading training file: ' + train_set_name
      x, y = util.load_sparse(train_set_name, n_features=2**bits, verbose=False)
      model.partial_fit(x, y, classes=[0., 1.])
  val_set_name = infile_base + '.4'
  print 'loading validation set...'
  x, y = util.load_sparse(val_set_name, n_features=2**bits, verbose=False)
  dv = model.decision_function(x)
  score = roc_auc_score(y, dv)
  print 'AUC: %.4f' % score
      

def train(model, infile_base, passes, bits):
  '''
  Trains a model on 0.zip...4.zip.
  
  Args:
    model - the model to train
    infile_base - bare input data name without path or extension
    pases - number of passes over data in training
    bits - the feature space shoul be of dimension 2**bits
    
  Side-effects:
    model is trained
  '''
  for k in range(passes):
    print 'Pass %d' % k
    for file_num in range(5):
      train_set_name = '%s.%d' % (infile_base, file_num)
      print 'loading training file: ' + train_set_name
      x, y = util.load_sparse(train_set_name, n_features=2**bits, verbose=False)
      model.partial_fit(x, y, classes=[0., 1.])

  
def test(model, infile_base, bits):
  '''
  Predicts on 5.zip with the provided model.
  
  Args:
    model - the model to predict with
    infile_base - bare input data name without path or extension
    bits - the feature space shoul be of dimension 2**bits

  Returns:
    predictions on 5.zip
  '''
  test_set_name = infile_base + '.5'
  print 'loading test set...'
  x, _ = util.load_sparse(test_set_name, n_features=2**bits, verbose=False)
  dv = model.decision_function(x)
  return dv


def run_all(model, infile_base, passes, bits, submit_id):
  '''
  Takes model and trains it on 0.zip...4.zip, then predicts on 5.zip.
  Writes predictions out as a valid submission identified by submit_id.
  
  Args:
    model - the model to train and test.
    infile_base - bare input data name without path or extension
    pases - number of passes over data in training
    bits - the feature space shoul be of dimension 2**bits
    submit_id - the result is written as submissions/submission_<submit_id>.csv

  Writes:
    A submission at paths.SUBMIT/submisssion_<submit_id>.csv
  '''
  train(model, infile_base, passes, bits)
  pred = test(model, infile_base, bits)
  util.write_submission(pred, submit_id)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=
      'By default, train and predict using all data, then write out submission.' + 
      'Otherwise, do validation by training on 0-3.zip and evaluating on 4.zip.')
  parser.add_argument('infile', type=str, help=
      'Base of train/test file names; data is read from data/processed')
  parser.add_argument('-s', '--submit_id', type=str, help=
      'Submission written at submissions/submission_<submit_id>.csv')
  parser.add_argument('-b', '--bits', type=int, default=20, 
        help='notional feature space dimension is 2**bits')
  parser.add_argument('-C', type=float, default=1.0, 
        help='C parameter of passive-aggressive model')
  parser.add_argument('-p', '--passes', type=int, default=10, 
        help='number of passes over full training data')
  parser.add_argument('-l', '--loss', choices=['hinge', 'squared_hinge'], 
        default='squared_hinge', help='loss function for model')
  parser.add_argument('-v', '--validate', action='store_true', 
        help='do validation')
  parser.add_argument('--avg', type=int, help=
       'average this # of models together, trained on different data order')
  start = datetime.now()
  args = parser.parse_args()
  print args
  model = PassiveAggressiveClassifier(C=args.C,  
                                      loss=args.loss, 
                                      warm_start=True)
  print 'Using model:'
  print model
  if args.validate:
    if args.avg is None:
      validate(model, args.infile, args.passes, args.bits)
    else:
      avg_validate(args.avg, model, args.infile, args.passes, args.bits)
  else:
    if args.avg is None:
      run_all(model, args.infile, args.passes, args.bits, args.submit_id)
    else:
      avg_run_all(args.avg, 
                  model, 
                  args.infile, 
                  args.passes, 
                  args.bits, 
                  args.submit_id)
  finish = datetime.now()
  print 'Run finished: %d sec.' % (finish - start).seconds









