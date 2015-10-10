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
  
  tags          = Counter()
  bigrams       = Counter()
  attrs         = Counter()
  tag_attrs     = Counter()
  tag_attr_vals = Counter()
  urls          = Counter()
  paths         = Counter()
  
  for page_tuple in sample:
    page = page_tuple[2]
    
    page_tags          = set()
    page_bigrams       = set()
    page_attrs         = set()
    page_tag_attrs     = set()
    page_tag_attr_vals = set()
    page_urls          = set()
    page_paths         = set()
    
    for tag in page.find_all(True):
      page_tags.add(tag.name)
      for child in tag.find_all(True, recursive=False):
        key = tag.name + '_' + child.name
        page_bigrams.add(key)
      for a in tag.attrs:
        page_attrs.add(a)
        key = tag.name + '_' + a
        page_tag_attrs.add(key)
        key = key + '_' + unicode(tag.attrs[a])
        page_tag_attr_vals.add(key)
    
    srcs = page.select('[src]')
    hrefs = page.select('[href]')
    all_urls = [tag['src'] for tag in srcs]
    all_urls.extend([tag['href'] for tag in hrefs])
    all_web = [urlparse(u).netloc for u in all_urls]
    page_urls = set(all_web)
    all_paths = [urlparse(u).path for u in all_urls]
    page_paths = set(all_paths)

    for key in page_urls:
      urls[key] += 1
    for key in page_paths:
      paths[key] += 1
    for key in page_tags:
      tags[key] += 1
    for key in page_bigrams:
      bigrams[key] += 1
    for key in page_attrs:
      attrs[key] += 1
    for key in page_tag_attrs:
      tag_attrs[key] += 1
    for key in page_tag_attr_vals:
      tag_attr_vals[key] += 1
      
  out = {'tags'          : tags, 
         'bigrams'       : bigrams, 
         'attrs'         : attrs,
         'tag_attrs'     : tag_attrs,
         'tag_attr_vals' : tag_attr_vals,
         'urls'          : urls,
         'paths'         : paths}
         
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds
  return out



