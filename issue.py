# -*- coding: utf-8 -*-
"""잡지 발행: 날짜별 「호」의 인쇄용 PDF 를 만든다(Edge·Chrome 의 인쇄 기능 사용 — 추가 설치 없음).
순서: python build.py → python issue.py → python build.py (PDF 링크가 붙음).
build.py 는 노트가 있는 날짜마다 docs/issue/<날짜>/ 쪽과 print.html 을 만든다. 이 스크립트는 print.html 을 PDF 로 찍어 issues_pdf/<날짜>.pdf 에 둔다(없는 날짜만).
사용: python issue.py            새로 만들 호만
      python issue.py --force    모든 호 다시 만들기"""
import glob, json, os, shutil, subprocess, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, 'docs')
PDF = os.path.join(HERE, 'issues_pdf')


def browser():
    cands = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', shutil.which('google-chrome') or '', shutil.which('chromium') or '',
             r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
             r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
             '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    br = next((c for c in cands if c and os.path.exists(c)), None)
    if not br:
        sys.exit('Edge 또는 Chrome 을 찾지 못했습니다. 환경변수 BROWSER 에 실행 파일 경로를 주세요.')
    return br


def main():
    force = '--force' in sys.argv
    pages = sorted(glob.glob(os.path.join(DOCS, 'issue', '*', 'print.html')))
    if not pages:
        sys.exit('호 쪽(docs/issue/<날짜>/print.html)이 없습니다. 원인 두 가지: ① 먼저 python build.py 를 돌려야 함 ② 확인 노트(notes/)가 0건이면 호가 없음 — 노트를 한 건 쓴 뒤 다시. (site.json 의 parts.issue 도 켜져 있어야 함)')
    os.makedirs(PDF, exist_ok=True)
    br = browser()
    made = 0
    for p in pages:
        d = os.path.basename(os.path.dirname(p))
        out = os.path.join(PDF, d + '.pdf')
        import hashlib   # 그날 호의 내용이 바뀌었으면(노트가 늘었으면) PDF 를 다시 만든다
        st_p = os.path.join(HERE, 'data', 'issue_state.json')
        st = json.load(open(st_p, encoding='utf-8')) if os.path.exists(st_p) else {}
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        if os.path.exists(out) and not force and st.get(d) == h:
            print('이미 있음(내용 그대로):', d); continue
        subprocess.run([br, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + out, 'file:///' + p.replace('\\', '/')],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            st[d] = h; os.makedirs(os.path.dirname(st_p), exist_ok=True); json.dump(st, open(st_p, 'w', encoding='utf-8'), indent=1)
            print('만듦:', out); made += 1
        else:
            print('실패:', d)
    print(f'PDF {made}개 새로 만듦. 이제 python build.py 를 다시 돌리면 호 쪽에 「인쇄용 PDF」 링크가 붙습니다.')


if __name__ == '__main__':
    main()
