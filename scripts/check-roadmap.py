#!/usr/bin/env python3
"""Offline roadmap build and release-boundary checks; no network or date changes."""
from pathlib import Path
from html.parser import HTMLParser
import argparse,copy,importlib.util,json,re,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('roadmap',ROOT/'scripts/build-roadmap.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--release-evidence',type=Path);args=parser.parse_args()
proof=json.loads(args.release_evidence.read_text())if args.release_evidence else None
d=json.loads(m.SOURCE.read_text());m.validate(d,proof)
assert m.OUTPUT.read_text()==m.render(d),'generated roadmap stale'
original=json.dumps(d,sort_keys=True)
checks=[]
def reject(name,mutate,proof=None):
    x=copy.deepcopy(d);mutate(x)
    try:m.validate(x,proof)
    except (ValueError,KeyError,TypeError):checks.append(name);return
    raise AssertionError('unsafe data accepted: '+name)
reject('unknown status',lambda x:x['features'][0].update(status='soon'))
reject('duplicate identity',lambda x:x['features'][1].update(id=x['features'][0]['id']))
def promote_internal(x):
    x['publication'].update(phase='prelaunch',acceptedPublicRelease=None)
    x['features'][0].update(status='available',releasedVersion='1.0')
reject('TestFlight is not public availability',promote_internal)
release={'version':'1.0','releasedOn':'2026-11-05','appStoreURL':'https://apps.apple.com/nz/app/example/id123456789'}
def promote(x):
    x['publication'].update(phase='released',acceptedPublicRelease=release)
    x['features'][0].update(status='available',releasedVersion='1.0')
reject('public release requires evidence',promote)
reject('internal acceptance evidence rejected',promote,dict(release,publicReleaseAccepted=False))
reject('mismatched accepted release rejected',promote,dict(release,publicReleaseAccepted=True,version='2.0'))
x=copy.deepcopy(d);promote(x);m.validate(x,dict(release,publicReleaseAccepted=True));checks.append('matching accepted-public-release boundary')
x=copy.deepcopy(d);x['features'][0]['title']='<script>alert("x")</script>'
assert '<script>'not in m.render(x)and '&lt;script&gt;'in m.render(x);checks.append('content escaped')
assert json.dumps(d,sort_keys=True)==original;checks.append('review date and source unchanged')
class Document(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.refs=[];self.h1=0;self.main=0;self.canonical=[];self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:assert a['id']not in self.ids,'duplicate HTML ID';self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='main':self.main+=1
        if tag=='img':assert 'alt'in a,'image missing alt';self.images.append(a)
        if tag=='link'and a.get('rel')=='canonical':self.canonical.append(a['href'])
        for k in ['href','src']:
            if k in a:self.refs.append(a[k])
        if tag in ['script','iframe','form']:raise AssertionError('unexpected active content')
pages={}
for page in ROOT.rglob('*.html'):
    if '.git'in page.parts:continue
    parsed=Document();parsed.feed(page.read_text());pages[page]=parsed
for page,parsed in pages.items():
    for ref in parsed.refs:
        u=urllib.parse.urlparse(ref)
        if u.scheme or u.netloc:continue
        target=(ROOT/u.path.lstrip('/'))if u.path.startswith('/')else page.parent/u.path
        if not u.path:target=page
        if target.is_dir():target=target/'index.html'
        assert target.is_file(),f'broken local link {page.relative_to(ROOT)} -> {ref}'
        if u.fragment and target.suffix=='.html':
            other=pages.get(target.resolve())
            if other is None:other=Document();other.feed(target.read_text())
            assert u.fragment in other.ids,f'broken fragment {ref}'
road=pages[m.OUTPUT]
assert road.h1==1 and road.main==1
assert road.canonical==['https://aflowlabs.com/aflow-read/roadmap/']
assert all(s in road.ids for s in m.STATUSES)
assert not re.search(r'\b[0-9a-f]{40}\b|/Users/|/Volumes/|LAUNCH-[A-Z]|TestFlight',m.OUTPUT.read_text()),'internal evidence leaked into public page'
checks+=['all site local assets/routes/fragments resolve','single h1/main and exact canonical','no active embeds or tracking','no internal IDs or private paths']
print(json.dumps({'status':'PASS','checks':checks,'HTMLPagesChecked':len(pages),'futureFeatures':len(d['features']),'launchPreviewCards':len(d['launchFoundation']),'availableFeatures':sum(f['status']=='available'for f in d['features']),'lastReviewed':d['lastReviewed']},indent=2))
