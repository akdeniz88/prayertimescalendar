import re
with open('../kalender-2027.html', 'r', encoding='utf-8') as f:
    c = f.read()

cities = re.findall(r'<td class="by" rowspan="6">([^<]+)</td>', c)
unique = list(dict.fromkeys(cities))
print(f"Unique cities: {len(unique)}")
for ci in unique:
    print(f"  {ci}")

# Count per first prayer page
first_b = c.split('<div class="pg b">')[1].split('<div class="pg ')[0]
city_count_page1 = len(re.findall(r'rowspan="6"', first_b))
print(f"\nCities on first prayer page: {city_count_page1}")
print(f"Data rows per page: {city_count_page1 * 6}")
