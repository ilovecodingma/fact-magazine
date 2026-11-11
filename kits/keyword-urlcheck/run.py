# -*- coding: utf-8 -*-
"""하네스 8: 글 주소 목록 → 열리는지(상태 번호)·검색에서 막혀 있지 않은지(noindex) 확인. 파이썬 기본 기능만.
사용: python -X utf8 run.py [주소.txt] [결과.md]
주소마다 1초 쉰다. robots.txt 도 함께 읽어 막힌 주소인지 본다."""
import sys, re, time, urllib.request, urllib.error, urllib.parse, urllib.robotparser

in_file = sys.argv[1] if len(sys.argv) > 1 else '주소.txt'
out_file = sys.argv[2] if len(sys.argv) > 2 else '결과.md'
UA = 'Mozilla/5.0 (address check study)'
urls = [u.strip() for u in open(in_file, encoding='utf-8') if u.strip() and not u.startswith('#')]
robots = {}


def allowed(url):
    p = urllib.parse.urlparse(url)
    root = '%s://%s' % (p.scheme, p.netloc)
    if root not in robots:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(root + '/robots.txt')
        try:
            rp.read()
        except Exception:
            rp = None
        robots[root] = rp
    return True if robots[root] is None else robots[root].can_fetch('Googlebot', url)


rows = []
for u in urls:
    code, noindex, note = '?', '?', ''
    try:
        req = urllib.request.Request(urllib.parse.quote(u, safe=':/?&=%#'), headers={'User-Agent': UA})   # 한글 주소도 열 수 있게 인코딩
        with urllib.request.urlopen(req, timeout=15) as r:
            code = r.status
            html = r.read(200000).decode('utf-8', 'replace')
            meta = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*>', html, re.I)
            hdr = r.headers.get('X-Robots-Tag', '')
            noindex = 'noindex' if ('noindex' in (meta.group(0).lower() if meta else '') or 'noindex' in hdr.lower()) else '아님'
    except urllib.error.HTTPError as e:
        code, noindex = e.code, '-'
    except Exception as e:
        note = str(e)[:40]
    rows.append((u, code, noindex, '허용' if allowed(u) else 'robots 가 막음', note))
    time.sleep(1)
ok = sum(1 for r in rows if r[1] == 200 and r[2] == '아님' and r[3] == '허용')
lines = ['# 주소 점검\n', '| 주소 | 상태 | noindex | robots | 비고 |', '|---|---|---|---|---|']
lines += ['| %s | %s | %s | %s | %s |' % r for r in rows]
lines.append('\n통과 %d / %d (상태 200 · noindex 아님 · robots 허용)' % (ok, len(rows)))
open(out_file, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('통과 %d / %d → %s' % (ok, len(rows), out_file))
