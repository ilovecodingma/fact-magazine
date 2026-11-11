# -*- coding: utf-8 -*-
"""하네스 3: 질문형 검색어만 고르기. 파이썬 기본 기능만.
사용: python -X utf8 run.py [입력.tsv] [결과.tsv]
입력 한 줄: 검색어<탭>시드<탭>상태(있으면). 상태가 「겹침」인 줄은 건너뛴다.
질문형 = 답이 숫자·날짜·방법인 말(언제, 얼마, 기간, 조건, 신청, 방법, 기준, 한도, 대상, 자격...)."""
import sys

in_file = sys.argv[1] if len(sys.argv) > 1 else '입력.tsv'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.tsv'
Q = ['언제', '얼마', '기간', '조건', '신청', '방법', '기준', '한도', '대상', '자격', '금액', '지급일', '인상', '계산', '변경']
# 이 사이트 범위 밖(사람 이야기·사건)은 뺀다
NO = ['논란', '열애', '결혼', '이혼', '사망', '구속', '의혹']
out = []
for line in open(in_file, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if not p or not p[0]:
        continue
    q, seed = p[0], (p[1] if len(p) > 1 else '')
    if len(p) > 2 and p[2] == '겹침':
        continue
    rest = q.replace(seed, ' ') if seed else q   # 시드 글자는 빼고 판단
    if any(n in rest for n in NO) or not any(k in rest for k in Q):
        continue
    out.append((q, seed))
with open(out_file, 'w', encoding='utf-8', newline='\n') as f:
    for q, s in out:
        f.write('%s\t%s\n' % (q, s))
print('질문형 %d개 → %s' % (len(out), out_file))
