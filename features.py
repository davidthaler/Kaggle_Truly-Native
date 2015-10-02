from bs4 import BeautifulSoup as bs
from csv import DictWriter
import zip_io
import util
import os
from datetime import datetime
import pdb


# Don't forget to get the length/compressed length from the zip archive

def write_sample(outfile, n_pos, n_neg):
  start = datetime.now()
  outpath = os.path.join(util.DATA, 'processed', outfile + '.csv')
  sample = zip_io.generate_sample(n_pos, n_neg, True)
  fieldnames = ['file', 'sponsored', 'tag_ct', 'head_tag_ct', 'body_tag_ct',
                'script', 'head_script', 'body_script', 'meta', 'link',
                'main', 'article', 'section', 'header', 'footer', 'nav',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'p', 
                'a', 'img', 'ul', 'ol', 'li', 'input', 'form', 'button',
                'br', 'em', 'center', 'i', 'b', 'pre', 'code', 'strong', 
                'strike', 'audio', 'video', 'canvas', 'map', 'table', 'tr',
                'th', 'td', 'frame', 'iframe', 'input_button', 'input_text', 
                'input_submit', 'input_reset','input_email', 'input_password', 
                'input_hidden', 'input_search', 'input_file', 'input_radio' ]
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
      row['script'] = len(page.select('script'))
      row['head_script'] = len(page.select('head script'))
      row['body_script'] = len(page.select('body script'))
      row['meta'] = len(page.select('meta'))
      row['link'] = len(page.select('link'))
      row['main'] = len(page.select('main'))
      row['article'] = len(page.select('article'))
      row['section'] = len(page.select('section'))
      row['header'] = len(page.select('header'))
      row['footer'] = len(page.select('footer'))
      row['nav'] = len(page.select('nav'))
      row['h1'] = len(page.select('h1'))
      row['h2'] = len(page.select('h2'))
      row['h3'] = len(page.select('h3'))
      row['h4'] = len(page.select('h4'))
      row['h5'] = len(page.select('h5'))
      row['h6'] = len(page.select('h6'))
      row['div'] = len(page.select('div'))
      row['span'] = len(page.select('span'))
      row['p'] = len(page.select('p'))
      row['a'] = len(page.select('a'))
      row['img'] = len(page.select('img'))
      row['ul'] = len(page.select('ul'))
      row['ol'] = len(page.select('ol'))
      row['li'] = len(page.select('li'))
      row['input'] = len(page.select('input'))
      row['form'] = len(page.select('form'))
      row['button'] = len(page.select('button'))
      row['br'] = len(page.select('br'))
      row['em'] = len(page.select('em'))
      row['center'] = len(page.select('center'))
      row['i'] = len(page.select('i'))
      row['b'] = len(page.select('b'))
      row['pre'] = len(page.select('pre'))
      row['code'] = len(page.select('code'))
      row['strong'] = len(page.select('strong'))
      row['strike'] = len(page.select('strike'))
      row['audio'] = len(page.select('audio'))
      row['video'] = len(page.select('video'))
      row['canvas'] = len(page.select('canvas'))
      row['map'] = len(page.select('map'))
      row['table'] = len(page.select('table'))
      row['tr'] = len(page.select('tr'))
      row['th'] = len(page.select('th'))
      row['td'] = len(page.select('td'))
      row['frame'] = len(page.select('frame'))
      row['iframe'] = len(page.select('iframe'))
      row['input_button'] = len(page.select('input[type=button]'))
      row['input_text'] = len(page.select('input[type=text]'))
      row['input_submit'] = len(page.select('input[type=submit]'))
      row['input_reset'] = len(page.select('input[type=reset]'))
      row['input_email'] = len(page.select('input[type=email]'))
      row['input_password'] = len(page.select('input[type=password]'))
      row['input_hidden'] = len(page.select('input[type=hidden]'))
      row['input_search'] = len(page.select('input[type=search]'))
      row['input_file'] = len(page.select('input[type=file]'))
      row['input_radio'] = len(page.select('input[type=radio]'))
      writer.writerow(row)
  finish = datetime.now()
  print 'Elapsed time: %d sec.' % (finish - start).seconds
