# -*- coding: utf-8 -*-
"""하네스 5: 검색어를 단기/중기/장기 칸으로 나누고 지울 날짜를 표시한다. 파이썬 기본 기능만.
사용: python -X utf8 run.py [입력.tsv] [결과.md] [오늘 YYYY-MM-DD]
입력 한 줄: 검색어<탭>처음 본 날(YYYY-MM-DD)<탭>종류(급상승|꾸준) — 종류를 비우면 검색어 말로 짐작한다.
규칙: 급상승(뉴스·사건) → 단기, 처음 본 날 + 4일 뒤 지움 / 제도·일정(연금·세금·신청) → 중기, +14일 뒤 다시 보기 / 꾸준히 찾는 말(방법·기준·계산) → 장기, 지우지 않고 글로 오래 둠."""
import sys, datetime

in_file = sys.argv[1] if len(sys.argv) > 1 else '입력.tsv'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
today = datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else datetime.date.today()
LONG = ['방법', '기준', '계산', '자격', '조건', '대상', '뜻']
MID = ['신청', '지급', '인상', '일정', '기간', '한도', '연장', '시행']
rows = []
for line in open(in_file, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 2 or not p[0]:
        continue
    q, first = p[0], datetime.date.fromisoformat(p[1])
    kind = p[2] if len(p) > 2 and p[2] else ''
    if kind == '급상승':
        tier = '단기'
    elif kind == '꾸준':
        tier = '장기'
    else:
        tier = '장기' if any(k in q for k in LONG) else ('중기' if any(k in q for k in MID) else '단기')
    days = {'단기': 4, '중기': 14, '장기': None}[tier]
    due = first + datetime.timedelta(days=days) if days else None
    if tier == '장기':
        todo = '지우지 않음(글로 오래 둠)'
    elif due <= today:
        todo = '지금 지우거나 결정(기한 지남: %s)' % due
    else:
        todo = '%s 까지 두고 그때 결정' % due
    rows.append((tier, q, first, todo))
rows.sort(key=lambda r: ('단기 중기 장기'.split().index(r[0]), r[1]))
lines = ['# 검색어 칸 나누기 (기준일 %s)\n' % today, '| 칸 | 검색어 | 처음 본 날 | 할 일 |', '|---|---|---|---|']
for t, q, f, todo in rows:
    lines.append('| %s | %s | %s | %s |' % (t, q, f, todo))
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('단기 %d / 중기 %d / 장기 %d → %s' % tuple([sum(1 for r in rows if r[0] == k) for k in ('단기', '중기', '장기')] + [out_file]))
