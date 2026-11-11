# -*- coding: utf-8 -*-
"""조합: 하네스 1 → 2 → 3 → 4 를 이어 돌려 「다음에 쓸 글 3건과 제목」을 만든다.
사용: python -X utf8 run_all.py   (이 폴더에서)
각 단계의 결과 파일을 다음 단계의 입력으로 복사해 넘긴다."""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.dirname(HERE)
PY = [sys.executable, '-X', 'utf8']


def step(folder, args, produced, next_folder=None, next_name=None):
    d = os.path.join(K, folder)
    print('==', folder)
    subprocess.run(PY + ['run.py'] + args, cwd=d, check=True)
    if next_folder:
        shutil.copy(os.path.join(d, produced), os.path.join(K, next_folder, next_name))


step('1_자동완성_모으기', ['seeds.txt', '결과.tsv'], '결과.tsv', '2_겹침_대조', '후보.tsv')
step('2_겹침_대조', ['후보.tsv', '이미쓴글.txt', '결과.tsv'], '결과.tsv', '3_질문형_고르기', '입력.tsv')
step('3_질문형_고르기', ['입력.tsv', '결과.tsv'], '결과.tsv', '4_묶음_제목후보', '입력.tsv')
step('4_묶음_제목후보', ['입력.tsv', '결과.md', '3'], '결과.md')
shutil.copy(os.path.join(K, '4_묶음_제목후보', '결과.md'), os.path.join(HERE, '다음글3건.md'))
print('끝 → 다음글3건.md')
