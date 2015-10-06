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

BARE_TAGS = ['a', 'article', 'audio', 'b', 'br', 'button', 'canvas', 
             'center', 'code', 'dd', 'div', 'dl', 'dt', 'em', 'footer', 
             'form', 'frame', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 
             'i', 'iframe', 'img', 'input', 'ins', 'li', 'link', 'main', 
             'map', 'meta', 'nav', 'ol', 'p', 'pre', 'script', 'section', 
             'span', 'strike', 'strong', 'style', 'table', 'td', 'textarea', 
             'th', 'tr', 'ul', 'video']

TAG_ATTR_VAL = ['a rel close', 'a rel nofollow', 'a target #', 
                'a target _blank', 'form method get', 'form method post', 
                'input type button', 'input type email', 'input type file', 
                'input type hidden', 'input type password', 
                'input type radio', 'input type reset', 'input type search', 
                'input type submit', 'input type text', 'link media all', 
                'link rel icon', 'link rel stylesheet', 'link type text/css', 
                'link type text/javascript', 'meta name viewport', 
                'script language javascript', 'style type text/css']

TAG_ATTR = ['a class', 'a height', 'a onclick', 'a rel', 'a target', 
            'a title', 'a width', 'article class', 'aside class', 
            'dd class', 'div class', 'div onclick', 'div style', 
            'dl class', 'dt class', 'footer class', 'form action', 
            'form class', 'form onsubmit', 'h1 class', 'h2 class', 
            'h3 class', 'h4 class', 'h5 class', 'h6 class', 
            'header class', 'i class', 'img alt', 'img border', 
            'img class', 'img height', 'img onclick', 'img width', 
            'input autocomplete', 'input class', 'input name', 
            'input placeholder', 'input value', 'ins class', 'li class', 
            'link media', 'link rel', 'meta charset', 'meta content', 
            'meta name', 'meta property', 'meta rel', 'nav class', 
            'ol class', 'p lang', 'p onclick', 'script async', 'script src', 
            'section class', 'span class', 'span onclick', 'span style', 
            'ul class']

TEXT_NAMES = ['bracket_ct', 'long_doctype', 'markup_len', 'markup_line_ct',
              'semicolon_ct', 'short_doctype', 'strict', 'text_len', 
              'text_line_ct', 'text_token_ct', 'transitional']


def write_sample(sample_dict, outfile):
  start = datetime.now()
  outpath = os.path.join(paths.PROCESSED, outfile + '.csv')
  if sample_dict is not None:
    sample = zip_io.generate_sample(sample_dict)
  else:
    sample = zip_io.generate_test()
  fieldnames = ['file', 'sponsored', 'tag_ct', 'head_tag_ct', 'body_tag_ct',
                'head_script', 'body_script', 'head_style', 'body_style',
                'head_link', 'body_link']
  fieldnames.extend(BARE_TAGS)
  tag_attr_val_names = ['_'.join(s.split()) for s in TAG_ATTR_VAL]
  fieldnames.extend(tag_attr_val_names)
  tag_attr_names = ['_'.join(s.split()) for s in TAG_ATTR]
  fieldnames.extend(tag_attr_names)
  fieldnames.extend(TEXT_NAMES)
  
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
      row['head_link'] = len(page.select('head link'))
      row['body_link'] = len(page.select('body link'))
      add_bare_tags(row, page)
      add_tag_attr_vals(row, page)
      add_tag_attr(row, page)
      text_features(row, page)
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


def add_tag_attr(row, page):
  for s in TAG_ATTR:
    name = '_'.join(s.split())
    selector = '%s[%s]' % tuple(s.split())
    row[name] = len(page.select(selector))


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
  row['bracket_ct'] = text.count('}')


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

