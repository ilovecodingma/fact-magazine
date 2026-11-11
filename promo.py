# -*- coding: utf-8 -*-
"""알리기 키트: 확인 노트(또는 글) → 블로그용 글 + 짧은 알림 문구 세 가지 길이를 파일로 만든다. **올리지는 않는다**(올리는 것은 사람 또는 로그인된 채널을 다루는 역할).
사용: python promo.py                   가장 최근 노트 1건
      python promo.py notes/노트.json     지정한 노트
      python promo.py --all             노트 전체
      python promo.py --out 폴더         결과 폴더 바꾸기(기본 promo_out/)
결과(노트마다 폴더 하나): 블로그글.md(요약+확인한 사실과 출처+끝에 사이트 링크) · 알림_짧게.txt(40자 안팎) · 알림_보통.txt(80자 안팎) · 알림_길게.txt(140자 안팎)
규칙: 노트에 있는 문장만 쓰고 새로 지어내지 않는다. 사이트 주소가 정해지지 않았으면 링크 자리에 안내 문구를 둔다."""
import glob, json, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def site():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    for k, env in (('name', 'SITE_NAME'), ('url', 'SITE_URL')):
        if os.environ.get(env):
            S[k] = os.environ[env]
    url = S.get('url', '').rstrip('/')
    return S['name'], ('' if (not url or '프로젝트이름' in url or '내계정' in url) else url)


def cut(t, n):
    """n 자 안팎으로 자른다 — 문장 끝(마침표·물음표)에서 자르고 숫자 한가운데서 자르지 않는다."""
    t = ' '.join(t.split())
    if len(t) <= n:
        return t
    head = t[:n]
    import re
    # 숫자 덩어리(1조 6,266억 원 같은 것)가 잘려 앞뒤가 달라지지 않게, 끝에 걸친 숫자·단위 낱말은 통째로 뺀다
    while True:
        m = re.search(r'(?:^|\s)(\S*\d\S*|원|명|달러)$', head.rstrip())
        nxt = t[len(head.rstrip()):len(head.rstrip()) + 1]
        if m and (nxt not in ('', ' ')) or (m and re.search(r'\d[\d,.]*[조억만천]$', head.rstrip())):
            head = head.rstrip()[:m.start(1)].rstrip()
            continue
        break
    for sep in ('. ', '? ', '다. ', ' '):
        k = head.rfind(sep)
        if k > n * 0.5:
            return head[:k + (1 if sep.endswith('. ') or sep.endswith('? ') else 0)].rstrip(' .,') + '…'
    return head.rstrip() + '…'


def make(path, name, url, out):
    n = json.load(open(path, encoding='utf-8'))
    link = f'{url}/n/{n["id"]}/' if url else '(공개 주소가 정해지면 노트 링크가 들어갑니다)'
    d = os.path.join(out, n['id'])
    os.makedirs(d, exist_ok=True)
    facts = ''.join(f'- {f["text"]} (출처: {f["source"]}, {f["url"]})\n' for f in n.get('facts', [])) or '- 공식 자료에서 같은 내용을 아직 찾지 못했습니다.\n'
    unc = ''.join(f'- {x}\n' for x in n.get('unconfirmed', []))
    blog = (f'# {n["title"]}\n\n> {n["question"]}\n\n**판정: {n["verdict"]}** ({n["date"]} 기준)\n\n{n["summary"]}\n\n## 확인한 사실\n{facts}\n'
            + (f'## 아직 확인 안 된 것\n{unc}\n' if unc else '') + f'---\n공식 자료로 한 번 더 확인합니다. 노트 전문과 출처: {link}\n— {name}\n')
    open(os.path.join(d, '블로그글.md'), 'w', encoding='utf-8').write(blog)
    base = f'[{n["verdict"]}] {n["title"]}'
    open(os.path.join(d, '알림_짧게.txt'), 'w', encoding='utf-8').write(cut(base, 40) + (f' {link}' if url else '') + '\n')
    open(os.path.join(d, '알림_보통.txt'), 'w', encoding='utf-8').write(cut(f'{base} — {n["summary"]}', 80) + (f'\n{link}' if url else '') + '\n')
    open(os.path.join(d, '알림_길게.txt'), 'w', encoding='utf-8').write(cut(f'{base}\n{n["question"]} {n["summary"]}', 140) + f'\n노트 전문·출처: {link}\n')
    return d


def main():
    args = sys.argv[1:]
    out = os.path.join(HERE, args[args.index('--out') + 1]) if '--out' in args else os.path.join(HERE, 'promo_out')
    paths = [a for a in args if a.endswith('.json')]
    allnotes = sorted((p for p in glob.glob(os.path.join(HERE, 'notes', '*.json')) if not json.load(open(p, encoding='utf-8')).get('example')), reverse=True)
    if not paths:
        paths = allnotes if '--all' in args else allnotes[:1]
    if not paths:
        sys.exit('알릴 노트가 없습니다.')
    name, url = site()
    for p in paths:
        print('만듦:', make(p, name, url, out))
    print('올리지는 않았습니다. 파일을 읽어 보고 사람이(또는 로그인된 채널을 다루는 역할이) 올립니다.')


if __name__ == '__main__':
    main()
