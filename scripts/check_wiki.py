"""Check local Markdown targets, page IDs, figures and archived-source hashes.

Run from any directory: python scripts/check_wiki.py
Only structural checks; technical claims require source review.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []
links = 0
page_ids = {}

for path in sorted(ROOT.rglob('*.md')):
    if '.git' in path.parts or 'raw' in path.parts and 'codes' in path.parts:
        continue
    text = path.read_text()
    # The repository uses inline Markdown links, without embedded parentheses
    # in local paths. Ignore fenced code examples when validating targets.
    prose = re.sub(r'```.*?```', '', text, flags=re.S)
    for match in re.finditer(r'!?\[[^\]]*\]\(([^\s)]+)\)', prose):
        target = match.group(1).strip('<>')
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        links += 1
        resolved = path.parent / unquote(parts.path)
        if resolved.resolve().is_relative_to(ROOT / 'raw/codes') and not resolved.exists():
            continue  # Optional local code snapshots are deliberately untracked.
        if not resolved.exists():
            errors.append(f'{path.relative_to(ROOT)}: missing {target}')
    if path.is_relative_to(ROOT / 'wiki') and text.startswith('---\n'):
        meta = text.split('---', 2)[1]
        match = re.search(r'^id:\s*(.+)$', meta, flags=re.M)
        if not match:
            errors.append(f'{path.relative_to(ROOT)}: missing page id')
        elif match[1] in page_ids:
            errors.append(f'{path.relative_to(ROOT)}: duplicate id {match[1]}')
        else:
            page_ids[match[1]] = path

figures = list((ROOT / 'wiki/imgs').glob('*.svg'))
for svg in figures:
    try:
        ET.parse(svg)
    except ET.ParseError as exc:
        errors.append(f'{svg.name}: invalid SVG: {exc}')
    png = svg.with_suffix('.png')
    if not png.exists() or png.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
        errors.append(f'{svg.name}: missing or invalid PNG export')

snapshots = list((ROOT / 'raw/codes').glob('*/snapshot.json'))
for snapshot in snapshots:
    manifest = json.loads(snapshot.read_text())
    for item in manifest['files']:
        path = snapshot.parent / item['path']
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            errors.append(f'{path}: archived source changed or missing')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'OK: {links} local links, {len(page_ids)} page IDs, {len(figures)} figure pairs, '
      f'{len(snapshots)} source snapshot(s). Technical claims need separate review.')
