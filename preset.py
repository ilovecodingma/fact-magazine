# -*- coding: utf-8 -*-
"""부품 묶음 적용: python preset.py 이름   (이름 목록은 python preset.py)
presets.json 의 묶음대로 site.json 의 parts(켜기·끄기)를 바꾼다. 바꾼 뒤 python build.py 를 다시 돌리면 화면에 반영된다."""
import json, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
P = {k: v for k, v in json.load(open(os.path.join(HERE, 'presets.json'), encoding='utf-8')).items() if not k.startswith('_')}
if len(sys.argv) < 2 or sys.argv[1] not in P:
    print('묶음:', ', '.join(P)); sys.exit(0 if len(sys.argv) < 2 else 1)
sp = os.path.join(HERE, 'site.json'); S = json.load(open(sp, encoding='utf-8'))
S['parts'] = P[sys.argv[1]]
json.dump(S, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('적용:', sys.argv[1], '→', {k: v for k, v in S['parts'].items() if v}, '(켜짐만 표시)')
