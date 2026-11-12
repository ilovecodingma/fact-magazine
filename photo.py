# -*- coding: utf-8 -*-
"""사진 받아 넣기: 낱말(영어)로 사진을 찾아 사이트 안에 파일로 넣는다. 파이썬 기본 기능만 쓴다.
python photo.py "camping tent" posts/_cover/first-night.jpg          글 사진(가로로 긴 것)
python photo.py "frying pan" shop/web/public/p/5.jpg --square        상품 사진(네모)
python photo.py "towel" 어디/사진.jpg --pick 2                        두 번째 후보로(첫 사진이 안 어울릴 때)
python photo.py "towel" --list                                        후보만 보기
찾는 곳: Openverse(api.openverse.org)에서 누구나 조건 없이 쓸 수 있게 풀린 사진(CC0·퍼블릭 도메인)만, 사진 모음 사이트(stocksnap·rawpixel) 것을 먼저.
받은 사진은 그 자리에 파일로 박히므로 올린 뒤에도 바깥 사이트에 기대지 않는다. 어디서 받았는지는 같은 폴더의 _사진출처.json 에 남는다.
받은 뒤에는 사진을 직접 열어 보고(세션이 눈으로) 안 어울리면 --pick 으로 다음 후보를 받는다. 남의 쇼핑몰·블로그의 사진은 가져오지 않는다."""
import hashlib, json, os, sys, tempfile, time, urllib.parse, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

UA = {'User-Agent': 'fact-magazine-harness/1.0 (tutorial boilerplate)'}
A = sys.argv[1:]


FAIL = [0]
BAD = ('naked', 'nude', 'nudity', 'lingerie', 'bikini', 'underwear', 'corpse', 'blood')


def search(q, square):
    """후보를 찾는다. 같은 낱말은 30분 동안 같은 후보·같은 차례로 돌려준다(--list 로 본 번호와 --pick 번호가 어긋나지 않게)."""
    cache = os.path.join(tempfile.gettempdir(), 'photo_' + hashlib.md5((q + str(square)).encode()).hexdigest()[:12] + '.json')
    if os.path.exists(cache) and time.time() - os.path.getmtime(cache) < 1800:
        try:
            return json.load(open(cache, encoding='utf-8'))
        except Exception:
            pass
    out = []; err = [0]

    def ask(query, **extra):
        u = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode({'q': query, 'license': 'cc0,pdm', 'page_size': 20, **extra})
        d = None
        for _ in range(2):   # 찾는 곳이 가끔 응답하지 않는다(504): 한 번 더 해 본다
            try:
                d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=12).read().decode('utf-8')); break
            except Exception:
                err[0] += 1; time.sleep(1.5)
        if d is None:
            return
        for r in d.get('results', []):
            if r.get('url') and not r.get('mature') and not any(b in (r.get('title') or '').lower() for b in BAD) and not r['url'].lower().endswith(('.png', '.svg', '.gif')) and r['url'] not in [x['url'] for x in out]:
                out.append(dict(url=r['url'], title=r.get('title') or '', source=r.get('source'), license=r.get('license'), page=r.get('foreign_landing_url') or '', by=r.get('creator') or ''))
    # 좁게 찾고, 없으면 조건을 하나씩 푼다: 모양(네모·가로) → 사진 갈래 → 낱말을 줄여서(끝 낱말, 첫 낱말)
    words = q.split()
    tries = [(q, dict(aspect_ratio='square,wide' if square else 'wide', category='photograph')), (q, dict(category='photograph')), (q, {})]
    if len(words) > 1:
        tries += [(' '.join(words[:2]), {}), (words[-1], dict(category='photograph')), (words[0], dict(category='photograph'))]
    for query, extra in tries:
        ask(query, **extra)
        if len(out) >= 4:
            break
        time.sleep(0.6)
    order = {'stocksnap': 0, 'rawpixel': 1}
    out.sort(key=lambda r: order.get(r['source'], 2))   # 사진 모음 사이트 것을 앞으로(같은 곳 안에서는 찾은 차례 그대로)
    FAIL[0] = err[0]
    if out:
        json.dump(out, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
    return out


def main():
    if not A or A[0].startswith('-'):
        print(__doc__); return 1
    q = A[0]; square = '--square' in A; pick = int(A[A.index('--pick') + 1]) if '--pick' in A else 1
    R = search(q, square)
    if not R:
        gone = ''
        if len(A) > 1 and not A[1].startswith('--') and os.path.exists(A[1]):
            os.remove(A[1]); gone = ' 그 자리에 있던 예전 사진은 치웠습니다(다른 상품의 사진이 남아 있지 않게).'
        why = '사진 찾는 곳이 지금 응답하지 않습니다(잠시 뒤 같은 명령을 다시 — 하루 200번, 1분에 20번까지 찾을 수 있습니다).' if FAIL[0] else f'「{q}」로 찾은 사진이 없습니다. 더 흔한 낱말 하나로 바꿔 보세요(예: "camping cookware pot" → "pot").'
        print(why + gone); return 1
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
