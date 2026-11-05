#!/usr/bin/env python3
"""Render a static roadmap from one reviewed JSON source. Never advances dates.

The existing GitHub Pages branch deploys the committed HTML. Run this command
and --check before an approved website commit; no new hosting pipeline required.
"""
from pathlib import Path
import argparse,datetime,html,json,re,sys,urllib.parse
from site_shell import header as site_header,footer as site_footer
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/aflow-read-roadmap.json'
OUTPUT=ROOT/'aflow-read/roadmap/index.html'
STATUSES=('available','up-next','planned','exploring')
def check(condition,message):
    if not condition:raise ValueError(message)
def text(value,name):
    check(isinstance(value,str) and bool(value.strip()),name+' must be nonempty text')
def date(value):
    check(isinstance(value,str),'review date must be text')
    datetime.date.fromisoformat(value)
def validate(d,release_evidence=None):
    check(d.get('schemaVersion')==1,'unsupported schema')
    for k in ['product','tagline','reviewNote','expectations','philosophy']:text(d.get(k),k)
    date(d['lastReviewed'])
    check([s['id']for s in d['sections']]==list(STATUSES),'exact four ordered public sections required')
    for s in d['sections']:
        for k in ['title','eyebrow','description']:text(s.get(k),k)
    check(d['publication']['phase']in ['prelaunch','released'],'invalid publication phase')
    text(d['publication']['notice'],'availability notice')
    for k in ['title','description']:text(d['performance'][k],k)
    check(d['contact']['supportUrl']=='/support/aflow-read/','use existing support route')
    u=urllib.parse.urlparse(d['contact']['url'])
    check(u.scheme=='mailto'and u.path=='help@aflowlabs.com','use approved existing contact')
    ids=set();orders=set()
    for f in d['features']+d['launchFoundation']:
        check(re.fullmatch(r'[a-z][a-z0-9-]*',f['id'])is not None,'invalid feature ID')
        check(f['id']not in ids,'duplicate feature ID');ids.add(f['id'])
        for k in ['title','description']:text(f.get(k),k)
        check(isinstance(f['details'],list)and all(isinstance(x,str)and x.strip()for x in f['details']),'invalid detail list')
    for f in d['features']:
        check(f['status']in STATUSES,'invalid feature status')
        text(f['category'],'category');date(f['lastReviewed'])
        check(type(f['displayOrder'])is int,'display order must be integer')
        key=(f['status'],f['displayOrder']);check(key not in orders,'duplicate section display order');orders.add(key)
        check('tier'not in f and 'price'not in f,'future tiers/prices require a separately qualified schema/product decision')
    available=[f for f in d['features']if f['status']=='available']
    if d['publication']['phase']=='prelaunch':
        check(d['publication']['acceptedPublicRelease']is None and not available,'internal builds must not become Available public releases')
    if available or d['publication']['phase']=='released':
        r=d['publication']['acceptedPublicRelease']
        check(isinstance(r,dict)and release_evidence is not None,'Available requires accepted PUBLIC release evidence, not a milestone or TestFlight upload')
        check(release_evidence.get('publicReleaseAccepted')is True,'public release not accepted')
        for k in ['version','releasedOn','appStoreURL']:check(r.get(k)==release_evidence.get(k),'public release evidence mismatch: '+k)
        date(r['releasedOn']);text(r['version'],'public release version')
        check(urllib.parse.urlparse(r['appStoreURL']).scheme=='https'and urllib.parse.urlparse(r['appStoreURL']).netloc=='apps.apple.com','accepted HTTPS App Store URL required')
        for f in available:check(f.get('releasedVersion')==r['version'],'released-version correspondence required')
    return d
e=lambda x:html.escape(str(x),quote=True)
def card(f,candidate=False):
    category='Launch foundation · pending release'if candidate else f['category']
    details=''.join('<li>'+e(x)+'</li>'for x in f['details'])
    return f'<article class="road-card" id="feature-{e(f["id"])}"><p class="road-category">{e(category)}</p><h3>{e(f["title"])}</h3><p>{e(f["description"])}</p><details><summary>More about this direction</summary><ul>{details}</ul></details></article>'
def render(d):
    nav=''.join(f'<a href="#{s["id"]}">{e(s["title"])}</a>'for s in d['sections'])
    sections=[]
    for index,s in enumerate(d['sections'],1):
        fs=sorted((f for f in d['features']if f['status']==s['id']),key=lambda f:f['displayOrder'])
        content=''.join(card(f)for f in fs)
        if s['id']=='available'and d['publication']['phase']=='prelaunch':
            content='<p class="road-empty">'+e(s['emptyMessage'])+'</p><h3 class="road-preview-title">Prepared for the first release</h3><div class="road-cards">'+''.join(card(f,True)for f in d['launchFoundation'])+'</div>'
        else:content='<div class="road-cards">'+content+'</div>'
        sections.append(f'<section class="road-section" id="{s["id"]}" aria-labelledby="heading-{s["id"]}"><header class="road-section-header"><span class="road-number" aria-hidden="true">0{index}</span><div><p class="eyebrow">{e(s["eyebrow"])}</p><h2 id="heading-{s["id"]}">{e(s["title"])}</h2><p>{e(s["description"])}</p></div></header>{content}</section>')
    return f"""<!doctype html>
<!-- Generated by scripts/build-roadmap.py from data/aflow-read-roadmap.json. Edit the JSON, not feature status in this HTML. -->
<html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Explore Aflow Read’s direction: more reading formats, smarter library organization, Calibre and optional cross-device experiences. Priorities may change."><link rel="canonical" href="https://aflowlabs.com/aflow-read/roadmap/"><title>Roadmap | Aflow Read</title><link rel="icon" href="/assets/aflow-read/mark.svg"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/assets/aflow-read.css"><link rel="stylesheet" href="/assets/aflow-read-roadmap.css"><link rel="stylesheet" href="/assets/site-layout.css"><script src="/assets/navigation.js" defer></script></head>
<body class="read-page roadmap-page"><a class="skip-link" href="#main">Skip to content</a>{site_header('product','roadmap')}
<main id="main" class="read-shell"><section class="road-hero"><div><p class="eyebrow">Built around the books you own</p><h1>A little further.<br>A little more yours.</h1><p class="road-lede">{e(d['tagline'])}</p><p>{e(d['philosophy'])}</p></div><aside class="road-review" aria-label="Roadmap review"><span class="road-review-label">Last reviewed</span><time datetime="{e(d['lastReviewed'])}">{datetime.date.fromisoformat(d['lastReviewed']).strftime('%-d %B %Y')}</time><p>{e(d['reviewNote'])}</p><a href="{e(d['contact']['url'])}">{e(d['contact']['label'])} <span aria-hidden="true">↗</span></a></aside></section>
<div class="road-notice"><strong>Direction, not a deadline.</strong><p>{e(d['expectations'])}</p></div><p class="road-availability">{e(d['publication']['notice'])}</p><nav class="road-jump" aria-label="Roadmap sections">{nav}</nav>
{''.join(sections)}
<aside class="road-performance"><p class="eyebrow">A priority in every phase</p><h2>{e(d['performance']['title'])}</h2><p>{e(d['performance']['description'])}</p></aside>
<section class="road-feedback"><h2>What would make your library feel more yours?</h2><p>Tell us about the reading or library problem you want to solve. Ideas help shape priorities; they are not promises of a particular release.</p><div class="read-actions"><a class="button primary" href="{e(d['contact']['url'])}">{e(d['contact']['label'])}</a><a class="button secondary" href="{e(d['contact']['supportUrl'])}">Get help with Aflow Read</a></div></section></main>
{site_footer()}</body></html>
"""
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--release-evidence',type=Path);a=p.parse_args()
    proof=json.loads(a.release_evidence.read_text())if a.release_evidence else None
    output=render(validate(json.loads(SOURCE.read_text()),proof))
    if a.check:check(OUTPUT.exists()and OUTPUT.read_text()==output,'generated roadmap is stale: run scripts/build-roadmap.py')
    else:OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_text(output)
    print('Roadmap schema, release boundary and generated HTML: PASS')
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError)as ex:raise SystemExit(str(ex))
