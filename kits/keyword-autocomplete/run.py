# -*- coding: utf-8 -*-
"""하네스 1: 자동완성으로 후보 모으기. 파이썬 기본 기능만, 시드마다 1초 쉼.
사용: python -X utf8 run.py [시드파일] [결과파일]
시드파일: 한 줄에 낱말 하나. 결과: 한 줄에 「검색어<탭>시드」."""
import sys, json, time, urllib.parse, urllib.request

seed_file = sys.argv[1] if len(sys.argv) > 1 else 'seeds.txt'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.tsv'


def suggest(q):
    url = 'https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&q=' + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (keyword study)'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))[1]


seeds = [s.strip() for s in open(seed_file, encoding='utf-8') if s.strip()]
seen, rows = set(), []
for s in seeds:
    try:
        for c in suggest(s):
            if c != s and c not in seen:
                seen.add(c)
                rows.append((c, s))
    except Exception as e:
        print('실패', s, e)
    time.sleep(1)   # 바깥 서비스에는 천천히
with open(out_file, 'w', encoding='utf-8', newline='\n') as f:
    for c, s in rows:
        f.write('%s\t%s\n' % (c, s))
print('시드 %d개 → 후보 %d개 → %s' % (len(seeds), len(rows), out_file))
