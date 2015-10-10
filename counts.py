from datetime import datetime
from urlparse import urlparse
from collections import Counter
import argparse
import zip_io
import artifacts
import pdb

def get_counts(sample_base):
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
    all_web = []
    all_paths = []
    for u in all_urls:
      try:
        all_web.append(urlparse(u).netloc)
        all_paths.append(urlparse(u).path)
      except ValueError:
        pass
    page_urls = set(all_web)
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
         

  return out

if __name__ == '__main__':
  text = '''
  Collect document frequencies for tags, attributes, urls, etc. from 
  a sample specified in <sample> and write results at artifacts/<outfile>.pkl
  '''
  start = datetime.now()
  parser = argparse.ArgumentParser(description=text)
  parser.add_argument('outfile', help=
      'bare name of output file, without path or extension')
  parser.add_argument('sample', help='bare name of sample')
  args = parser.parse_args()
  out = get_counts(args.sample)
  artifacts.put_artifact(out, args.outfile)
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds









