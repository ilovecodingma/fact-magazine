# -*- coding: utf-8 -*-
"""링크 점검(링크 모음 키트): kits/links/data/links.json 의 주소를 하나씩 열어 상태를 본다(한 곳씩 1초 간격). 결과: logs/links.json.
사용: python linkcheck.py"""
import json, os, sys, time, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, 'kits', 'links', 'data', 'links.json'), encoding='utf-8'))
out, bad = [], 0
for g in L:
    for i in g['items']:
        try:
            r = urllib.request.urlopen(urllib.request.Request(i['url'], headers={'User-Agent': 'Mozilla/5.0 (link check)'}), timeout=20)
            st = r.status
        except Exception as e:
            st = getattr(e, 'code', repr(e)[:40])
        ok = st == 200
        bad += 0 if ok else 1
        out.append({'name': i['name'], 'url': i['url'], 'status': st}); print(('열림 ' if ok else '문제 ') + str(st), i['name'], i['url']); time.sleep(1)
os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
json.dump(out, open(os.path.join(HERE, 'logs', 'links.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'점검 {len(out)}개, 문제 {bad}개')
