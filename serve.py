# -*- coding: utf-8 -*-
"""내 PC 에서 바로 보기: 사이트를 찍고(조립 예시 포함) 내 컴퓨터 주소(localhost)로 열어 준다. 공개 주소·GitHub·로그인이 필요 없다. 파이썬 기본 기능만 쓴다.
사용: python serve.py                 찍기 → http://127.0.0.1:8000/ 로 열기. 서버를 뒤에 떼어 띄우고 바로 돌아온다(이미 떠 있으면 그 주소 그대로)
      python serve.py --stop          뒤에 떠 있는 서버 끄기
      python serve.py --fg            이 창에서 붙잡고 돌리기(멈추려면 Ctrl+C)
      python serve.py --open          열린 주소를 브라우저로도 띄우기
      python serve.py --port 8080     포트 바꾸기(8000 이 쓰이고 있으면 자동으로 다음 번호)
      python serve.py --no-demo       조립 예시는 건너뛰기(더 빨리)
      python serve.py --no-build      이미 찍은 것을 그대로 열기
설명: 로컬에서는 주소가 항상 「/」 에서 시작하도록(base) 따로 찍어 site_local/ 에 둔다(저장소의 docs/ 는 건드리지 않음). 공개용 주소(url)가 없으므로 검색용 정보(canonical·사이트맵)는 만들지 않는다."""
import os, subprocess, sys, threading, webbrowser
import http.server, socketserver
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)   # 주소 줄이 바로 보이게(실제 포트를 읽을 수 있게)
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

    preview_id = ''

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header('X-Preview', self.preview_id)   # 이 폴더가 띄운 서버인지 가리는 표시
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.exists(os.path.join(OUT, '404.html')):   # 없는 주소에는 404 쪽(길 안내)을 보여 준다
            body = open(os.path.join(OUT, '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            super().send_error(code, message, explain)


STATE = os.path.join(HERE, 'logs', '미리보기.json')   # 떼어 띄운 서버의 번호·포트(logs/ 는 git 에 올라가지 않는다)


def _up(port):
    import socket
    for fam, addr in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):   # 다른 프로그램이 IPv4·IPv6 어느 쪽으로든 쓰고 있으면 쓰이는 것으로 본다
        try:
            s_ = socket.socket(fam, socket.SOCK_STREAM); s_.settimeout(0.3)
            hit = s_.connect_ex((addr, port)) == 0; s_.close()
            if hit:
                return True
        except OSError:
            pass
    return False


def _state():
    try:
        import json
        return json.load(open(STATE, encoding='utf-8'))
    except Exception:
        return {}


def _mine(st):
    """적어 둔 포트에서 이 폴더의 미리 보기 서버가 답하는지(다른 프로그램이 그 포트를 쓰는 것과 가린다)."""
    if not st.get('port'):
        return False
    try:
        import urllib.request
        r = urllib.request.urlopen(f'http://127.0.0.1:{st["port"]}/', timeout=2)
        return r.headers.get('X-Preview') == str(st.get('id'))
    except Exception:
        return False


def stop():
    st = _state()
    if _mine(st):
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(st['pid']), '/F'], capture_output=True)
            else:
                os.kill(st['pid'], 15)
        except Exception:
            pass
        print('미리 보기 서버를 껐습니다.')
    else:
        print('켜져 있는 미리 보기 서버가 없습니다.')
    try:
        os.remove(STATE)
    except OSError:
        pass


def background(port):
    """서버를 떼어 띄우고 바로 돌아온다 — 부른 쪽(세션)이 서버를 붙잡고 기다리지 않게."""
    import json, time
    st = _state()
    if _mine(st):   # 이미 떠 있으면 그대로 쓴다(방금 다시 찍은 것이 그 주소에 바로 보인다)
        return st['port'], True
    for p in range(port, port + 20):
        if not _up(p):
            port = p; break
    else:
        sys.exit('쓸 수 있는 포트를 찾지 못했습니다(--port 로 다른 번호를 주세요).')
    pid_ = f'{os.getpid()}-{int(time.time())}'
    cmd = [sys.executable, '-X', 'utf8', os.path.abspath(__file__), '--fg', '--no-build', '--port', str(port), '--id', pid_]
    kw = dict(cwd=HERE, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    if os.name == 'nt':
        flags = 0x08000000 | 0x00000200   # 창 없이 · 새 프로세스 묶음
        try:
            proc = subprocess.Popen(cmd, creationflags=flags | 0x01000000, **kw)   # 부른 쪽이 끝나도 같이 꺼지지 않게
        except OSError:
            proc = subprocess.Popen(cmd, creationflags=flags, **kw)
    else:
        proc = subprocess.Popen(cmd, start_new_session=True, **kw)
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump({'pid': proc.pid, 'port': port, 'id': pid_}, open(STATE, 'w', encoding='utf-8'))
    t0 = time.time()
    while time.time() - t0 < 15:
        if _mine(_state()):
            return port, False
        time.sleep(0.3)
    sys.exit('미리 보기 서버가 15초 안에 켜지지 않았습니다. python serve.py --fg 로 직접 켜서 오류를 확인하세요.')


def main():
    if '--help' in ARGS or '-h' in ARGS:
        print(__doc__); return
    if '--stop' in ARGS or '끄기' in ARGS:
        return stop()
    if '--no-build' not in ARGS or not os.path.isdir(OUT):
        build()
    port = int(ARGS[ARGS.index('--port') + 1]) if '--port' in ARGS else 8000
    if '--fg' not in ARGS:
        port, reused = background(port)
        url = f'http://127.0.0.1:{port}/'
        print(f'\n내 PC 에서 열었습니다 → {url}' + (' (켜져 있던 서버에 새로 찍은 것이 보입니다)' if reused else '') + '\n(' + ('' if '--no-demo' in ARGS else f'조립 예시: {url}demo/ · ') + '서버는 뒤에서 계속 돕니다. 끄기: python serve.py --stop)')
        if '--open' in ARGS and os.environ.get('HARNESS_NO_OPEN') != '1':   # HARNESS_NO_OPEN=1 이면 창을 띄우지 않는다(시험·자동 실행 때 사용자의 화면이 바뀌지 않게)
            webbrowser.open(url)
        return
    Handler.preview_id = ARGS[ARGS.index('--id') + 1] if '--id' in ARGS else ''
    socketserver.TCPServer.allow_reuse_address = True
    srv = None
    for p in range(port, port + 20):
        if _up(p):   # 다른 프로그램이 이 포트를 이미 쓰고 있으면 다음 번호로 간다 — 엉뚱한 사이트가 열리는 것을 막는다
            continue
        try:
            srv = socketserver.ThreadingTCPServer(('127.0.0.1', p), Handler); port = p; break
        except OSError:
            continue
    if not srv:
        sys.exit('쓸 수 있는 포트를 찾지 못했습니다(--port 로 다른 번호를 주세요).')
    url = f'http://127.0.0.1:{port}/'   # localhost 대신 127.0.0.1 — localhost 가 다른 프로그램(IPv6)으로 가는 일을 피한다
    print(f'\n내 PC 에서 열었습니다 → {url}\n(멈추려면 Ctrl+C)')
    if '--open' in ARGS and os.environ.get('HARNESS_NO_OPEN') != '1':
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n멈췄습니다.')


if __name__ == '__main__':
    main()
