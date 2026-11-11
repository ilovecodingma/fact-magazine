# -*- coding: utf-8 -*-
"""알리기 하네스 1: 글 한 편 → 블로그용 글(요약 + 출처 + 끝에 사이트 링크). 파이썬 기본 기능만, 인터넷 안 씀.
사용: python -X utf8 run.py [글.md] [글주소] [결과.md]
원문 문장을 그대로 옮기지 않는다: 소제목은 「…를 정리했습니다」 목록으로 바꾸고, 숫자는 숫자 둘레의 짧은 구절만 뽑는다.
끝에서 원문과 겹치는 정도(연속 12글자 겹침 비율)를 재서 보여 준다. 올리지는 않는다(파일까지만)."""
import sys, re

in_file = sys.argv[1] if len(sys.argv) > 1 else '글.md'
url = sys.argv[2] if len(sys.argv) > 2 else 'https://example.com/글주소/'
out_file = sys.argv[3] if len(sys.argv) > 3 else '결과.md'
SITE = '파이어족 뉴스'
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
heads = [l.lstrip('# ').strip() for l in lines if l.startswith('## ') and '출처' not in l]
src_i = next((i for i, l in enumerate(lines) if l.startswith('## ') and '출처' in l), None)
sources = [l for l in lines[src_i + 1:] if l.strip().startswith('-')] if src_i is not None else []
body = '\n'.join(lines[1:src_i] if src_i else lines[1:])
# 숫자 둘레 구절(앞 14글자 + 숫자 + 뒤 6글자)만 뽑는다
facts, seen = [], set()
for m in re.finditer(r'\d[\d,\.]*(?:만원|억원|%|년|월|일|세|가지)', body):
    f = snippet(body, m, 14, 6)
    k = m.group(0)
    if k not in seen and len(facts) < 6:
        seen.add(k)
        facts.append(f)
out = ['# %s, 숫자만 먼저 정리했습니다\n' % title.split(',')[0],
       '%s에서 공식 자료와 맞춰 본 글의 핵심만 추렸습니다. 조건과 계산 예시는 아래 원문 글에서 볼 수 있습니다.\n' % SITE,
       '## 이 글에서 다룬 것']
out += ['- %s' % h for h in heads]
out += ['', '## 핵심 숫자']
out += ['- …%s…' % f for f in facts]
out += ['', '## 출처'] + (sources or ['- (원문 글 끝의 출처 목록 참고)'])
out += ['', '## 더 보기', '원문과 전체 계산 예시: %s' % url,
        '%s는 뉴스에 나온 제도·숫자를 공식 자료로 한 번 더 확인하는 정보 사이트입니다.' % SITE]
result = '\n'.join(out) + '\n'
open(out_file, 'w', encoding='utf-8', newline='\n').write(result)
# 겹침: 결과의 연속 12글자가 원문에도 나오는 비율
orig = re.sub(r'\s', '', text)
res = re.sub(r'\s', '', result)
n = 12
grams = [res[i:i + n] for i in range(0, max(1, len(res) - n + 1))]
hit = sum(1 for g in grams if g in orig)
print('결과 %s — 원문과 겹침 %d%% (12글자 연속 기준). 낮을수록 다시 쓴 것에 가깝다' % (out_file, 100 * hit // max(1, len(grams))))
