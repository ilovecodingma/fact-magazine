# -*- coding: utf-8 -*-
"""운영 기록: 저자 팀이 한 달 동안 실제로 운영한 기록(가린 판)을 받아 와서, 독자의 세션이 읽고 분석하게 한다. 파이썬 기본 기능만 쓴다.
python run.py 운영기록 받기 [zip 파일|주소]   묶음을 받아 참고/운영기록/ 에 푼다(이미 있으면 다시 받지 않는다, 다시 받으려면 --다시)
python run.py 운영기록 목록                   받은 파일과 크기, 책의 절마다 어느 기록을 보면 되는지
python run.py 운영기록 찾기 <낱말> [낱말 …]    그 낱말이 모두 든 줄을 파일·줄 번호와 함께(날짜는 10-23, 10/23 어느 쪽으로 쳐도 된다)
분석은 세션이 한다 — 지킬 것은 참고/운영기록_읽는법.md 에 있다."""
import io, json, os, re, sys, urllib.request, zipfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, '참고', '운영기록')
URL = os.environ.get('ARCHIVE_URL', 'https://sungprofile.cloud/park/archive/archive.zip')
MAX = 60 * 1024 * 1024
INDEX = os.environ.get('ARCHIVE_INDEX', 'https://sungprofile.cloud/park/archive/index.json')


def _get(u, limit=5 * 1024 * 1024):
    req = urllib.request.Request(u, headers={'User-Agent': 'fact-magazine-harness/1'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(limit)


def _text(h):
    """화면용 글(HTML)을 읽기 좋은 글로: 꾸밈과 스크립트를 걷고 줄만 남긴다."""
    import html as _html
    h = re.sub(r'(?is)<(script|style|head|nav|footer)\b.*?</\1>', '', h)
    h = re.sub(r'(?i)<h([1-4])[^>]*>', lambda m: '\n\n' + '#' * (int(m.group(1)) + 1) + ' ', h)
    h = re.sub(r'(?i)</(p|div|h[1-6]|tr|li|section|article|table|figure|blockquote)>|<br\s*/?>', '\n', h)
    h = re.sub(r'(?i)<li[^>]*>', '- ', h); h = re.sub(r'(?i)</t[dh]>', ' | ', h)
    t = _html.unescape(re.sub(r'<[^>]+>', '', h))
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(x.strip() for x in t.splitlines())).strip()


def flows():
    """책에서 뺀 「실제 흐름」 글들을 받아 흐름_<번호>.md 로 놓고, 제목 목록(흐름_목록.md)을 만든다. 못 받아도 원문 기록은 그대로 쓴다."""
    try:
        F = json.loads(_get(INDEX).decode('utf-8')).get('flows') or []
    except Exception:
        return 0
    n = 0; idx = ['# 실제 흐름 — 제목으로 찾기', '', '상황별로 찾을 때는 이 제목이 가장 좋은 길잡이다. 파일은 같은 폴더의 흐름_<번호>.md', '']
    for f in F[:80]:
        fid = re.sub(r'[^A-Za-z0-9_-]', '', str(f.get('id') or '')); u = str(f.get('url') or '')
        if not fid or not u.startswith('https://sungprofile.cloud/park/archive/'):
            continue   # 보관소 밖 주소는 받지 않는다
        try:
            body = _text(_get(u).decode('utf-8', 'replace'))
        except Exception:
            continue
        open(os.path.join(DIR, f'흐름_{fid}.md'), 'w', encoding='utf-8').write(f'# {f.get("title", "")}\n\n(출처: {u})\n\n{body}\n'); n += 1
        idx.append(f'- 흐름_{fid}.md — {f.get("title", "")}')
    if n:
        open(os.path.join(DIR, '흐름_목록.md'), 'w', encoding='utf-8').write('\n'.join(idx) + '\n')
    return n


def files():
    return sorted(f for f in os.listdir(DIR) if f.endswith('.md')) if os.path.isdir(DIR) else []


def fetch(A):
    again = '--다시' in A; A = [a for a in A if a != '--다시']
    if files() and not again:
        print(f'이미 받아 두었습니다: 참고/운영기록/ 에 {len(files())}개 파일. 다시 받으려면 python run.py 운영기록 받기 --다시'); return 0
    src = A[0] if A else URL
    if os.path.exists(src):
        raw = open(src, 'rb').read()
    else:
        try:
            req = urllib.request.Request(src, headers={'User-Agent': 'fact-magazine-harness/1'})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read(MAX + 1)
        except Exception as e:
            print(f'✗ 지금은 운영 기록을 받지 못했습니다({type(e).__name__}). 주소: {src}\n  학습 사이트(https://sungprofile.cloud/park/)에서 묶음을 직접 내려받았다면: python run.py 운영기록 받기 <받은 zip 파일>'); return 1
    if len(raw) > MAX:
        print('✗ 묶음이 너무 큽니다(60MB 넘음). 받지 않았습니다.'); return 1
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except Exception:
        print('✗ 받은 것이 zip 묶음이 아닙니다. 받지 않았습니다.'); return 1
    os.makedirs(DIR, exist_ok=True); n = 0; size = 0
    for i in z.infolist():
        name = i.filename
        if i.flag_bits & 0x800 == 0:   # 한글 파일 이름이 옛 방식으로 적힌 묶음
            try:
                name = name.encode('cp437').decode('cp949')
            except Exception:
                pass
        base = os.path.basename(name.replace('\\', '/'))
        if i.is_dir() or not base.endswith('.md') or base.startswith('.'):
            continue   # 글 파일(.md)만 푼다. 폴더 구조는 버리고 한 폴더에 놓는다(묶음 밖으로 나가는 경로를 막는다)
        data = z.read(i); size += len(data)
        if size > 200 * 1024 * 1024:
            print('✗ 풀어 보니 너무 큽니다. 멈췄습니다.'); return 1
        open(os.path.join(DIR, base), 'wb').write(data); n += 1
    if not n:
        print('✗ 묶음 안에 글 파일(.md)이 없습니다.'); return 1
    nf = flows() if not os.path.exists(src) else 0
    print(f'✓ 운영 기록을 받았습니다: 참고/운영기록/ 에 {n}개 파일, {size / 1024 / 1024:.1f}MB' + (f' · 실제 흐름 {nf}편(흐름_목록.md 에 제목)' if nf else ''))
    print('  먼저 읽을 것: 참고/운영기록/읽어두기.md · 참고/운영기록/책_절별_원자료_찾기.md · 참고/운영기록_읽는법.md(세션이 지킬 것)')
    print('  이제 이렇게 말해 보세요 — 「10월 23일에 무슨 일이 있었는지 정리해 줘」 「예약이 멈췄던 날을 찾아 줘」 「사람이 가장 많이 한 말이 뭐야」')
    return 0


def listing():
    fs = files()
    if not fs:
        print('아직 받지 않았습니다. python run.py 운영기록 받기'); return 1
    print(f'참고/운영기록/ — {len(fs)}개 파일')
    for f in fs:
        fp = os.path.join(DIR, f); n = sum(1 for _ in open(fp, encoding='utf-8', errors='replace'))
        print(f'  {f:<34} {os.path.getsize(fp) / 1024:>7.0f}KB  {n:>6}줄')
    print('책의 절마다 어느 기록을 보면 되는지는 책_절별_원자료_찾기.md 에 있습니다.')
    return 0


def _forms(w):
    m = re.fullmatch(r'(\d{1,2})[-/.월]\s*(\d{1,2})일?', w)
    if not m:
        return [w.lower()]
    a, b = int(m.group(1)), int(m.group(2))
    return [f'{a:02d}-{b:02d}', f'{a}/{b}', f'{a}월 {b}일', f'{a:02d}/{b:02d}']


def find(words):
    fs = files()
    if not fs:
        print('아직 받지 않았습니다. python run.py 운영기록 받기'); return 1
    if not words:
        print('사용: python run.py 운영기록 찾기 <낱말> [낱말 …]'); return 1
    W = [_forms(w) for w in words]; hits = []; per = {}
    for f in fs:
        for no, ln in enumerate(open(os.path.join(DIR, f), encoding='utf-8', errors='replace'), 1):
            low = ln.lower()
            if all(any(x in low for x in forms) for forms in W):
                hits.append((f, no, ln.strip())); per[f] = per.get(f, 0) + 1
    print(f'「{" ".join(words)}」 — {len(hits)}줄, 파일 {len(per)}개')
    for f, c in sorted(per.items(), key=lambda x: -x[1])[:12]:
        print(f'  {f}: {c}줄')
    for f, no, ln in hits[:40]:
        print(f'{f}:{no}: {ln[:160]}')
    if len(hits) > 40:
        print(f'… {len(hits) - 40}줄 더 있습니다. 낱말을 더 주거나 파일을 열어 그 둘레를 읽습니다.')
    return 0


def main():
    A = sys.argv[1:]
    c = A[0] if A else '목록'
    if c == '받기':
        return fetch(A[1:])
    if c == '찾기':
        return find(A[1:])
    return listing()


if __name__ == '__main__':
    sys.exit(main())
