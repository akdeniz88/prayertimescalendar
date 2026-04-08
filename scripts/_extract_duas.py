# -*- coding: utf-8 -*-
import re

for f in ['uker/uke-01-02.html', 'uker/uke-03-04.html', 'uker/uke-05-06.html']:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()
    m = re.search(r'(<div class="dua-section">.*?</div>\s*</div>)', content, re.DOTALL)
    if m:
        print(f'--- {f} ---')
        print(m.group(1))
        print()
