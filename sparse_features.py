from bs4 import BeautifulSoup as bs
import os
import argparse
import re
from collections import Counter
from urlparse import urlparse
from datetime import datetime
import zip_io
import paths
import artifacts

# Do not import pandas into this module.

D = 2**20


def write_features(data, outfile):
  print 'Feature space dimension: %d' % D
  start = datetime.now()
  outpath = os.path.join(paths.PROCESSED, outfile + '.libsvm')
  with open(outpath, 'w') as f_out:
    for (k, page_tuple) in enumerate(data):
      label = str(page_tuple[1])
      page = page_tuple[2]
      row = {}
      tag_counts(row, page)
      get_urls(row, page)
      get_paths(row, page)
      hashed_strings(row, page)
      #script_tokens(row, page)
      #parents(row, page)
      #tag_children(row, page)
      #tag_bigrams(row, page)
      #tag_trigrams(row, page)
      tag_attrs(row, page)
      tag_attr_vals(row, page)
      #attrs(row, page)
      f_out.write(label + ' ')
      for key in sorted(row.keys()):
        f_out.write('%s:%d ' % (key, row[key]))
      f_out.write('\n')
      if (k + 1) % 1000 == 0:
        print '%d lines read' % (k + 1)
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds


def tag_counts(row, page):
  tags = page.find_all(True)
  for tag in tags:
    key = abs(hash(tag.name)) % D
    ct = row.get(key, 0)
    row[key] = ct + 1


def hashed_strings(row, page):
  for s in page.stripped_strings:
    key = abs(hash(s[:100])) % D
    ct = row.get(key, 0)
    row[key] = ct + 1


def script_tokens(row, page):
  ctr = Counter()
  for tag in page.select('script'):
    script_tokens = re.split('\W', tag.get_text())
    for token in script_tokens:
      if len(token) > 2:
        ctr[token] += 1
        
  for tag in page.select('script'):
    script_tokens = re.split('\W', tag.get_text())
    for token in script_tokens:
      if ctr[token] >= 5:
        key = abs(hash(token)) % D
        ct = row.get(key, 0)
        row[key] = ct + 1


def get_paths(row, page):
  all_urls = [x['src'] for x in page.select('[src]')]
  all_urls.extend([x['href'] for x in page.select('[href]')])
  for u in all_urls:
    try:
      path = urlparse(u).path
      path_parts = path.split('/')
      for p in path_parts:
        key = abs(hash('pathpart' + p)) % D
        ct = row.get(key, 0)
        row[key] = ct + 1
    except ValueError:
      pass


def get_urls(row, page):
  all_urls = [x['src'] for x in page.select('[src]')]
  all_urls.extend([x['href'] for x in page.select('[href]')])
  for u in all_urls:
    try:
      key = abs(hash(urlparse(u).netloc)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1
    except ValueError:
      pass


def parents(row, page):
  tags = page.find_all(True)
  for tag in tags:
    parents = len(list(tag.parents))
    key = abs(hash(tag.name + 'child' +  str(parents))) % D
    ct = row.get(key, 0)
    row[key] = ct + 1


def tag_children(row, page):
  tags = page.find_all(True)
  for tag in tags:
    children = len(tag.find_all(True, recursive=False))
    key = abs(hash(tag.name + 'child' +  str(children))) % D
    ct = row.get(key, 0)
    row[key] = ct + 1


def tag_bigrams(row, page):
  tags = page.find_all(True)
  for tag in tags:
    children = tag.find_all(True, recursive=False)
    for child in children:
      key = abs(hash(tag.name + '-' + child.name)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1


def tag_trigrams(row, page):
  tags = page.find_all(True)
  for tag in tags:
    children = tag.find_all(True, recursive=False)
    for child in children:
      grandkids = child.find_all(True, recursive=False)
      for grandkid in grandkids:
        key = abs(hash(tag.name + '-' + child.name + '_' + grandkid.name)) % D
        ct = row.get(key, 0)
        row[key] = ct + 1


def tag_attrs(row, page):
  tags = page.find_all(True)
  for tag in tags:
    for a in tag.attrs:
      key = abs(hash(tag.name + '-' + a)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1


def tag_attr_vals(row, page):
  tags = page.find_all(True)
  for tag in tags:
    for a in tag.attrs:
      value = unicode(tag.attrs[a])               # can be a list
      key = abs(hash(tag.name + '-' + a + '-' + value)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1
  
      
def attrs(row, page):
  tags = page.find_all(True)
  for tag in tags:
    for a in tag.attrs:
      key = abs(hash(a)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1
  
  
def sample_features(sample_name, outfile):
  sample_dict = artifacts.get_artifact(sample_name)
  sample = zip_io.generate_sample(sample_dict)
  write_features(sample, outfile)


def test_features(outfile):
  test = zip_io.generate_test()
  # The + '.5' allows the test set to have the same base name as the 
  # training data, with base.5 as test and base.0-4 for train.
  write_features(test, outfile + '.5')


def train_features(outfile):
  train_dict = artifacts.get_artifact('train_dict')
  for archive_num in range(5):
    data = zip_io.one_archive(archive_num, train_dict)
    batch_name = '%s.%d' % (outfile, archive_num)
    write_features(data, batch_name)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description =
           'Write sample of training data as .libsvm file at paths.ARTIFACTS')
  parser.add_argument('outfile', type=str, help = 
           'Data matrix written at paths/PROCESSED/<outfile>.libsvm')
  parser.add_argument('--all', action='store_true', help=
           'compute features over training and test data in per-file batches')
  parser.add_argument('--train', action='store_true', help=
           'compute training set features in per-file batches')
  parser.add_argument('--test', action='store_true', help=
           'compute features over test set')
  parser.add_argument('--sample', type=str, help = 
           'filename of sample dict at paths/ARTIFACTS')
  parser.add_argument('--bits', type=int, default=20, help=
          'notional feature space dimension is 2**bits')
  args = parser.parse_args()
  print args
  D = 2**args.bits
  if args.all:
    train_features(args.outfile)
    test_features(args.outfile)
  elif args.test:
    test_features(args.outfile)
  elif args.train:
    train_features(args.outfile)
  elif args.sample is not None:
    sample_features(args.sample, args.outfile)
  else:
    print 'must select one of --sample, --train or --test'





