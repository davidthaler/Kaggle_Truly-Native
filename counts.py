from datetime import datetime
from urlparse import urlparse
from collections import Counter
import zip_io
import artifacts
import pdb

def get_counts(sample_base):
  start = datetime.now()
  sample_dict = artifacts.get_artifact(sample_base)
  sample = zip_io.generate_sample(sample_dict)
  
  tags              = Counter()
  bigrams           = Counter()
  trigrams          = Counter()
  attrs             = Counter()
  tag_attrs         = Counter()
  tag_attr_vals     = Counter()
  
  for page_tuple in sample:
    page = page_tuple[2]
    for tag in page.find_all(True):
      tags[tag.name] += 1
      for a in tag.find_all(True, recursive=False):
        key = tag.name + '_' + a.name
        bigrams[key] += 1
        for b in a.find_all(True, recursive=False):
          key = tag.name + '_' + a.name + '_' + b.name
          trigrams[key] += 1
      for a in tag.attrs:
        attrs[a] += 1
        key = tag.name + '_' + a
        tag_attrs[key] += 1
        key = key + '_' + unicode(tag.attrs[a])
        tag_attr_vals[key] += 1
    
  out = {'tags'             : tags, 
         'bigrams'          : bigrams, 
         'trigrams'         : trigrams,
         'attrs'            : attrs,
         'tag_attrs'        : tag_attrs,
         'tag_attr_vals'    : tag_attr_vals}
         
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds
  return out



