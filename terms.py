# -*- coding: utf-8 -*-
"""용어 설명: 책의 CS 용어(216개)에서 뜻을 찾아 준다. 파이썬 기본 기능만 쓴다.
python run.py 용어 목록                 책의 절별로 용어를 묶어 보여 준다
python run.py 용어 <낱말> [낱말 …]      낱말이 든 용어를 가까운 순으로(용어 이름·영어 이름·뜻에서 찾는다) 다섯 개까지
세션은 이 뜻을 한두 문장으로 전한 뒤 **독자의 지금 폴더에서 실제로 확인한 값**을 붙이고, 책의 절과 더 물어볼 말 하나로 끝낸다(참고/용어_답하는법.md)."""
import json, os, re, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, '참고', '용어.json')
A = sys.argv[1:]


def load():
    try:
        return json.load(open(FILE, encoding='utf-8'))
    except Exception:
        print('용어 자료(참고/용어.json)가 없습니다.'); sys.exit(1)


def norm(t):
    return re.sub(r'[\s·\-_/()]+', '', str(t)).lower()


def listing(D):
    g = {}
    for d in D:
        g.setdefault(d.get('처음 나오는 곳', '(절 없음)'), []).append(d['용어'])
    print(f'용어 {len(D)}개 — 책의 절별')
    for sec, names in g.items():
        print(f'■ {sec} ({len(names)})')
        print('   ' + ' · '.join(n.split('(')[0].strip() for n in names))
    return 0


def find(D, words):
    q = [norm(w) for w in words if w.strip()]
    scored = []
    for d in D:
        raw = d['용어']; name = norm(raw); base = norm(raw.split('(')[0]); eng = norm(raw.split('(')[1].rstrip(')')) if '(' in raw else ''; mean = norm(d.get('뜻', ''))
        s = 0
        for w in q:
            if w in (base, eng):
                s += 100
            elif w in name:
                s += 40
            elif w in mean:
                s += 5
        if s:
            scored.append((s, d))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print(f'「{" ".join(words)}」에 맞는 용어가 책의 용어 목록에 없습니다. 일반 지식으로 짧게 설명하고, 목록에 없다고 말합니다.'); return 1
    for s, d in scored[:5]:
        print(f'■ {d["용어"]}\n  뜻: {d.get("뜻", "")}\n  책의 절: {d.get("처음 나오는 곳", "")}\n  더 물어볼 말: {d.get("물어볼 말", "")}\n')
    return 0


def main():
    D = load()
    if not A or A[0] == '목록':
        return listing(D)
    return find(D, A)


if __name__ == '__main__':
    sys.exit(main())
