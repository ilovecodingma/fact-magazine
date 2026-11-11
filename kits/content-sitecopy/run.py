# -*- coding: utf-8 -*-
"""내용 하네스 4: 사이트 문구 세트. 사이트 이름·주제 → 한 줄 소개·title·description·메뉴 이름. 파이썬 기본 기능만.
사용: python -X utf8 run.py "<사이트 이름>" "<주제>" [결과.md]
예: python -X utf8 run.py "파이어족 뉴스" "돈·생활 뉴스 속 제도·숫자" 결과.md
주제는 「…를 공식 자료로 확인」 앞에 들어갈 말."""
import sys

name = sys.argv[1] if len(sys.argv) > 1 else '내 사이트 이름'
topic = sys.argv[2] if len(sys.argv) > 2 else '뉴스 속 제도·숫자'
out_file = sys.argv[3] if len(sys.argv) > 3 else '결과.md'
title = '%s | %s를 공식 자료로 확인' % (name, topic)
desc = '뉴스에 나온 숫자와 날짜를 정부·공공기관 자료로 대조해 확인됨·일부만 확인됨·아직 확인 안 됨으로 알려 드립니다.'
lines = ['# 사이트 문구 세트: %s\n' % name,
         '- 한 줄 소개: %s를 공식 자료로 한 번 더 맞춰 보는 작은 정보 사이트' % topic,
         '- title(검색 결과 제목, 40자 안쪽 권장): %s (%d자)' % (title, len(title)),
         '- description(검색 결과 설명, 100자 안쪽 권장): %s (%d자)' % (desc, len(desc)),
         '- 메뉴 이름: 오늘의 확인 / 확인하는 방법 / 소개 / 문의 / 개인정보 처리방침',
         '',
         '손볼 곳: 이름 말고 사이트가 하는 일이 첫 문장에 보이는지, 과장 낱말이 없는지 본다.']
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print(title, '→', out_file)
