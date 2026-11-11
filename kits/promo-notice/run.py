# -*- coding: utf-8 -*-
"""알리기 하네스 2: 글 한 편 → 짧은 알림 문구 세 길이(한 줄/세 줄/다섯 줄)와 해시태그 후보. 파이썬 기본 기능만, 인터넷 안 씀.
사용: python -X utf8 run.py [글.md] [글주소] [결과.md]  (올리지 않고 파일까지만)"""
import sys, re
from collections import Counter

in_file = sys.argv[1] if len(sys.argv) > 1 else '글.md'
url = sys.argv[2] if len(sys.argv) > 2 else 'https://example.com/글주소/'
out_file = sys.argv[3] if len(sys.argv) > 3 else '결과.md'
text = open(in_file, encoding='utf-8').read()

def snippet(body, m, left=14, right=6):
    """숫자 둘레를 잘라 오되 낱말 중간에서 끊기지 않게 다듬는다."""
    a, b = max(0, m.start() - left), min(len(body), m.end() + right)
    s = body[a:b].replace(chr(10), ' ')
    if a > 0 and body[a - 1] != ' ' and ' ' in s:
        s = s.split(' ', 1)[1]                 # 앞쪽 잘린 낱말 버리기
    if b < len(body) and body[b] != ' ' and ' ' in s:
        s = s.rsplit(' ', 1)[0]                # 뒤쪽 잘린 낱말 버리기
    return s.strip(' -,.')

lines = text.split('\n')
title = lines[0].lstrip('# ').strip()
src_i = next((i for i, l in enumerate(lines) if l.startswith('## ') and '출처' in l), None)
body = '\n'.join(lines[1:src_i] if src_i else lines[1:])
facts, seen = [], set()
for m in re.finditer(r'\d[\d,\.]*(?:만원|억원|%|년|월|일|세|가지)', body):
    f = snippet(body, m, 10, 3)
    if m.group(0) not in seen:
        seen.add(m.group(0))
        facts.append(f)
agencies = [a for a in ['국세청', '금융감독원', '국가법령정보센터', '고용노동부', '보건복지부', '관세청'] if a in text]
# 해시태그: 제목·소제목의 두 글자 이상 한글 낱말 중 많이 나온 것
words = re.findall(r'[가-힣A-Za-z]{2,}', title + ' ' + ' '.join(l for l in lines if l.startswith('#')))
STOP = {'확인', '정리', '공식', '자료', '출처', '어디', '얼마', '한도', '까지', '그리고', '만원까지', '누가', '공제', '한눈에'}
tags = ['#' + w for w, _ in Counter(w for w in words if w not in STOP).most_common(6)] + ['#파이어족뉴스', '#공식자료확인']
one = '%s — %s' % (title.split(',')[0], url)
three = '\n'.join([title.split(',')[0], '숫자 확인: ' + ' / '.join(f for f in facts[:2]), url])
five = '\n'.join(['[새 글] ' + title.split(',')[0], '공식 자료로 맞춰 본 숫자만 모았습니다.',
                  '확인한 숫자: ' + ' / '.join(f for f in facts[:3]),
                  '근거: ' + (', '.join(agencies[:2]) if agencies else '글 끝의 출처 목록'), url])
out = ['# 알림 문구 (글: %s)\n' % title, '## 한 줄', one, '', '## 세 줄', three, '', '## 다섯 줄', five, '',
       '## 해시태그 후보', ' '.join(tags), '',
       '확인: 줄마다 주소가 맞는지, 과장 낱말(충격·대박)이 없는지, 숫자가 글과 같은지 본다.']
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('한 줄 %d자 / 세 줄 %d자 / 다섯 줄 %d자 → %s' % (len(one), len(three), len(five), out_file))
