from bs4 import BeautifulSoup as bs
from csv import DictWriter
import os
import re
import argparse
from datetime import datetime
from urlparse import urlparse
from collections import namedtuple
from collections import Counter
import zip_io
import paths
import artifacts

# Do not import pandas/numpy etc. into this file. It need to run under pypy.

TEXT_NAMES = ['brace_ct', 'bracket_ct', 'long_doctype', 'markup_len', 'markup_line_ct',
              'semicolon_ct', 'short_doctype', 'strict', 'text_len', 
              'text_line_ct', 'text_token_ct', 'transitional', 'parens_ct',
              'plus_ct', 'minus_ct', 'times_ct', 'divide_ct', 'and_ct', 'or_ct', 
              'colon_ct', 'under_ct', 'single_ct', 'double_ct', 'tab_ct', 
              'dot_ct', 'question_ct', 'excl_ct', 'amp_ct', 'hash_ct', 
              'backslash_ct', 'dollar_ct']


def load_counts():
  '''
  Returns:
    a namedtuple of sets of the items of each type that had a document
    frequency above threshold in the sample
  '''
  counts = artifacts.get_artifact('counts')
  Counters = namedtuple('Counters', counts.keys())
  for ctr_name in counts:
    ctr = counts[ctr_name]
    if ctr_name in ['tags', 'urls']:
      thr = 400
    elif ctr_name == 'script':
      thr = 10000
    else:
      thr = 4000
    counts[ctr_name] = {key for key in ctr if ctr[key] > thr}
  out = Counters(**counts)
  return out


def write_features(data, outfile):
  '''
  Args:
    data - a generator from zip_io such as generate_sample or generate_train
    outfile - just the base, with no path or extension
  '''
  outpath = os.path.join(paths.PROCESSED, outfile + '.csv')

  top_items = load_counts()
  fieldnames = ['file', 'sponsored', 'file_size', 
                'compressed_size', 'compression_ratio']
  for items in top_items:
    fieldnames.extend(items)
  fieldnames.extend(TEXT_NAMES)
  
  with open(outpath, 'w') as f_out:
    writer = DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    for (k, page_tuple) in enumerate(data):
      row = Counter()
      row['file'] = page_tuple[0]
      row['sponsored'] = page_tuple[1]
      page = page_tuple[2]
      row['file_size'] = page_tuple[3]
      row['compressed_size'] = page_tuple[4]
      row['compression_ratio'] = page_tuple[4] / (1.0 + page_tuple[3])
      # fill row up with features
      add_tags(row, page, top_items)
      add_script(row, page, top_items)
      add_style(row, page, top_items)
      #add_bigrams(row, page, top_items)
      add_attrs(row, page, top_items)
      add_tag_attrs(row, page, top_items)
      add_tag_attr_vals(row, page, top_items)
      add_urls(row, page, top_items)
      add_paths(row, page, top_items)
      text_features(row, page)
      writer.writerow(row)
      if (k + 1) % 1000 == 0:
        print '%d lines read' % (k + 1)


def add_script(row, page, top_items):
  for script_tag in page.select('script'):
    script_tokens = re.findall('\W(\w\w+)\W', script_tag.get_text())
    for token in script_tokens:
      if token in top_items.script:
        row[token] += 1


def add_style(row, page, top_items):
  for style_tag in page.select('style'):
    style_tokens = re.findall('\W(\w\w+)\W', style_tag.get_text())
    for token in style_tokens:
      if token in top_items.style:
        row[token] += 1


def add_tags(row, page, top_items):
  for tag in page.find_all(True):
    if tag.name in top_items.tags:
      row[tag.name] += 1


def add_bigrams(row, page, top_items):
  for tag in page.find_all(True):
    for child in tag.find_all(True, recursive=False):
      key = tag.name + '_' + child.name
      if key in top_items.bigrams:
        row[key] += 1


def add_attrs(row, page, top_items):
  for tag in page.find_all(True):
    for a in tag.attrs:
      if a in top_items.attrs:
        row[a] += 1
        
        
def add_tag_attrs(row, page, top_items):
  for tag in page.find_all(True):
    for a in tag.attrs:
      key = tag.name + '_' + a
      if key in top_items.tag_attrs:
        row[key] +=  1


def add_tag_attr_vals(row, page, top_items):
  for tag in page.find_all(True):
    for a in tag.attrs:
      key = tag.name + '_' + a + '_' + unicode(tag.attrs[a])
      if key in top_items.tag_attr_vals:
        row[key] += 1


def add_urls(row, page, top_items):
  all_urls = [x['src'] for x in page.select('[src]')]
  all_urls.extend([x['href'] for x in page.select('[href]')])
  for u in all_urls:
    try:
      key = urlparse(u).netloc
      if key in top_items.urls:
        row[key] += 1
    except ValueError:
      pass

  
def add_paths(row, page, top_items):
  all_urls = [x['src'] for x in page.select('[src]')]
  all_urls.extend([x['href'] for x in page.select('[href]')])
  for u in all_urls:
    try:
      key = urlparse(u).path
      if key in top_items.paths:
        row[key] += 1
    except ValueError:
      pass



def text_features(row, page):
  markup = page.prettify()
  row['markup_len'] = len(markup)
  row['markup_line_ct'] = markup.count('\n')
  row['short_doctype'] = int(markup.startswith('<!DOCTYPE html>'))
  row['long_doctype'] = int(markup.startswith('<!DOCTYPE html PUBLIC'))
  start = markup[:150]
  row['transitional'] = start.find('transitional')
  row['strict'] = start.find('strict')
  text = page.get_text(strip=True)
  row['text_len'] = len(text)
  row['text_line_ct'] = text.count('\n')
  row['text_token_ct'] = len(text.split())
  row['semicolon_ct'] = text.count(';')
  row['brace_ct'] = text.count('}')
  row['bracket_ct'] = text.count(']')
  row['parens_ct'] = text.count(')')
  row['plus_ct'] = text.count('+')
  row['minus_ct'] = text.count('-')
  row['times_ct'] = text.count('*')
  row['divide_ct'] = text.count('/')
  row['and_ct'] = text.count('&')
  row['or_ct'] = text.count('|')
  row['colon_ct'] = text.count(':')
  row['under_ct'] = text.count('_')
  row['single_ct'] = text.count("'")
  row['double_ct'] = text.count('"')
  row['tab_ct'] = text.count('\t')
  row['dot_ct'] = text.count('.')
  row['question_ct'] = text.count('?')
  row['excl_ct'] = text.count('!')
  row['amp_ct'] = text.count('@')
  row['hash_ct'] = text.count('#')
  row['backslash_ct'] = text.count('\\')
  row['dollar_ct'] =  text.count('$')


def test_features(outfile):
  test = zip_io.generate_test()
  write_features(test, outfile + '_test')


def train_features(outfile):
  train_dict = artifacts.get_artifact('train_dict')
  data = zip_io.generate_sample(train_dict)
  write_features(data, outfile + '_train')


def sample_features(sample_name, outfile):
  sample_dict = artifacts.get_artifact(sample_name)
  sample = zip_io.generate_sample(sample_dict)
  write_features(sample, outfile)


def all(outfile):
  train_features(outfile)
  test_features(outfile)
  
  
if __name__ == '__main__':
  start = datetime.now()
  parser = argparse.ArgumentParser(description=
      'Makes dense count features from the most frequent tags, attributes, etc.')
  parser.add_argument('outfile', help=
      'Base name of the output file, with no path or extension')
  parser.add_argument('--all', action='store_true', help=
      'Make training and test sets in one go.')
  parser.add_argument('--train', action='store_true', help=
      'Generate features for full training set.')
  parser.add_argument('--test', action='store_true', help=
      'Generate features for test set.')
  parser.add_argument('--sample', help=
      'Base name of the sample file, with no path or extension')
  args = parser.parse_args()
  if args.all:
    all(args.outfile)
  elif args.test:
    test_features(args.outfile)
  elif args.train:
    train_features(args.outfile)
  elif args.sample is not None:
    sample_features(args.sample, args.outfile)
  else:
    print 'must select one of --sample, --train,  --test or --all'
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds 










