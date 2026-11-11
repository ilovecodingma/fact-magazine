# -*- coding: utf-8 -*-
"""내 PC 에서 바로 보기: 사이트를 찍고(조립 예시 포함) 내 컴퓨터 주소(localhost)로 열어 준다. 공개 주소·GitHub·로그인이 필요 없다. 파이썬 기본 기능만 쓴다.
사용: python serve.py                 찍기 → http://127.0.0.1:8000/ 로 열기(멈추려면 Ctrl+C)
      python serve.py --open          열린 주소를 브라우저로도 띄우기
      python serve.py --port 8080     포트 바꾸기(8000 이 쓰이고 있으면 자동으로 다음 번호)
      python serve.py --no-demo       조립 예시는 건너뛰기(더 빨리)
      python serve.py --no-build      이미 찍은 것을 그대로 열기
설명: 로컬에서는 주소가 항상 「/」 에서 시작하도록(base) 따로 찍어 site_local/ 에 둔다(저장소의 docs/ 는 건드리지 않음). 공개용 주소(url)가 없으므로 검색용 정보(canonical·사이트맵)는 만들지 않는다."""
import os, subprocess, sys, threading, webbrowser
import http.server, socketserver
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'site_local')
ARGS = sys.argv[1:]


def build():
    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=OUT)   # 주소 맨 위(/)에서 열리게, 공개 주소는 없음
    env.pop('DEMO', None)
    py = [sys.executable, '-X', 'utf8']
    for name, cmd in (('사이트 찍기', py + [os.path.join(HERE, 'build.py')]), ('조립 예시 찍기', py + [os.path.join(HERE, 'demo.py')])):
        if name.startswith('조립') and '--no-demo' in ARGS:
            continue
        print('▶', name)
        r = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('   ' + '\n   '.join((r.stdout.strip().splitlines() or [''])[-2:]))
        if r.returncode != 0:
            sys.exit(f'{name} 에 실패했습니다:\n' + r.stderr[-400:])


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=OUT, **k)

    def log_message(self, *a):
        pass

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.exists(os.path.join(OUT, '404.html')):   # 없는 주소에는 404 쪽(길 안내)을 보여 준다
            body = open(os.path.join(OUT, '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            super().send_error(code, message, explain)


def main():
    if '--no-build' not in ARGS or not os.path.isdir(OUT):
        build()
    port = int(ARGS[ARGS.index('--port') + 1]) if '--port' in ARGS else 8000
    socketserver.TCPServer.allow_reuse_address = True
    srv = None
    import socket
    for p in range(port, port + 20):
        # 다른 프로그램이 이 포트를 이미 쓰고 있으면(IPv4·IPv6 어느 쪽이든) 다음 번호로 간다 — 엉뚱한 사이트가 열리는 것을 막는다
        busy = False
        for fam, addr in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
            try:
                s_ = socket.socket(fam, socket.SOCK_STREAM); s_.settimeout(0.3)
                if s_.connect_ex((addr, p)) == 0:
                    busy = True
                s_.close()
            except OSError:
                pass
        if busy:
            continue
        try:
            srv = socketserver.ThreadingTCPServer(('127.0.0.1', p), Handler); port = p; break
        except OSError:
            continue
    if not srv:
        sys.exit('쓸 수 있는 포트를 찾지 못했습니다(--port 로 다른 번호를 주세요).')
    url = f'http://127.0.0.1:{port}/'   # localhost 대신 127.0.0.1 — localhost 가 다른 프로그램(IPv6)으로 가는 일을 피한다
    print(f'\n내 PC 에서 열었습니다 → {url}\n(조립 예시: {url}demo/ · 멈추려면 Ctrl+C)')
    if '--open' in ARGS:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n멈췄습니다.')


if __name__ == '__main__':
    main()
