import zipfile
import os
from random import random
from bs4 import BeautifulSoup as bs
import paths
import artifacts

# Do not import pandas into this module. It needs to run under pypy.

ZIP_TEMPLATE = '%s.zip'

def generate_sample(sample):
  '''
  Generator for a sample drawn from the training data. 
  See one_archive below.
  
  Args:
    sample - a dict like {filename: label} for every file in the sample.
  
  Generates:
    tuples like:
      (filename, label, soup, file size, zip file compressed size)
  '''
  for archive_num in range(5):
    for item in one_archive(archive_num, sample):
      yield item


def generate_train():
  '''
  Generator for the full training data. See one_archive.
  
  Generates:
    tuples like:
      (filename, label, soup, file size, zip file compressed size)
  '''
  train_dict = artifacts.get_artifact('train_dict')
  for archive_num in range(5):
    for item in one_archive(archive_num, train_dict):
      yield item
    
      
def generate_test():
  '''
  Generator for the full test data. See one_archive.
  
  Generates:
    tuples like:
      (filename, label, soup, file size, zip file compressed size)
  '''
  for item in one_archive(5, None):
    yield item


def one_archive(archive_num, train_data):
  '''
  A generator that produces tuples like:
      (filename, label, soup, file size, zip file compressed size)
  where soup is a web page parsed by BeautifulSoup.
  Assumes the naming convention: 0.zip...5.zip.
  The dict needed (train_data) can be created by util.create_sample.
  
  Args:
    archive_num - either an int or string 0...5 or '0'...'5'
    train_data - A dict or none. 
      If dict, it maps filenames to labels, and both are included in output.
      If None, 0's are output for the labels.
      If not None, only files in the dict are produced.
        
  Generates:
    tuples like:
      (filename, label, soup, file size, zip file compressed size)
  '''
  archive_name = ZIP_TEMPLATE % str(archive_num)
  print 'reading %s' % archive_name 
  archive_path = os.path.join(paths.DATA, archive_name)
  with zipfile.ZipFile(archive_path) as zf:
    # first entry is '<archive_num>/'
    pages = zf.infolist()[1:]
    if train_data is not None:
      pages = [pg for pg in pages if pg.filename.split('/')[1] in train_data]
    for page in pages:
      with zf.open(page.filename) as f:
        soup = bs(f, 'html.parser')
        page_name = page.filename.split('/')[1]
        if train_data is not None:
          yield (page_name, 
                 train_data[page_name], 
                 soup, 
                 page.file_size, 
                 page.compress_size)
        else:
          yield (page_name, 0, soup, page.file_size, page.compress_size)
        
        




