# -*- coding: utf-8 -*-
"""알리기 하네스 4: 한 주 홍보 계획표. 파이썬 기본 기능만, 인터넷 안 씀.
사용: python -X utf8 run.py [글목록.tsv] [결과.md] [시작일 YYYY-MM-DD(월요일)]
글목록.tsv 한 줄: 글 제목<탭>글 주소. 위에서부터 월요일부터 차례로 배정한다.
하루 한도(아래 LIMIT): 블로그 하루 1건, 영상 하루 1건, 소식 메일 주 1회(받겠다고 한 사람에게만). 올리지 않고 표까지만."""
import sys, datetime

in_file = sys.argv[1] if len(sys.argv) > 1 else '글목록.tsv'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
start = datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else datetime.date.today()
LIMIT = {'블로그': 1, '영상': 1, '소식 메일': 1}   # 하루 한도(소식 메일은 주 1회 금요일만)
posts = [l.rstrip('\n').split('\t') for l in open(in_file, encoding='utf-8') if l.strip()]
DAY = '월 화 수 목 금 토 일'.split()
rows = []
for i in range(7):
    d = start + datetime.timedelta(days=i)
    wd = DAY[d.weekday()]
    plan = {'블로그': '', '영상': '', '소식 메일': ''}
    if d.weekday() < 5 and i < len(posts):          # 평일에 글 하나씩
        plan['블로그'] = posts[i][0]
        if i >= 1:
            plan['영상'] = posts[i - 1][0]           # 영상은 하루 늦게(블로그에 먼저 올린 글)
    if d.weekday() == 4:                            # 금요일: 한 주 요약 메일
        plan['소식 메일'] = '이번 주 글 %d편 모음(받겠다고 한 사람에게만)' % min(len(posts), 5)
    rows.append((d, wd, plan))
out = ['# 한 주 홍보 계획표 (%s ~ %s)\n' % (start, start + datetime.timedelta(days=6)),
       '하루 한도: 블로그 %d건 / 영상 %d건 / 소식 메일 주 1회\n' % (LIMIT['블로그'], LIMIT['영상']),
       '| 날짜 | 요일 | 블로그 | 영상 | 소식 메일 |', '|---|---|---|---|---|']
for d, wd, p in rows:
    out.append('| %s | %s | %s | %s | %s |' % (d, wd, p['블로그'] or '-', p['영상'] or '-', p['소식 메일'] or '-'))
cnt = {k: sum(1 for r in rows if r[2][k]) for k in LIMIT}
over = [k for k in LIMIT if k != '소식 메일' and any(1 for r in rows if r[2][k].count('|') > 0)]
out.append('\n한 주 합계: 블로그 %d건 / 영상 %d건 / 소식 메일 %d회. 하루 한도(채널당 %d건)를 넘는 날은 없다.' % (cnt['블로그'], cnt['영상'], cnt['소식 메일'], LIMIT['블로그']))
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('7일 표 → %s (블로그 %d / 영상 %d / 메일 %d)' % (out_file, cnt['블로그'], cnt['영상'], cnt['소식 메일']))
