from bs4 import BeautifulSoup as bs
from csv import DictWriter
import os
import argparse
from datetime import datetime
from urlparse import urlparse
import zip_io
import paths
import artifacts

# Do not import pandas into this module.

BARE_TAGS = ['a', 'article', 'b', 'br', 'button', 
             'center', 'dd', 'div', 'dl', 'dt', 'em', 'footer', 
             'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 
             'i', 'iframe', 'img', 'input', 'ins', 'li', 'link', 
             'meta', 'nav', 'ol', 'p', 'script', 'section', 
             'span', 'strike', 'strong', 'style', 'table', 'td', 'textarea', 
             'th', 'tr', 'ul']

TAG_ATTR_VAL = ['a rel nofollow',
                'a target _blank', 'form method get', 'form method post', 
                'input type button', 'input type email', 'input type file', 
                'input type hidden', 'input type password', 
                'input type radio', 'input type reset', 'input type search', 
                'input type submit', 'input type text', 'link media all', 
                'link rel icon', 'link rel stylesheet', 'link type text/css', 
                'link type text/javascript', 'meta name viewport', 
                'script language javascript', 'style type text/css']

TAG_ATTR = ['a class', 'a onclick', 'a rel', 'a target', 
            'a title', 'article class', 'aside class', 'div class', 
            'div style', 'footer class', 'form action', 
            'form class', 'form onsubmit', 'h1 class', 'h2 class', 
            'h3 class', 'h4 class', 'h5 class', 'h6 class', 
            'header class', 'i class', 'img alt', 'img border', 
            'img class', 'img height', 'img width', 
            'input autocomplete', 'input class', 'input name', 
            'input placeholder', 'input value', 'ins class', 'li class', 
            'link media', 'link rel', 'meta charset', 'meta content', 
            'meta name', 'meta property', 'nav class', 
            'ol class', 'script async', 'script src', 
            'section class', 'span class', 'span style', 
            'ul class']

TEXT_NAMES = ['bracket_ct', 'long_doctype', 'markup_len', 'markup_line_ct',
              'semicolon_ct', 'short_doctype', 'strict', 'text_len', 
              'text_line_ct', 'text_token_ct', 'transitional']

SCRIPT_FEATURES = ['script_text_ct', 'script_no_txt', 'total_script_length',
                   'max_script_length', 'mean_script_length', 
                   'script_tot_lines', 'script_max_lines', 
                   'script_tot_braces', 'script_max_braces', 
                   'script_urls', 'script_distinct_urls']
                   
URL_FEATURES = ['facebook', 'google', 'twitter', 'pinterest', 'linkedin', 
                 'amazonaws', 'cloudfront', 'addthis', 'googlesyndication']

PATH_FEATURES = ['wp-content', 'wp-includes', 'plugins', 'jquery', 'sites', 
                 'assets', 'js', 'widgets', 'files', 'ajax', 'themes', 
                 'public', 'google', 'bootstrap', 'pagead', 'media', 
                 'static', 'share']
                 
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
  fieldnames.extend(SCRIPT_FEATURES)
  script_url_names = ['script_url_' + url for url in URL_FEATURES]
  fieldnames.extend(script_url_names)
  script_path_names = ['script_path_' + p for p in PATH_FEATURES]
  fieldnames.extend(script_path_names)
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
      script_features(row, page)
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


def script_features(row, page):
  safemax = lambda l : 0 if len(l) == 0 else max(l)
  scripts = [tag.get_text(strip=True) for tag in page.select('script')]
  scripts = [s for s in scripts if len(s) > 0]
  lengths = [len(tag) for tag in scripts]
  row['script_text_ct'] = len(scripts)
  row['script_no_txt'] = row['script'] - row['script_text_ct']
  row['total_script_length'] = sum(lengths)
  row['max_script_length'] = safemax(lengths)
  if len(scripts) > 0:
    row['mean_script_length'] = 1.0 * row['total_script_length'] / len(scripts)
  else:
    row['mean_script_length'] = 0
  line_ct = [s.count(';') for s in scripts]
  row['script_tot_lines'] = sum(line_ct)
  row['script_max_lines'] = safemax(line_ct)
  braces = [s.count('}') for s in scripts]
  row['script_tot_braces'] = sum(braces)
  row['script_max_braces'] = safemax(braces)
  srcs = [tag['src'] for tag in page.select('script[src]')]
  urls = [urlparse(s).netloc for s in srcs]
  urls = [u for u in urls if len(u) > 0]
  row['script_urls'] = len(urls)
  row['script_distinct_urls'] = len(set(urls))
  for url in URL_FEATURES:
    key = 'script_url_' + url
    row[key] = sum([url in s for s in urls])
  paths = [urlparse(s).path for s in srcs]
  for path_part in PATH_FEATURES:
    key = 'script_path_' + path_part
    row[key] = sum([path_part in s for s in paths])


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

