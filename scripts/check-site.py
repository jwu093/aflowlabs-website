#!/usr/bin/env python3
"""Static company/product boundary and accessible-content regression checks."""
from pathlib import Path
from html.parser import HTMLParser
import json,re
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/site-navigation.json').read_text())
assert [x['label']for x in d['company']]==['Home','Products','About','Contact']
assert [x['label']for x in d['product']]==['Overview','Features','Roadmap','Support','Privacy','Aflow Labs']
assert [x['label']for x in d['footerGroups']]==['Aflow Read','DwellCheck','Company']
class Page(HTMLParser):
 def __init__(self):super().__init__();self.h1=0;self.main=0;self.links=[];self.summaries=0;self.images=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='h1':self.h1+=1
  if t=='main':self.main+=1
  if t=='summary':self.summaries+=1
  if t=='img':assert a.get('alt')is not None;self.images.append(a)
  if t=='script':assert a.get('src')=='/assets/navigation.js'and'defer'in a
  assert not any(k.lower().startswith('on')for k in a),'unclassified inline behavior'
for rel in ['index.html','aflow-read/index.html','aflow-read/roadmap/index.html','support/aflow-read/index.html','legal/aflow-read/privacy/index.html','privacy/index.html','support/index.html','terms/index.html']:
 text=(ROOT/rel).read_text();p=Page();p.feed(text)
 assert p.h1==1 and p.main==1,rel
 assert 'Skip to content'in text and 'shared-shell-header'in text and 'shared-shell-footer'in text,rel
 assert p.summaries>=1 and 'aria-label='in text,rel
home=(ROOT/'index.html').read_text()
assert home.index('id="products"')<home.index('id="dwellcheck"')
assert 'In development'in home
product=(ROOT/'aflow-read/index.html').read_text()
if json.loads((ROOT/'data/aflow-read-roadmap.json').read_text())['publication']['phase']=='prelaunch':
 assert 'Preparing for launch'in home and 'Preparing for launch'in product
assert 'iphone-reader.jpeg'in product and 'iphone-appearance.jpeg'in product
assert 'structured Cloud library sync is not part of the Free launch'in product
support=(ROOT/'support/aflow-read/index.html').read_text()
assert all(x in support for x in ['Add Library Folder','Show books with multiple files','Consolidation Stopped','Saving Library','Restore Access','Go back to','Settings → Send Feedback'])
assert 'Purchase-help instructions will be added after the final App Store configuration is verified'in support
print(json.dumps({'status':'PASS','scope':'static hierarchy, generated shells, truthful prelaunch boundaries and semantic content','pages':8},indent=2))
