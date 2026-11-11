# -*- coding: utf-8 -*-
"""알리기 하네스 3: 글 한 편 → 쇼츠 제목·설명·첫 3초 문장 후보. 파이썬 기본 기능만, 인터넷 안 씀.
사용: python -X utf8 run.py [글.md] [글주소] [결과.md]  (올리지 않고 파일까지만)
규칙: 제목은 질문형 40자 안쪽, 과장 없음. 첫 3초 문장은 짧게(18자 안쪽 권장), 숫자나 질문으로 시작."""
import sys, re

in_file = sys.argv[1] if len(sys.argv) > 1 else '글.md'
url = sys.argv[2] if len(sys.argv) > 2 else 'https://example.com/글주소/'
out_file = sys.argv[3] if len(sys.argv) > 3 else '결과.md'
text = open(in_file, encoding='utf-8').read()
lines = text.split('\n')
title = lines[0].lstrip('# ').strip()
core = title.split(',')[0].strip()
src_i = next((i for i, l in enumerate(lines) if l.startswith('## ') and '출처' in l), None)
body = '\n'.join(lines[1:src_i] if src_i else lines[1:])
nums = []
for m in re.finditer(r'\d[\d,\.]*(?:만원|억원|%|년|세|가지)', body):
    if m.group(0) not in nums:
        nums.append(m.group(0))
n1 = nums[0] if nums else '숫자'
n2 = nums[1] if len(nums) > 1 else ''
titles = ['%s, 한도가 얼마일까?' % core, '%s 숫자, 공식 자료로 확인했습니다' % core, '%s, 헷갈리는 점 30초 정리' % core]
hooks = ['%s이라는 숫자, 맞을까요?' % n1, '%s, 이것부터 확인하세요' % core,
         ('%s과 %s, 차이를 아세요?' % (n1, n2)) if n2 else '공식 자료로 다시 확인했습니다']
desc = ['%s의 숫자를 공식 자료로 한 번 더 맞춰 봤습니다.' % core, '자세한 계산과 출처는 아래 주소에서 볼 수 있습니다.', url]
out = ['# 쇼츠 문구 (글: %s)\n' % title, '## 제목 후보']
out += ['%d. %s (%d자)' % (i, t, len(t)) for i, t in enumerate(titles, 1)]
out += ['', '## 설명(2줄 + 주소)'] + desc
out += ['', '## 첫 3초 문장 후보'] + ['%d. %s (%d자)' % (i, h, len(h)) for i, h in enumerate(hooks, 1)]
out += ['', '확인: 제목이 40자 안쪽인지, 첫 문장이 숫자나 질문으로 시작하는지, 영상 속 숫자가 글과 같은지 본다.']
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('제목 후보 %d개, 첫 3초 후보 %d개 → %s' % (len(titles), len(hooks), out_file))
