from datetime import datetime
from urlparse import urlparse
from collections import Counter
import argparse
import re
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
  script        = Counter()
  style         = Counter()
  ctrs = [tags, bigrams, attrs, tag_attrs, tag_attr_vals, urls, paths,
          script, style]
  
  for (k, page_tuple) in enumerate(sample):
    page = page_tuple[2]
    
    page_tags          = set()
    page_bigrams       = set()
    page_attrs         = set()
    page_tag_attrs     = set()
    page_tag_attr_vals = set()
    page_urls          = set()
    page_paths         = set()
    page_script        = set()
    page_style         = set()
    
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
      if tag.name == 'script':
        script_tokens = re.findall('\W(\w\w+)\W', tag.get_text())
        for tok in script_tokens:
          page_script.add(tok)
      if tag.name == 'style':
        style_tokens = re.findall('\W(\w\w+)\W', tag.get_text())
        for tok in style_tokens:
          page_style.add(tok)
          
    
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
    for key in page_script:
      script[key] += 1
    for key in page_style:
      style[key] += 1
    
    if (k + 1) % 1000 == 0:
      for ctr in ctrs:
        for key in ctr.keys():
          if ctr[key] == 1:
            del ctr[key]

  out = {'tags'          : tags, 
         'bigrams'       : bigrams, 
         'attrs'         : attrs,
         'tag_attrs'     : tag_attrs,
         'tag_attr_vals' : tag_attr_vals,
         'urls'          : urls,
         'paths'         : paths,
         'script'        : script,
         'style'         : style}

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









