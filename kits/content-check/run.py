# -*- coding: utf-8 -*-
"""내용 하네스 3: 글 점검. 글 한 편(md) → 출처 없는 숫자 문단, 과장 낱말, 너무 긴 문장을 표시. 파이썬 기본 기능만.
사용: python -X utf8 run.py [글.md] [결과.md]"""
import sys, re

in_file = sys.argv[1] if len(sys.argv) > 1 else '글.md'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
text = open(in_file, encoding='utf-8').read()
SRC = ['http', '출처', '법 제', '법」', '국세청', '금융감독원', '고시', '시행령', '보도자료', '법령', '소득세법', '조세특례제한법']
HYPE = ['충격', '대박', '무조건', '반드시', '최고', '역대급', '놀라운', '필수', '100%', '절대', '폭등', '폭락']
MAX = 80
issues = []
for n, para in enumerate([p.strip() for p in text.split('\n\n') if p.strip()], 1):
    if para.startswith('#') or para.startswith('|'):
        continue
    if re.search(r'\d', para) and not any(s in para for s in SRC):
        issues.append(('출처 없는 숫자', '문단 %d' % n, para[:50] + '…'))
    for s in re.split(r'(?<=[.?!])\s+', para):
        if len(s) > MAX and 'http' not in s:   # 출처 주소 줄은 길어도 괜찮다
            issues.append(('긴 문장(%d자)' % len(s), '문단 %d' % n, s[:50] + '…'))
for w in HYPE:
    for m in re.finditer(re.escape(w), text):
        issues.append(('과장 낱말 「%s」' % w, '%d자째' % m.start(), text[max(0, m.start() - 15):m.start() + 20].replace('\n', ' ')))
lines = ['# 글 점검: %s\n' % in_file, '| 종류 | 위치 | 내용 |', '|---|---|---|']
lines += ['| %s | %s | %s |' % i for i in issues]
if not issues:
    lines.append('| (표시할 것 없음) | | |')
lines.append('\n표시 %d건. 표시는 사람이 볼 곳을 알려 줄 뿐, 맞고 틀림을 판정하지 않는다.' % len(issues))
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('표시 %d건 → %s' % (len(issues), out_file))
