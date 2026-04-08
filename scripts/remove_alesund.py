"""Remove Ålesund rows from all prayer-times pages in kalender-2027.html"""
import re

with open('../kalender-2027.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ålesund block: starts with a row containing rowspan="6">Ålesund</td>
# and includes the next 5 rows (total 6 rows for the city)
# Pattern: the first row has <td class="by" rowspan="6">Ålesund</td>, then 5 more <tr> rows

# We need to remove 6 consecutive <tr> blocks for Ålesund
# The first row contains "Ålesund" in a td.by cell

count = 0
while True:
    # Find Ålesund rowspan marker  
    marker = '>Ålesund</td>'
    idx = content.find(marker)
    if idx == -1:
        break
    
    # Find the start of this <tr>
    tr_start = content.rfind('<tr', 0, idx)
    
    # Find 6 consecutive </tr> endings from this point
    pos = tr_start
    for _ in range(6):
        pos = content.find('</tr>', pos) + 5
    
    # Remove this block
    content = content[:tr_start] + content[pos:]
    count += 1

print(f"Removed {count} Ålesund blocks")

# Also remove from thead if Ålesund appears in column headers (unlikely for row-based layout)

with open('../kalender-2027.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
cities = re.findall(r'<td class="by" rowspan="6">([^<]+)</td>', content)
unique = list(dict.fromkeys(cities))
print(f"Remaining cities: {len(unique)}")
for ci in unique:
    print(f"  {ci}")
