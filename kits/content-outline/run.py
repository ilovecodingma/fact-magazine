# -*- coding: utf-8 -*-
"""내용 하네스 1: 글 뼈대 만들기. 검색어 묶음 → 소제목과 각 소제목에서 답할 질문. 파이썬 기본 기능만.
사용: python -X utf8 run.py [묶음.txt] [결과.md]
묶음.txt: 한 줄에 검색어 하나(같은 주제 묶음). 첫 줄이 대표 검색어."""
import sys

in_file = sys.argv[1] if len(sys.argv) > 1 else '묶음.txt'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
qs = [l.strip() for l in open(in_file, encoding='utf-8') if l.strip()]
rep = qs[0]
# 검색어에 들어 있는 말 → (소제목, 그 소제목에서 답할 질문)
RULES = [
    (['금액', '얼마', '한도'], '금액과 한도', '얼마까지(얼마를) 받거나 낼 수 있나?'),
    (['신청', '방법', '신청방법'], '신청 방법', '어디서 어떻게 신청하나?'),
    (['기간', '언제', '지급일', '날짜'], '기간과 날짜', '언제부터 언제까지, 언제 지급되나?'),
    (['조건', '자격', '대상', '기준', '재산'], '대상과 조건', '누가 해당하고, 어떤 기준을 보나?'),
    (['계산'], '계산 예시', '숫자를 넣으면 얼마가 되나?'),
]
secs, used = [], set()
for q in qs:
    for keys, h, ques in RULES:
        if any(k in q for k in keys) and h not in used:
            used.add(h)
            secs.append((h, ques, q))
lines = ['# 글 뼈대: %s\n' % rep,
         '## 1. 결론부터',
         '- 답할 질문: 가장 많이 궁금해하는 한 가지(%s)에 두세 문장으로 먼저 답하기' % rep,
         '- 근거로 쓸 공식 자료: (법령·기관 안내 주소)\n']
for i, (h, ques, q) in enumerate(secs, 2):
    lines += ['## %d. %s' % (i, h), '- 답할 질문: %s' % ques,
              '- 이 소제목에 담을 검색어: %s' % q, '- 근거로 쓸 공식 자료: (법령·기관 안내 주소)\n']
lines += ['## %d. 확인한 출처' % (len(secs) + 2), '- 직접 열어 본 주소만 적기']
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('소제목 %d개(결론·출처 제외) → %s' % (len(secs), out_file))
