from bs4 import BeautifulSoup as bs
import os
import argparse
from datetime import datetime
import re
import zip_io
import paths
import artifacts

# Do not import pandas into this module.

D = 2**24

def write_features(sample_dict, outfile):
  start = datetime.now()
  outpath = os.path.join(paths.PROCESSED, outfile + '.libsvm')
  if sample_dict is not None:
    sample = zip_io.generate_sample(sample_dict)
  else:
    sample = zip_io.generate_test()
  with open(outpath, 'w') as f_out:
    for (k, page_tuple) in enumerate(sample):
      label = str(page_tuple[1])
      page = page_tuple[2]
      row = {}
      tag_counts(row, page)
      tag_attrs(row, page)
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
    ct = row.get(tag.name, 0)
    row[key] = ct + 1
    children = tag.find_all(True, recursive=False)
    for child in children:
      key = abs(hash(tag.name + '-' + child.name)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1
      grandchildren = child.find_all(True, recursive=False)
      for grandchild in grandchildren:
        key = abs(hash(tag.name + '-' + child.name + '_' + grandchild.name)) % D
        ct = row.get(key, 0)
        row[key] = ct + 1


def tag_attrs(row, page):
  tags = page.find_all(True)
  for tag in tags:
    attrs = tag.attrs
    for a in attrs:
      key = abs(hash(tag.name + '-' + a)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1
      
      # tag-attr-val
      value = unicode(tag.attrs[a])
      key = abs(hash(tag.name + '-' + a + '-' + value)) % D
      ct = row.get(key, 0)
      row[key] = ct + 1
      
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description =
           'Write sample of training data as .libsvm file at paths.ARTIFACTS')
  parser.add_argument('outfile', type=str, help = 
           'Data matrix written at paths/PROCESSED/<outfile>.libsvm')
  parser.add_argument('--sample', type=str, help = 
          'filename of sample dict at paths/ARTIFACTS')
  args = parser.parse_args()
  
  if args.sample is not None:
    sample_dict = artifacts.get_artifact(args.sample)
    write_features(sample_dict, args.outfile)
  else:
    write_features(None, args.outfile)





