from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import roc_auc_score
import os
import argparse
from datetime import datetime
import util
import artifacts
import paths


def validate(model, infile_base, passes, bits):
  for k in range(passes):
    print 'Pass %d' % k
    for file_num in range(4):
      train_set_name = '%s.%d' % (infile_base, file_num)
      print 'loading training file: ' + train_set_name
      x, y = util.load_sparse(train_set_name, n_features=2**bits)
      model.partial_fit(x, y, classes=[0., 1.])
  val_set_name = infile_base + '.4'
  print 'loading validation set...'
  x, y = util.load_sparse(val_set_name, n_features=2**bits)
  dv = model.decision_function(x)
  score = roc_auc_score(y, dv)
  print 'AUC: %.4f' % score
      

def train(model, infile_base, passes, bits):
  for k in range(passes):
    print 'Pass %d' % k
    for file_num in range(5):
      train_set_name = '%s.%d' % (infile_base, file_num)
      print 'loading training file: ' + train_set_name
      x, y = util.load_sparse(train_set_name, n_features=2**bits)
      model.partial_fit(x, y, classes=[0., 1.])

  
def test(model, infile_base, bits):
  test_set_name = infile_base + '.5'
  print 'loading test set...'
  x, _ = util.load_sparse(test_set_name, n_features=2**bits)
  dv = model.decision_function(x)
  return dv


def run_all(model, infile_base, passes, bits, submit_id,):
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
  parser.add_argument('-p', '--passes', type=int, default=5, 
        help='number of passes over full training data')
  parser.add_argument('-l', '--loss', choices=['hinge', 'squared_hinge'], 
        default='squared_hinge', help='loss function for model')
  parser.add_argument('-v', '--validate', action='store_true', 
        help='do validation')
  start = datetime.now()
  args = parser.parse_args()
  print args
  model = PassiveAggressiveClassifier(C=args.C,  
                                      loss=args.loss, 
                                      warm_start=True)
  print 'Using model:'
  print model
  if args.validate:
    validate(model, args.infile, args.passes, args.bits)
  else:
    run_all(model, args.infile, args.passes, args.bits, args.submit_id)
  finish = datetime.now()
  print 'Run finished: %d sec.' % (finish - start).seconds









