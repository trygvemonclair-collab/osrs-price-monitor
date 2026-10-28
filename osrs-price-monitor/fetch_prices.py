import json
import os
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = 'https://prices.runescape.wiki/api/v2/osrs'
UA = os.environ.get('OSRS_USER_AGENT', 'PersonalOSRSPriceMonitor/1.0 (personal research; github-actions)')
ITEMS = [
    ('Super strength potion(4)', 'Super strength(4)'),
    ('Super defence potion(4)', 'Super defence(4)'),
    ('Super attack potion(4)', 'Super attack(4)'),
    ('Torstol',),
    ('Super combat potion(4)', 'Super combat(4)'),
    ('Dragon keel parts', 'Dragon keel part'),
    ('Large dragon keel parts', 'Large dragon keel part'),
]
OUT = Path('docs'); OUT.mkdir(exist_ok=True)

def get(endpoint, **params):
    url = BASE + '/' + endpoint
    if params: url += '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as resp:
        return json.load(resp)

def weighted_average(points, field, weight):
    pairs = [(row[field], row.get(weight, 0)) for row in points if row.get(field) is not None and row.get(weight, 0)>0]
    return round(sum(value * count for value, count in pairs)/sum(count for _,count in pairs)) if pairs else None

mapping = get('mapping')
lookup = {str(item['name']).casefold(): item for item in mapping}
latest = get('latest').get('data', {})
output = {'updated_utc': datetime.now(timezone.utc).isoformat(), 'source':'OSRS Wiki Real-time Prices API v2', 'lookback':'24h', 'items':{}}
for alternatives in ITEMS:
    item = next((lookup[name.casefold()] for name in alternatives if name.casefold() in lookup), None)
    if not item:
        output['items'][alternatives[0]] = {'error':'Item name not found in mapping', 'searched_names':list(alternatives)}
        continue
    ident = item['id']
    ts = get('timeseries', id=ident, lookback='24h')
    rows = ts.get('data', [])
    volumes = {'high':sum(r.get('highPriceVolume',0) for r in rows), 'low':sum(r.get('lowPriceVolume',0) for r in rows)}
    output['items'][alternatives[0]] = {
        'id': ident, 'official_name':item['name'], 'buy_limit':item.get('limit'),
        'latest':latest.get(str(ident),{}),
        'volume_24h':volumes,
        'weighted_high_24h':weighted_average(rows,'avgHighPrice','highPriceVolume'),
        'weighted_low_24h':weighted_average(rows,'avgLowPrice','lowPriceVolume'),
        'observations':rows,
        'interval_seconds':ts.get('timestep')
    }
with (OUT/'prices.json').open('w',encoding='utf-8') as f:
    json.dump(output,f,ensure_ascii=False,indent=2)
print('Wrote docs/prices.json with',len(output['items']),'items')
