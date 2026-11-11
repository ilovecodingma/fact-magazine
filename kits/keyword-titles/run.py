# -*- coding: utf-8 -*-
"""하네스 4: 주제 묶음 나누기 + 제목 후보. 파이썬 기본 기능만.
사용: python -X utf8 run.py [입력.tsv] [결과.md] [글 수]
입력 한 줄: 검색어<탭>시드. 시드가 같은 것끼리 한 묶음이 되고, 검색어가 많은 묶음 순으로 글 수만큼 고른다.
묶음마다 대표 검색어(가장 짧은 것)와 제목 후보 2개를 적는다. 제목은 질문에 답이 되는 문장, 과장 없이."""
import sys
from collections import OrderedDict

in_file = sys.argv[1] if len(sys.argv) > 1 else '입력.tsv'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
n_posts = int(sys.argv[3]) if len(sys.argv) > 3 else 3

groups = OrderedDict()
for line in open(in_file, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if p and p[0]:
        groups.setdefault(p[1] if len(p) > 1 else p[0].split()[0], []).append(p[0])
ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))[:n_posts]
lines = ['# 다음에 쓸 글 %d건\n' % len(ranked)]
for i, (seed, qs) in enumerate(ranked, 1):
    rep = min(qs, key=len)
    lines.append('## %d. %s (검색어 %d개)' % (i, seed, len(qs)))
    lines.append('- 대표 검색어: %s' % rep)
    lines.append('- 같은 묶음: %s' % ', '.join(qs[:8]))
    lines.append('- 제목 후보 1: %s, 공식 자료로 확인한 내용' % rep)
    lines.append('- 제목 후보 2: %s, 먼저 볼 숫자와 날짜' % rep)
    lines.append('')
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('묶음 %d개 중 %d건 선택 → %s' % (len(groups), len(ranked), out_file))
