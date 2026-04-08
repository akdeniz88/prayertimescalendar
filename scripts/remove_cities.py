"""Remove Bodø and Tromsø rows from all prayer-times pages in kalender-2027.html"""
import re

with open('../kalender-2027.html', 'r', encoding='utf-8') as f:
    content = f.read()

for city in ['Bodø', 'Tromsø']:
    count = 0
    while True:
        marker = f'>{city}</td>'
        idx = content.find(marker)
        if idx == -1:
            break
        tr_start = content.rfind('<tr', 0, idx)
        pos = tr_start
        for _ in range(6):
            pos = content.find('</tr>', pos) + 5
        content = content[:tr_start] + content[pos:]
        count += 1
    print(f"Removed {count} {city} blocks")

with open('../kalender-2027.html', 'w', encoding='utf-8') as f:
    f.write(content)

cities = re.findall(r'<td class="by" rowspan="6">([^<]+)</td>', content)
unique = list(dict.fromkeys(cities))
print(f"\nRemaining cities: {len(unique)}")
for ci in unique:
    print(f"  {ci}")
