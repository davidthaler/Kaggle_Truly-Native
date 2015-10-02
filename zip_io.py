import zipfile
import os
from random import random
from bs4 import BeautifulSoup as bs
import util

ZIP_TEMPLATE = '%s.zip'

def generate_sample(n_pos, n_neg, max_rows=None):
  tr = util.load_train(False)
  tr_pos = tr[tr.sponsored == 1]
  tr_pos = tr_pos.sample(n_pos)
  tr_neg = tr[tr.sponsored == 0]
  tr_neg = tr.sample(n_neg)
  sample_df = tr_pos.append(tr_neg)
  sample = dict(zip(sample_df.file, sample_df.sponsored))
  for archive_num in range(5):
    for item in one_archive(archive_num, sample):
      yield item


def generate_train():
  train_dict = util.load_train(as_dict=True)
  for archive_num in range(5):
    for item in one_archive(archive_num, train_dict):
      yield item
    
      
def generate_test():
  for item in one_archive(5, None):
    yield item
    

def limit(archive_num, train_data, max_items):
  it = one_archive(archive_num, train_data)
  for (k, item) in enumerate(it):
    if k == max_items:
      break
    else:
      yield item


def one_archive(archive_num, train_data):
  '''
  A generator that produces tuples of (filename, label, soup) or
  (filename, soup), where soup is a web page parsed by BeautifulSoup,
  for all of the files in an archive.
  Assumes the naming convention: 0.zip...5.zip
  
  Args:
    archive_num - either an int or string 0...5 or '0'...'5'
    train_data - A dict or none. 
      If dict, it maps filenames to labels, and labels are included in output.
      If None, only file names are included in output.
      If not None, only files in the dict are produced.
        
  Generate:
    A tuple of either labels or file names and a BeautifulSoup object 
    for each file in the zip archive.
  '''
  archive_name = ZIP_TEMPLATE % str(archive_num)  
  archive_path = os.path.join(util.DATA, archive_name)
  with zipfile.ZipFile(archive_path) as zf:
    # first entry is '<archive_num>/'
    pages = zf.namelist()[1:]
    if train_data is not None:
      pages = [page for page in pages if page.split('/')[1] in train_data]
    for page in pages:
      f = zf.open(page)
      soup = bs(f, 'html.parser')
      page_name = page.split('/')[1]
      if train_data is not None:
        yield (page_name, train_data[page_name], soup)
      else:
        yield (page_name, soup)
        
        




