import zipfile
import os
from bs4 import BeautifulSoup as bs
import util

ZIP_TEMPLATE = '%s.zip'

# TODO: get a better name for this...its a generator.
def read_archive(archive_num, whitelist=None):
  '''
  A generator that produces BeautifulSoup objects (parsed web pages)
  for all of the files in an archive.
  Assumes the naming convention: 0.zip...5.zip
  
  Args:
    archive_num - either an int or string 0...5 or '0'...'5'
    whitelist - A set or none, default None. 
        If not None, only use files with names in the whitelist.
        
  Generate:
    A BeautifulSoup object for each file in the zip archive.
  '''
  filename = ZIP_TEMPLATE % str(archive_num)
  archive_path = os.path.join(util.DATA, filename)
  with zipfile.ZipFile(archive_path) as zf:
    # first entry is like '<archive_num>/'
    pages = zf.namelist()[1:]          
    if whitelist is not None:
      pages = [page for page in pages if page.split('/')[1] in whitelist]
    for page in pages:
      f = zf.open(page)
      soup = bs(f, 'lxml')
      yield soup