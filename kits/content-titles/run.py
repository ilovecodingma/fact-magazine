# -*- coding: utf-8 -*-
"""내용 하네스 2: 제목 다듬기. 틀에 끼운 제목 후보 → 자연스러운 제목 5개와 고른 이유. 파이썬 기본 기능만.
사용: python -X utf8 run.py [제목후보.txt] [결과.md]
제목후보.txt: 한 줄에 후보 하나(예: 「기초연금 금액, 공식 자료로 확인한 내용」). 쉼표 앞부분을 검색어로 본다."""
import sys

in_file = sys.argv[1] if len(sys.argv) > 1 else '제목후보.txt'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
PAT = [
    ('{q} 총정리: 숫자와 날짜 한눈에', '검색어가 맨 앞에 있고, 글에서 얻을 것(숫자·날짜)을 약속한다.'),
    ('{q} 2026년 기준, 공식 자료로 확인', '연도가 있어 최신 글로 읽히고, 「공식 자료」로 신뢰를 준다.'),
    ('{q}, 헷갈리기 쉬운 점만 정리', '독자가 막히는 지점을 겨냥해 클릭할 이유를 만든다.'),
    ('{q}, 어디서 확인하나? 기관 안내 모음', '질문형이라 검색창 문장과 가깝고, 답(기관 안내)이 있다고 알려 준다.'),
    ('{q} 신청 전에 볼 숫자 3가지', '숫자(3가지)가 있어 분량이 짐작되고, 신청 직전의 독자를 겨냥한다.'),
]
base = []
for l in open(in_file, encoding='utf-8'):
    l = l.strip()
    if l:
        q = l.split(',')[0].strip()
        if q not in base:
            base.append(q)
lines = ['# 제목 다듬기\n',
         '규칙: 과장(충격·대박)·느낌표 없음, 검색어를 앞쪽에, 질문에 답이 되는 제목. 아래는 틀로 만든 후보이니 마지막은 사람이 고른다.\n']
for q in base:
    lines.append('## %s' % q)
    for i, (t, why) in enumerate(PAT, 1):
        lines.append('%d. %s — 이유: %s' % (i, t.format(q=q), why))
    lines.append('')
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('검색어 %d개 × 제목 5개 → %s' % (len(base), out_file))
