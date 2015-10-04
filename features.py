from bs4 import BeautifulSoup as bs
from csv import DictWriter
import os
import argparse
from datetime import datetime
import zip_io
import paths
import artifacts

# Do not import pandas into this module.
# TODO: Don't forget to get the length/compressed length from the zip archive

BARE_TAGS = [ 'script', 'style', 'meta', 'link', 'main', 'article', 
              'section', 'header', 'footer', 'nav',
              'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'p', 
              'a', 'img', 'ul', 'ol', 'li', 'input', 'form', 'button',
              'br', 'em', 'center', 'i', 'b', 'pre', 'code', 'strong', 
              'strike', 'audio', 'video', 'canvas', 'map', 'table', 'tr',
              'th', 'td', 'frame', 'iframe' ]

TAG_ATTR_VAL = ['input type button', 'input type text', 'input type submit',
                'input type reset', 'input type email', 'input type password', 
                'input type hidden', 'input type search', 'input type file',
                'input type radio']
         
def write_sample(sample_dict, outfile):
  start = datetime.now()
  outpath = os.path.join(paths.PROCESSED, outfile + '.csv')
  if sample_dict is not None:
    sample = zip_io.generate_sample(sample_dict)
  else:
    sample = zip_io.generate_test()
  fieldnames = ['file', 'sponsored', 'tag_ct', 'head_tag_ct', 'body_tag_ct',
                'head_script', 'body_script', 'head_style', 'body_style']
  fieldnames.extend(BARE_TAGS)
  tag_attr_names = ['_'.join(s.split()) for s in TAG_ATTR_VAL]
  fieldnames.extend(tag_attr_names)
  with open(outpath, 'w') as f_out:
    writer = DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    for page_tuple in sample:
      row = {}
      row['file'] = page_tuple[0]
      row['sponsored'] = page_tuple[1]
      page = page_tuple[2]
      row['tag_ct'] = len(page.select('*'))
      row['head_tag_ct'] = len(page.select('head *'))
      row['body_tag_ct'] = len(page.select('body *'))
      row['head_script'] = len(page.select('head script'))
      row['body_script'] = len(page.select('body script'))
      row['head_style'] = len(page.select('head style'))
      row['body_style'] = len(page.select('body style'))
      add_bare_tags(row, page)
      add_tag_attr_vals(row, page)
      writer.writerow(row)
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds


def add_bare_tags(row, page):
  for tag in BARE_TAGS:
    row[tag] = len(page.select(tag))


def add_tag_attr_vals(row, page):
  for s in TAG_ATTR_VAL:
    name = '_'.join(s.split())
    selector = '%s[%s=%s]' % tuple(s.split())
    row[name] = len(page.select(selector))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description =
             'Write sample of training data as .csv file at paths.ARTIFACTS')
  parser.add_argument('outfile', type=str, help = 
           'Data matrix written at paths/PROCESSED/<outfile>.csv')
  parser.add_argument('--sample', type=str, help = 
          'filename of sample dict at paths/ARTIFACTS')
  args = parser.parse_args()
  
  if args.sample is not None:
    sample_dict = artifacts.get_artifact(args.sample)
    write_sample(sample_dict, args.outfile)
  else:
    write_sample(None, args.outfile)

