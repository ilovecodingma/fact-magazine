# -*- coding: utf-8 -*-
"""중복 점검(공지·중복 키트): 노트·글·용어·위키 제목에서 비슷한 것끼리 짝을 찾는다(글자 2-gram 겹침). 사용: python dupcheck.py [기준 0.5]"""
import glob, json, os, re, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
th = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
T = []
for p in glob.glob(os.path.join(HERE, 'notes', '*.json')):
    n = json.load(open(p, encoding='utf-8')); T.append(('노트', n['title']))
for p in glob.glob(os.path.join(HERE, 'posts', '*.md')):
    m = re.search(r'^# (.+)$', open(p, encoding='utf-8').read(), re.M); T.append(('글', m.group(1) if m else os.path.basename(p)))
gp = os.path.join(HERE, 'kits', 'glossary', 'data', 'terms.json')
if os.path.exists(gp):
    T += [('용어', t['term']) for t in json.load(open(gp, encoding='utf-8'))]
for p in glob.glob(os.path.join(HERE, 'kits', 'wiki', 'data', '*.md')):
    T.append(('위키', os.path.splitext(os.path.basename(p))[0]))
g = lambda s: {s2[i:i + 2] for s2 in [re.sub(r'\s+', '', s)] for i in range(len(s2) - 1)}
hits = 0
for i in range(len(T)):
    for j in range(i + 1, len(T)):
        a, b = g(T[i][1]), g(T[j][1])
        if a and b and len(a & b) / len(a | b) >= th:
            hits += 1; print(f'비슷함 {len(a & b) / len(a | b):.2f}: [{T[i][0]}] {T[i][1]}  ↔  [{T[j][0]}] {T[j][1]}')
print(f'제목 {len(T)}개 점검, 비슷한 짝 {hits}쌍(기준 {th})')
