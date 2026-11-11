# -*- coding: utf-8 -*-
"""키트 섞기: 고른 키트만 켜진 사이트를 만든다.
사용: python mix.py                      키트 목록과 한 줄 설명
      python mix.py calc glossary search  고른 키트만 켜기(나머지는 끔) → site.json 의 parts 를 바꿈
      python mix.py --add search          지금 켜진 것에 더하기
      python mix.py --off shorts          지금 켜진 것에서 빼기
      python mix.py 예시1                 예시 조합(kits/mixes.json)으로 켜기
바꾼 뒤 python build.py 를 다시 돌리면 화면과 메뉴가 맞춰진다. 키트 하나는 kits/이름/ 폴더(README·kit.json·자료)이고 kit.json 의 parts 가 켜질 부품이다."""
import glob, json, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
KITS = {}
for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json'))):
    k = json.load(open(p, encoding='utf-8')); KITS[k['name']] = k
MIXES = json.load(open(os.path.join(HERE, 'kits', 'mixes.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'kits', 'mixes.json')) else {}
sp = os.path.join(HERE, 'site.json')
S = json.load(open(sp, encoding='utf-8'))
ALL = [k for k in S['parts']]


def main():
    args = sys.argv[1:]
    if not args:
        print('키트:'); [print(f'  {n:10} {k["title"]} — {k["gives"][:60]}') for n, k in KITS.items()]
        print('예시 조합:', ', '.join(MIXES) or '(없음)'); return
    cur = {k for k, v in S['parts'].items() if v}
    if args[0] == '--add':
        want = cur | set(expand(args[1:]))
    elif args[0] == '--off':
        want = cur - set(expand(args[1:]))
    elif args[0] in MIXES:
        want = set(expand(MIXES[args[0]]['kits']))
    else:
        want = set(expand(args))
    S['parts'] = {k: (k in want) for k in ALL}
    json.dump(S, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    lp = os.path.join(HERE, 'site.local.json')   # 내 컴퓨터 설정에 parts 가 따로 있으면 그쪽이 우선이므로 같이 바꾼다
    if os.path.exists(lp):
        L = json.load(open(lp, encoding='utf-8'))
        if 'parts' in L:
            L['parts'] = dict(S['parts']); json.dump(L, open(lp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('켜진 부품:', ', '.join(sorted(want)) or '(없음)'); print('이제 python build.py 를 돌리세요.')


def expand(names):
    """키트 이름 → 부품 이름(kit.json 의 parts). 부품 이름을 그대로 써도 된다."""
    out = []
    for n in names:
        if n in KITS:
            out += KITS[n].get('parts', [n])
        elif n in ALL:
            out.append(n)
        else:
            sys.exit(f'모르는 키트·부품: {n} (python mix.py 로 목록 보기)')
    return out


if __name__ == '__main__':
    main()
