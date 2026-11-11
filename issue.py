# -*- coding: utf-8 -*-
"""잡지 발행: 날짜별 「호」의 인쇄용 PDF 를 만든다(Edge·Chrome 의 인쇄 기능 사용 — 추가 설치 없음).
순서: python build.py → python issue.py → python build.py (PDF 링크가 붙음).
build.py 는 노트가 있는 날짜마다 docs/issue/<날짜>/ 쪽과 print.html 을 만든다. 이 스크립트는 print.html 을 PDF 로 찍어 issues_pdf/<날짜>.pdf 에 둔다(없는 날짜만).
사용: python issue.py            새로 만들 호만
      python issue.py --force    모든 호 다시 만들기"""
import glob, os, shutil, subprocess, sys
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
        sys.exit('docs/issue/ 가 없습니다. 먼저 python build.py 를 돌리세요(site.json 의 parts.issue 가 켜져 있어야 함).')
    os.makedirs(PDF, exist_ok=True)
    br = browser()
    made = 0
    for p in pages:
        d = os.path.basename(os.path.dirname(p))
        out = os.path.join(PDF, d + '.pdf')
        if os.path.exists(out) and not force:
            print('이미 있음:', d); continue
        subprocess.run([br, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + out, 'file:///' + p.replace('\\', '/')],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            print('만듦:', out); made += 1
        else:
            print('실패:', d)
    print(f'PDF {made}개 새로 만듦. 이제 python build.py 를 다시 돌리면 호 쪽에 「인쇄용 PDF」 링크가 붙습니다.')


if __name__ == '__main__':
    main()
