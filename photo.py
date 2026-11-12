# -*- coding: utf-8 -*-
"""사진 받아 넣기: 낱말(영어)로 사진을 찾아 사이트 안에 파일로 넣는다. 파이썬 기본 기능만 쓴다.
python photo.py "camping tent" posts/_cover/first-night.jpg          글 사진(가로로 긴 것)
python photo.py "frying pan" shop/web/public/p/5.jpg --square        상품 사진(네모)
python photo.py "towel" 어디/사진.jpg --pick 2                        두 번째 후보로(첫 사진이 안 어울릴 때)
python photo.py "towel" --list                                        후보만 보기
찾는 곳: Openverse(api.openverse.org)에서 누구나 조건 없이 쓸 수 있게 풀린 사진(CC0·퍼블릭 도메인)만, 사진 모음 사이트(stocksnap·rawpixel) 것을 먼저.
받은 사진은 그 자리에 파일로 박히므로 올린 뒤에도 바깥 사이트에 기대지 않는다. 어디서 받았는지는 같은 폴더의 _사진출처.json 에 남는다.
받은 뒤에는 사진을 직접 열어 보고(세션이 눈으로) 안 어울리면 --pick 으로 다음 후보를 받는다. 남의 쇼핑몰·블로그의 사진은 가져오지 않는다."""
import json, os, sys, time, urllib.parse, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

UA = {'User-Agent': 'fact-magazine-harness/1.0 (tutorial boilerplate)'}
A = sys.argv[1:]


def search(q, square):
    out = []
    for src in ('stocksnap', 'rawpixel', ''):
        u = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode({'q': q, 'license': 'cc0,pdm', 'page_size': 12, 'aspect_ratio': 'square,wide' if square else 'wide', 'category': 'photograph', **({'source': src} if src else {})})
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read().decode('utf-8'))
        except Exception:
            d = {}
        for r in d.get('results', []):
            if r.get('url') and not r['url'].lower().endswith(('.png', '.svg', '.gif')) and r['url'] not in [x['url'] for x in out]:
                out.append(dict(url=r['url'], title=r.get('title') or '', source=r.get('source'), license=r.get('license'), page=r.get('foreign_landing_url') or '', by=r.get('creator') or ''))
        if len(out) >= 6:
            break
        time.sleep(1)
    return out


def main():
    if not A or A[0].startswith('--'):
        print(__doc__); return 1
    q = A[0]; square = '--square' in A; pick = int(A[A.index('--pick') + 1]) if '--pick' in A else 1
    R = search(q, square)
    if not R:
        print(f'「{q}」로 찾은 사진이 없습니다. 더 흔한 낱말로 바꿔 보세요(예: "tumbler" → "cup").'); return 1
    if '--list' in A or len(A) < 2 or A[1].startswith('--'):
        for i, r in enumerate(R, 1):
            print(f'{i}. [{r["source"]} {r["license"]}] {r["title"][:50]}  {r["url"]}')
        return 0
    r = R[min(pick, len(R)) - 1]; dst = os.path.abspath(A[1]); os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        b = urllib.request.urlopen(urllib.request.Request(r['url'], headers=UA), timeout=40).read()
    except Exception as e:
        print('받지 못했습니다:', repr(e)[:120], '— --pick 으로 다른 후보를 받아 보세요.'); return 1
    if len(b) < 8000:
        print('받은 파일이 너무 작습니다. --pick 으로 다른 후보를 받아 보세요.'); return 1
    open(dst, 'wb').write(b)
    log = os.path.join(os.path.dirname(dst), '_사진출처.json'); L = json.load(open(log, encoding='utf-8')) if os.path.exists(log) else {}
    L[os.path.basename(dst)] = dict(q=q, title=r['title'], source=r['source'], license=r['license'], page=r['page'], by=r['by']); json.dump(L, open(log, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'받았습니다: {os.path.relpath(dst)}  ({len(b) // 1024}KB, {pick}번째 후보 「{r["title"][:40]}」, {r["source"]} {r["license"]}, 후보 {len(R)}개)\n사진을 열어 보고 안 어울리면 --pick {pick + 1}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
