"""Shared company/product navigation and explicitly scoped footer; no feature status."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
def e(s):return html.escape(s,quote=True)
def data():return json.loads((ROOT/'data/site-navigation.json').read_text())
def header(scope='company',current=''):
 d=data();label='Company navigation'if scope=='company'else'Aflow Read navigation'
 brand='<a class="brand" href="/" aria-label="Aflow Labs home"><span class="brand-mark" aria-hidden="true">A</span><span>Aflow Labs</span></a>'if scope=='company'else'<a class="read-brand" href="/aflow-read/" aria-label="Aflow Read home"><img src="/assets/aflow-read/app-icon.png" alt="" width="42" height="42">Aflow Read</a>'
 links=''.join('<a href="'+e(x['href'])+'" aria-label="'+e(x['label'])+'"'+(' aria-current="page"'if x['key']==current else'')+'>'+e(x['label'])+'</a>'for x in d[scope])
 return '<!-- shared-shell-header --><header class="site-header shell-header">'+brand+'<nav class="site-nav desktop-nav" aria-label="'+label+'">'+links+'</nav><details class="shell-mobile-menu"><summary aria-label="'+('Company menu'if scope=='company'else'Aflow Read menu')+'"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18"><path d="M2 4h14M2 9h14M2 14h14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>Menu</summary><nav class="mobile-panel" aria-label="'+label+'">'+links+'</nav></details></header><!-- /shared-shell-header -->'
def footer():
 groups=''.join('<section class="footer-group" aria-label="'+e(g['label'])+' links"><h2>'+e(g['label'])+'</h2>'+''.join('<a href="'+e(x['href'])+'">'+e(x['label'])+'</a>'for x in g['links'])+'</section>'for g in data()['footerGroups'])
 return '<!-- shared-shell-footer --><footer class="site-footer grouped-footer"><div class="footer-columns">'+groups+'</div><p class="copyright">© 2026 Aflow Labs Limited</p></footer><!-- /shared-shell-footer -->'
