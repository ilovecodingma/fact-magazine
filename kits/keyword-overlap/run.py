# -*- coding: utf-8 -*-
"""하네스 2: 이미 쓴 글과 겹침 대조. 파이썬 기본 기능만.
사용: python -X utf8 run.py [후보.tsv] [이미쓴글.txt] [결과.tsv]
이미쓴글.txt: 이미 쓴 글 제목을 한 줄에 하나씩.
판정: 후보의 시드(또는 후보 속 핵심 낱말)가 이미 쓴 제목에 있으면 「겹침」, 없으면 「새 주제」."""
import sys

cand_file = sys.argv[1] if len(sys.argv) > 1 else '후보.tsv'
used_file = sys.argv[2] if len(sys.argv) > 2 else '이미쓴글.txt'
out_file = sys.argv[3] if len(sys.argv) > 3 else '결과.tsv'

used = [l.strip() for l in open(used_file, encoding='utf-8') if l.strip()]
blob = ' '.join(used).replace(' ', '')
out = []
for line in open(cand_file, encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if not parts or not parts[0]:
        continue
    q = parts[0]
    seed = parts[1] if len(parts) > 1 else q.split()[0]
    # 시드까지 포함해 비교: 시드가 이미 쓴 글 제목에 나오면 같은 주제로 본다
    state = '겹침' if seed.replace(' ', '') in blob else '새 주제'
    out.append((q, seed, state))
with open(out_file, 'w', encoding='utf-8', newline='\n') as f:
    for q, s, st in out:
        f.write('%s\t%s\t%s\n' % (q, s, st))
new = sum(1 for r in out if r[2] == '새 주제')
print('후보 %d개 중 새 주제 %d개, 겹침 %d개 → %s' % (len(out), new, len(out) - new, out_file))
