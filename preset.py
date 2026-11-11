# -*- coding: utf-8 -*-
"""부품 켜기: python preset.py 이름        묶음 이름(목록은 python preset.py)
      python preset.py info,games,issue   부품 이름을 쉼표(또는 +)로 나열 — 나열한 것만 켜고 나머지는 끔(묶음에 없는 조합용)
presets.json 의 묶음대로 site.json 의 parts(켜기·끄기)를 바꾼다. 바꾼 뒤 python build.py 를 다시 돌리면 화면에 반영된다."""
import json, os, re, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
P = {k: v for k, v in json.load(open(os.path.join(HERE, 'presets.json'), encoding='utf-8')).items() if not k.startswith('_')}
ALL = list(P['전부'])
sp = os.path.join(HERE, 'site.json'); S = json.load(open(sp, encoding='utf-8'))
if len(sys.argv) >= 2 and sys.argv[1] not in P:
    names = [x.strip() for x in re.split(r'[,+ ]+', sys.argv[1]) if x.strip()]
    bad = [x for x in names if x not in ALL]
    if bad or not names:
        print('모르는 부품:', ', '.join(bad) or sys.argv[1], '/ 부품:', ', '.join(ALL)); sys.exit(1)
    P[sys.argv[1]] = {k: (k in names) for k in ALL}
if len(sys.argv) < 2 or sys.argv[1] not in P:
    print('묶음:', ', '.join(k for k in P if k != '전부' or True), '/ 부품 나열도 됨: ' + ', '.join(ALL)); sys.exit(0 if len(sys.argv) < 2 else 1)
S['parts'] = P[sys.argv[1]]
json.dump(S, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('적용:', sys.argv[1], '→', {k: v for k, v in S['parts'].items() if v}, '(켜짐만 표시)')
