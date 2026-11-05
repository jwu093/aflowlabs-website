#!/usr/bin/env python3
"""Build/check the static site without changing roadmap review dates or status."""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from site_shell import ROOT, header, footer

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
parser.add_argument('--release-evidence', type=Path)
args = parser.parse_args()
evidence = ['--release-evidence', str(args.release_evidence)] if args.release_evidence else []

def run(script, flags=()):
    subprocess.run([sys.executable, '-B', str(ROOT / 'scripts' / script), *flags], check=True)

run('build-roadmap.py', (['--check'] if args.check else []) + evidence)
pages = {
    'index.html': ('company', 'home'),
    'aflow-read/index.html': ('product', 'overview'),
    'aflow-read/roadmap/index.html': ('product', 'roadmap'),
    'support/aflow-read/index.html': ('product', 'support'),
    'legal/aflow-read/privacy/index.html': ('product', 'privacy'),
    'privacy/index.html': ('company', ''),
    'support/index.html': ('company', ''),
    'terms/index.html': ('company', ''),
}
for relative, (scope, current) in pages.items():
    path = ROOT / relative
    original = path.read_text()
    rendered = re.sub(r'<!-- shared-shell-header -->.*?<!-- /shared-shell-header -->',
                      lambda _: header(scope, current), original, flags=re.S)
    rendered = re.sub(r'<!-- shared-shell-footer -->.*?<!-- /shared-shell-footer -->',
                      lambda _: footer(), rendered, flags=re.S)
    if args.check:
        assert rendered == original, 'shared shell stale: ' + relative
    else:
        path.write_text(rendered)
run('check-roadmap.py', evidence)
run('check-site.py')
print('Static site, shared shells, roadmap and links: PASS')
