# -*- coding: utf-8 -*-
"""조합: 키워드 하네스 4개(자동완성 → 겹침 대조 → 질문형 고르기 → 묶음+제목 후보)를 이어 돌려 「다음에 쓸 글 3건과 제목」을 만든다.
사용: python -X utf8 run_all.py [결과파일]      (결과파일을 안 쓰면 이 폴더의 다음글3건.md)
입력: 이 폴더의 seeds.txt(시드) · 이미쓴글.txt(이미 쓴 글 제목). 앞 단계의 결과가 다음 단계의 입력이 된다.
중간 파일은 임시 폴더에만 만들고, 각 단계 스크립트는 옆 키트(keyword-autocomplete 등)의 run.py 를 그대로 쓴다.
바깥 서비스(검색창 자동완성)에는 시드마다 1초 쉬며 요청한다."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.dirname(HERE)
PY = [sys.executable, '-X', 'utf8']
final = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, '다음글3건.md')
tmp = tempfile.mkdtemp(prefix='next3_')


def step(kit, args):
    print('==', kit, flush=True)
    subprocess.run(PY + [os.path.join(K, kit, 'run.py')] + args, cwd=tmp, check=True)


seeds = os.path.join(HERE, 'seeds.txt')
used = os.path.join(HERE, '이미쓴글.txt')
step('keyword-autocomplete', [seeds, os.path.join(tmp, '1.tsv')])
step('keyword-overlap', [os.path.join(tmp, '1.tsv'), used, os.path.join(tmp, '2.tsv')])
step('keyword-questions', [os.path.join(tmp, '2.tsv'), os.path.join(tmp, '3.tsv')])
step('keyword-titles', [os.path.join(tmp, '3.tsv'), os.path.join(tmp, '4.md'), '3'])
shutil.copy(os.path.join(tmp, '4.md'), final)
print(open(final, encoding='utf-8').read())
print('끝 →', final)
