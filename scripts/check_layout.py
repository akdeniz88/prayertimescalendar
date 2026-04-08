# -*- coding: utf-8 -*-
"""Check dua presence on each inn page and verify page order."""
import re

with open('../kalender-2027.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all pages in order
pages = list(re.finditer(r'<div class="pg (b|inn)">', content))
print(f"Total pages: {len(pages)}")
print()

# Check ordering: should alternate b, inn, b, inn...
for i, m in enumerate(pages):
    ptype = m.group(1)
    expected = 'b' if i % 2 == 0 else 'inn'
    ok = '✓' if ptype == expected else '✗ WRONG'
    # Find the week label near this page
    chunk = content[m.start():m.start()+500]
    uke = re.search(r'Uke (\d+)', chunk)
    uke_label = uke.group(0) if uke else '?'
    
    extra = ''
    if ptype == 'inn':
        # Find end of this inn page
        next_pg = pages[i+1].start() if i+1 < len(pages) else len(content)
        inn_content = content[m.start():next_pg]
        has_dua = 'dua-section' in inn_content
        extra = f'  dua: {"✓" if has_dua else "✗ MISSING"}'
    
    print(f"  Page {i+1:2d}: {ptype:3s} {uke_label:8s} {ok}{extra}")
