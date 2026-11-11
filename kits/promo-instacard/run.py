# -*- coding: utf-8 -*-
"""알리기 하네스 5: 글 한 편 → 인스타 카드 한 장에 올릴 글자 + 본문 문구 + 해시태그 후보. 파이썬 기본 기능만, 인터넷 안 씀.
사용: python -X utf8 run.py [글.md] [글주소] [결과.md]
카드 글자: 큰 제목 한 줄 / 숫자 하나 / 출처 한 줄. 글자 수 한도를 표시하고 넘치면 「줄이기」로 알린다.
그림은 만들지 않고(카드 그림 키트가 만든다) 올리지도 않는다. 파일까지만."""
import sys, re
from collections import Counter

in_file = sys.argv[1] if len(sys.argv) > 1 else '글.md'
url = sys.argv[2] if len(sys.argv) > 2 else 'https://example.com/글주소/'
out_file = sys.argv[3] if len(sys.argv) > 3 else '결과.md'
LIMIT = {'큰 제목': 20, '숫자 하나': 12, '출처 한 줄': 28, '본문': 300}   # 글자 수 한도(카드가 읽기 쉬운 길이로 정한 실습용 값)
MAX_TAGS = 8
text = open(in_file, encoding='utf-8').read()
lines = text.split('\n')
title = lines[0].lstrip('# ').strip()
big = title.split(',')[0].strip()
src_i = next((i for i, l in enumerate(lines) if l.startswith('## ') and '출처' in l), None)
body = '\n'.join(lines[1:src_i] if src_i else lines[1:])
sources = [l.strip('- ').strip() for l in lines[src_i + 1:] if l.strip().startswith('-')] if src_i is not None else []
# 숫자 하나: 글에서 가장 먼저 나오는 「숫자+단위」, 앞의 낱말 하나를 붙인다
m = re.search(r'([가-힣]{1,6}\s)?(\d[\d,\.]*(?:만원|억원|%|년|월|일|세))', body)
num = ((m.group(1) or '') + m.group(2)).strip() if m else '(숫자 없음)'
# 출처 한 줄: 첫 출처의 기관 이름(쉼표 앞)
src = '출처: ' + (sources[0].split(',')[0].strip() if sources else '(출처 없음)')
para = [p.strip() for p in body.split('\n\n') if p.strip() and not p.startswith(('#', '|', '-'))]
caption = [big + ', 공식 자료로 확인했습니다.']
caption += ['숫자: ' + num, src, '전체 계산과 조건은 프로필 링크 또는 아래 주소에서 볼 수 있습니다.', url]
cap = '\n'.join(caption)
words = re.findall(r'[가-힣A-Za-z]{2,}', title + ' ' + ' '.join(l for l in lines if l.startswith('#')))
STOP = {'확인', '정리', '공식', '자료', '출처', '어디', '얼마', '한도', '까지', '그리고', '누가', '공제', '한눈에', '만원까지'}
tags = ['#' + w for w, _ in Counter(w for w in words if w not in STOP).most_common(MAX_TAGS - 2)] + ['#파이어족뉴스', '#공식자료확인']


def mark(name, s):
    n = len(s)
    return '%s (%d자 / 한도 %d자%s)' % (name, n, LIMIT[name], '' if n <= LIMIT[name] else ' — 줄이기')


out = ['# 인스타 카드 글자 (글: %s)\n' % title, '## 그림 한 장에 올릴 글자',
       '- ' + mark('큰 제목', big) + ': ' + big,
       '- ' + mark('숫자 하나', num) + ': ' + num,
       '- ' + mark('출처 한 줄', src) + ': ' + src,
       '', '## 본문 문구', cap, '(%d자 / 한도 %d자%s)' % (len(cap), LIMIT['본문'], '' if len(cap) <= LIMIT['본문'] else ' — 줄이기'),
       '', '## 해시태그 후보 (%d개, 한도 %d개)' % (len(tags), MAX_TAGS), ' '.join(tags), '',
       '확인: 카드 속 숫자가 글과 같은지, 출처 기관 이름이 맞는지, 과장 낱말이 없는지 본다. 올리기는 사람이 「올려」 한 뒤에만.']
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
over = [k for k, v in [('큰 제목', big), ('숫자 하나', num), ('출처 한 줄', src), ('본문', cap)] if len(v) > LIMIT[k]]
print('큰 제목 %d자 / 숫자 %d자 / 출처 %d자 / 본문 %d자 / 태그 %d개 — 한도 넘는 것: %s → %s' % (len(big), len(num), len(src), len(cap), len(tags), ', '.join(over) or '없음', out_file))
