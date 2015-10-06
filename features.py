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
              'th', 'td', 'frame', 'iframe', 'dd', 'dl', 'dt', 'ins', 
              'textarea']

TAG_ATTR_VAL = ['input type button', 'input type text', 'input type submit',
                'input type reset', 'input type email', 'input type password', 
                'input type hidden', 'input type search', 'input type file',
                'input type radio', 'link rel stylesheet', 'meta name viewport', 
                'link rel icon', 'style type text/css',
                'link type text/css', 'link type text/javascript', 'a rel close',
                'link media all', 'script language javascript', 'a rel nofollow',
                'form method get', 'form method post', 'a target _blank', 
                'a target #']

TAG_ATTR = ['a class', 'article class', 'aside class', 'dd class', 'div class',
            'dl class', 'dt class', 'footer class', 'form class', 'h1 class',
            'h2 class', 'h3 class', 'h4 class', 'h5 class', 'h6 class', 
            'header class', 'i class', 'img class', 'input class', 'ins class',
            'li class', 'ol class', 'ul class', 'nav class', 'section class', 
            'span class', 'meta content', 'meta name', 'meta property', 
            'meta rel', 'meta charset', 'script async', 'link media', 
            'script src', 'a rel', 'input value', 'input name', 'a target', 
            'div style', 'input placeholder', 'input autocomplete', 
            'form action', 'img alt', 'a title', 'a height', 'a width', 
            'img height', 'img width', 'img border', 'span style', 'p lang',
            'a onclick', 'img onclick', 'div onclick', 'span onclick', 
            'p onclick', 'form onsubmit', 'link rel']

TEXT_NAMES = ['markup_len', 'markup_line_ct', 'short_doctype', 'long_doctype',
              'transitional', 'strict', 'text_len', 'text_line_ct', 
              'text_token_ct', 'semicolon_ct', 'bracket_ct']


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

