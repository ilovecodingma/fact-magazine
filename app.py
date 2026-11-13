# -*- coding: utf-8 -*-
"""앱(안드로이드): 만든 글 사이트를 앱(APK)으로 감싸고, 사이트 안에 내려받기 화면까지 둔다. 파이썬 기본 기능만 쓴다.
python run.py 앱 환경              빌드에 필요한 것(JDK·안드로이드 SDK·Gradle)을 이 PC 에서 찾아 보여 준다
python run.py 앱 환경 --받기 [--동의]   없는 것을 하네스 폴더(내 사용자 폴더 아래 harness_android)에만 받는다. 안드로이드 SDK 사용 약관에 동의하는 일이 들어 있어 독자가 동의한 뒤(--동의)에만 이어진다
python run.py 앱 만들기            사이트를 빌드해 앱 안에 넣고 → 프로젝트 → 빌드 → 서명한 APK → 내려받기 화면(android_app/out/)
python run.py 앱 상태              만든 앱의 버전·크기와 서명 키 위치
APK 는 「올려 줘」 때 사이트의 /app/ 아래에 같이 올라간다(내려받기 화면 + app.apk).
서명 키(android_app/app.keystore, keystore.properties)는 이력에 올라가지 않고, 읽기 도구로는 열 수 없게 막아 두었으며 세션은 열지 않는다(명령으로 읽는 길은 모두 막을 수 없다). 키를 잃으면 같은 앱의 업데이트를 낼 수 없다."""
import glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, zipfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
HA = os.environ.get('HARNESS_ANDROID') or os.path.join(HOME, 'harness_android')   # 하네스가 받은 도구와 빌드 캐시를 두는 한 폴더(지우면 끝). 환경변수 HARNESS_ANDROID 로 바꿀 수 있다
PROJ = os.path.join(HERE, 'android_template')
APP = os.path.join(HERE, 'android_app')
OUT = os.path.join(APP, 'out')
A = sys.argv[1:]
WIN = os.name == 'nt'
URL_SDK = 'https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip'
URL_GRADLE = 'https://services.gradle.org/distributions/gradle-8.7-bin.zip'
URL_JDK = 'https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse'
PLATFORM, BUILDTOOLS = 'android-35', '35.0.0'


def exe(n, kind):
    return n + ('.exe' if kind == 'exe' and WIN else '.bat' if kind == 'bat' and WIN else '')


# ---------------------------------------------------------------- 환경 찾기
def _roots():
    r = [HA, os.environ.get('ANDROID_HOME') or '', os.environ.get('ANDROID_SDK_ROOT') or '', os.environ.get('JAVA_HOME') or '', os.path.join(HOME, 'tools')]
    r += glob.glob(os.path.join(HOME, '*', 'tools')) + glob.glob(os.path.join(HOME, 'AppData', 'Local', 'Android', 'Sdk')) + glob.glob(os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Eclipse Adoptium', 'jdk-*'))
    r += glob.glob(os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Java', 'jdk*')) + glob.glob(os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Android', '*'))
    return [x for x in r if x and os.path.isdir(x)]


def _walk(root, name, depth=4):
    root = os.path.abspath(root); base = root.count(os.sep)
    for d, ds, fs in os.walk(root):
        if d.count(os.sep) - base >= depth:
            ds[:] = []
        ds[:] = [x for x in ds if x not in ('node_modules', '.git', 'build', 'caches', '.gradle')]
        if name in fs:
            yield os.path.join(d, name)


def find_jdk():
    for root in _roots():
        for p in _walk(root, exe('javac', 'exe')):
            home = os.path.dirname(os.path.dirname(p))
            try:
                v = subprocess.run([p, '-version'], capture_output=True, text=True, errors='replace', timeout=20)
                m = re.search(r'javac (\d+)', (v.stderr or '') + (v.stdout or ''))
                if m and 17 <= int(m.group(1)) <= 21:
                    return home, m.group(1)
            except Exception:
                continue
    return None, None


def find_sdk():
    for root in _roots():
        cands = [root] + [os.path.join(root, x) for x in os.listdir(root)] if os.path.isdir(root) else []
        for c in cands:
            if os.path.isdir(os.path.join(c, 'platforms', PLATFORM)) and os.path.isdir(os.path.join(c, 'build-tools', BUILDTOOLS)):
                return c
    return None


def find_gradle():
    g = shutil.which('gradle')
    if g:
        try:
            v = subprocess.run([g, '--version'], capture_output=True, text=True, errors='replace', timeout=60, shell=WIN).stdout
            m = re.search(r'Gradle (\d+)\.(\d+)', v)
            if m and (int(m.group(1)), int(m.group(2))) >= (8, 7) and int(m.group(1)) < 9:
                return g, f'{m.group(1)}.{m.group(2)}'
        except Exception:
            pass
    for root in _roots():
        for p in _walk(root, exe('gradle', 'bat'), 3):
            if os.path.basename(os.path.dirname(p)) == 'bin' and re.search(r'gradle-8\.', p):
                return p, re.search(r'gradle-(8\.[\d.]+)', p).group(1)
    return None, None


def env():
    jdk, jv = find_jdk(); sdk = find_sdk(); gr, gv = find_gradle()
    return dict(jdk=jdk, jdk_v=jv, sdk=sdk, gradle=gr, gradle_v=gv)


def show_env(e):
    print('━━ 환경 구성 — 안드로이드 빌드에 필요한 것 ━━')
    print(f'  {"✔" if e["jdk"] else "✘"} JDK 17~21   {e["jdk"] and f"{e["jdk_v"]}  ({e["jdk"]})" or "없음"}')
    print(f'  {"✔" if e["sdk"] else "✘"} 안드로이드 SDK(플랫폼 35, 빌드 도구 35.0.0)   {e["sdk"] or "없음"}')
    print(f'  {"✔" if e["gradle"] else "✘"} Gradle 8.x   {e["gradle"] and f"{e["gradle_v"]}  ({e["gradle"]})" or "없음"}')
    return all(e[k] for k in ('jdk', 'sdk', 'gradle'))


# ---------------------------------------------------------------- 받기(하네스 폴더에만)
def fetch(url, dst):
    t0 = time.time(); last = [0]
    req = urllib.request.Request(url, headers={'User-Agent': 'fact-magazine-harness/1'})
    with urllib.request.urlopen(req, timeout=60) as r, open(dst, 'wb') as f:
        total = int(r.headers.get('Content-Length') or 0); got = 0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b); got += len(b)
            if total and got * 10 // total > last[0]:
                last[0] = got * 10 // total; print(f'    {last[0] * 10}% ({got // 1048576}MB)', flush=True)
    print(f'    받았습니다: {os.path.basename(dst)} {os.path.getsize(dst) // 1048576}MB · {time.time() - t0:.0f}초', flush=True)


def unzip(zf, to):
    with zipfile.ZipFile(zf) as z:
        z.extractall(to)


def download(e, agree):
    if not WIN:
        print('✗ 자동으로 받는 것은 윈도우만 됩니다. 맥·리눅스는 JDK 17, 안드로이드 명령줄 도구(sdkmanager), Gradle 8.7 을 직접 갖춘 뒤 다시 하세요.'); return False
    os.makedirs(HA, exist_ok=True); dl = os.path.join(HA, '_zip'); os.makedirs(dl, exist_ok=True)
    print(f'받는 곳은 이 한 폴더뿐입니다: {HA}  (지우면 끝납니다. 시스템에 설치하지 않고 관리자 승인도 필요 없습니다)', flush=True)
    t0 = time.time()
    if not e['jdk']:
        print('▶ JDK 17 (Eclipse Temurin)', flush=True); z = os.path.join(dl, 'jdk17.zip'); fetch(URL_JDK, z); unzip(z, os.path.join(HA, 'jdk17'))
    if not e['gradle']:
        print('▶ Gradle 8.7', flush=True); z = os.path.join(dl, 'gradle.zip'); fetch(URL_GRADLE, z); unzip(z, HA)
    if not e['sdk']:
        sdk = os.path.join(HA, 'sdk'); sm = os.path.join(sdk, 'cmdline-tools', 'latest', 'bin', exe('sdkmanager', 'bat'))
        if not os.path.exists(sm):
            print('▶ 안드로이드 명령줄 도구', flush=True); z = os.path.join(dl, 'cmdline.zip'); fetch(URL_SDK, z)
            tmp = os.path.join(HA, '_cmd'); shutil.rmtree(tmp, ignore_errors=True); unzip(z, tmp)
            os.makedirs(os.path.join(sdk, 'cmdline-tools'), exist_ok=True); shutil.move(os.path.join(tmp, 'cmdline-tools'), os.path.join(sdk, 'cmdline-tools', 'latest')); shutil.rmtree(tmp, ignore_errors=True)
        if not agree:
            print('\n멈춥니다 — 안드로이드 SDK 를 받으려면 사용 약관(https://developer.android.com/studio/terms)에 동의해야 합니다.\n독자가 동의하면 `python run.py 앱 환경 --받기 --동의` 로 이어 갑니다.'); return False
        e2 = env(); jh = e2['jdk'] or find_jdk()[0]
        ev = dict(os.environ, JAVA_HOME=jh or '')
        print('▶ 약관 동의 후 SDK 구성 요소(플랫폼 35, 빌드 도구, platform-tools)', flush=True)
        subprocess.run([sm, f'--sdk_root={sdk}', '--licenses'], input='y\n' * 30, text=True, env=ev, capture_output=True, timeout=300, shell=WIN)
        r = subprocess.run([sm, f'--sdk_root={sdk}', 'platform-tools', f'platforms;{PLATFORM}', f'build-tools;{BUILDTOOLS}'], text=True, env=ev, capture_output=True, errors='replace', timeout=1500, shell=WIN)
        if r.returncode != 0:
            print('✗ SDK 구성 요소를 받지 못했습니다:', (r.stdout + r.stderr)[-300:]); return False
    print(f'✓ 환경을 갖췄습니다 — {time.time() - t0:.0f}초', flush=True)
    return True


def cmd_env():
    e = env(); ok = show_env(e)
    if '--받기' in A and not ok:
        if download(e, '--동의' in A):
            return 0 if show_env(env()) else 1
        return 1
    if not ok:
        print('\n없는 것은 `python run.py 앱 환경 --받기` 로 하네스 폴더(' + HA + ')에만 받습니다(안드로이드 SDK 약관 동의가 필요합니다).')
    return 0 if ok else 1


# ---------------------------------------------------------------- 만들기
def slug_pkg():
    try:
        L = json.load(open(os.path.join(HERE, 'site.local.json'), encoding='utf-8'))
    except Exception:
        L = {}
    s = re.sub(r'[^a-z0-9]+', '', str(L.get('slug') or '').lower()) or 'mysite'
    if not s[0].isalpha():
        s = 'a' + s
    return 'com.harness.' + s[:30], str(L.get('name') or '내 사이트'), str(L.get('accent') or '#2f6b3f')


def build_site(dst):
    r = subprocess.run([sys.executable, '-X', 'utf8', 'build.py'], cwd=HERE, env=dict(os.environ, OUT_DIR=dst, SITE_BASE='/'), capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0 or not os.path.exists(os.path.join(dst, 'index.html')):
        print('✗ 빌드 실패(사이트):', (r.stderr or r.stdout)[-300:]); return False
    print('빌드했습니다(사이트): ' + (r.stdout.strip().splitlines() or [''])[-1].split('->')[0].strip(), flush=True)
    return True


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", "\\'").replace('"', '\\"')


def scaffold(pkg, name, color, vcode, vname):
    first = not os.path.isdir(APP)
    ver = {'@@PACKAGE@@': pkg, '@@PKGDIR@@': pkg.replace('.', os.sep), '@@APPNAME@@': esc(name), '@@COLOR@@': color if re.fullmatch(r'#[0-9a-fA-F]{6}', color) else '#2f6b3f', '@@VERSIONCODE@@': str(vcode), '@@VERSIONNAME@@': vname}
    for root, ds, fs in os.walk(PROJ):
        rel = os.path.relpath(root, PROJ)
        for f in fs:
            src = os.path.join(root, f); out_rel = os.path.join(rel, f) if rel != '.' else f
            for k, v in ver.items():
                out_rel = out_rel.replace(k, v)
            dst = os.path.join(APP, out_rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
            t = open(src, encoding='utf-8').read()
            for k, v in ver.items():
                t = t.replace(k, v)
            open(dst, 'w', encoding='utf-8', newline='\n').write(t)
    return first


def ensure_key(jdk):
    ks = os.path.join(APP, 'app.keystore'); kp = os.path.join(APP, 'keystore.properties')
    if os.path.exists(ks) and os.path.exists(kp):
        return False
    pw = hashlib.sha256(os.urandom(32)).hexdigest()[:24]
    for f in (ks, kp):
        if os.path.exists(f):
            os.remove(f)
    r = subprocess.run([os.path.join(jdk, 'bin', exe('keytool', 'exe')), '-genkeypair', '-keystore', ks, '-alias', 'app', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-storepass', pw, '-keypass', pw, '-dname', 'CN=Harness App'], capture_output=True, text=True, errors='replace', timeout=120)
    if r.returncode != 0:
        print('✗ 서명 키를 만들지 못했습니다:', (r.stdout + r.stderr)[-200:]); sys.exit(1)
    open(kp, 'w', encoding='utf-8').write(f'storeFile=app.keystore\nstorePassword={pw}\nkeyAlias=app\nkeyPassword={pw}\n')
    return True


PAGE = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__NAME__ 앱 받기</title>
<style>body{margin:0;font:16px/1.7 system-ui,"Malgun Gothic",sans-serif;color:#222;background:#fff}main{max-width:560px;margin:0 auto;padding:40px 20px}h1{font-size:26px;margin:0 0 6px}.s{color:#666;margin:0 0 28px}a.b{display:block;text-align:center;background:__COLOR__;color:#fff;text-decoration:none;font-weight:700;padding:16px;border-radius:12px;margin:0 0 28px}ol{padding-left:20px}li{margin:0 0 10px}small{color:#777}</style>
<main><h1>__NAME__</h1><p class="s">안드로이드 휴대폰에 앱으로 설치합니다. 버전 __VNAME__ · __SIZE__</p>
<a class="b" href="app.apk" download>앱 받기</a>
<ol><li>안드로이드 휴대폰에서 이 화면을 연 채로 위의 「앱 받기」를 누릅니다.</li><li>받은 파일을 엽니다.</li><li>「출처를 알 수 없는 앱」 설치를 허용하라는 창이 뜨면 이 브라우저에 한해 허용합니다.</li><li>「설치」를 누르고, 끝나면 「열기」를 누릅니다.</li></ol>
<small>아이폰에서는 설치되지 않습니다. 설치한 앱은 휴대폰의 앱 목록에서 지우면 사라집니다.</small></main></html>
'''


def cmd_make():
    t0 = time.time(); e = env()
    if not show_env(e):
        if '--동의' in A or all(e[k] for k in ('jdk', 'gradle')) is False and False:
            pass
        print('\n환경이 모자랍니다. `python run.py 앱 환경 --받기` (SDK 약관 동의가 필요하면 독자에게 묻고 `--동의`)'); return 1
    pkg, name, color = slug_pkg(); vf = os.path.join(APP, 'version.json'); ver = json.load(open(vf, encoding='utf-8')) if os.path.exists(vf) else {'code': 0}
    vcode = int(ver.get('code', 0)) + 1; vname = f'1.{vcode - 1}'
    tmp = tempfile.mkdtemp(prefix='appsite_')
    try:
        if not build_site(os.path.join(tmp, 'site')):
            return 1
        import deploy
        n = deploy.ascii_names(os.path.join(tmp, 'site'), quiet=True)
        first = scaffold(pkg, name, color, vcode, vname)
        print(f'{"스캐폴딩: 앱 프로젝트를 android_app/ 에 만들었습니다" if first else "앱 프로젝트를 갱신했습니다"}(패키지 {pkg}, 버전 {vname}/{vcode})', flush=True)
        assets = os.path.join(APP, 'app', 'src', 'main', 'assets', 'site'); shutil.rmtree(assets, ignore_errors=True)
        shutil.copytree(os.path.join(tmp, 'site'), assets, ignore=shutil.ignore_patterns('.vercel', '.base', '.nojekyll'))
        files = sum(len(fs) for _, _, fs in os.walk(assets))
        print(f'사이트 파일 {files}개를 앱 안에 넣었습니다' + (f'(한글 이름 {n}개는 영어 이름으로)' if n else ''), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    open(os.path.join(APP, 'local.properties'), 'w', encoding='utf-8').write('sdk.dir=' + e['sdk'].replace('\\', '/') + '\n')
    made = ensure_key(e['jdk'])
    print('서명 키: ' + ('새로 만들었습니다(android_app/app.keystore — 이력에 올라가지 않고 세션은 열지 않습니다. 잃으면 업데이트를 낼 수 없으니 따로 보관하세요)' if made else '기존 키를 씁니다'), flush=True)
    envs = dict(os.environ, JAVA_HOME=e['jdk'], ANDROID_HOME=e['sdk'], ANDROID_SDK_ROOT=e['sdk'], GRADLE_USER_HOME=os.path.join(HA, 'gradle_home'))
    t1 = time.time(); print('빌드하는 중…(처음에는 빌드 도구를 내려받느라 몇 분 걸릴 수 있습니다)', flush=True)
    r = subprocess.run([e['gradle'], '--no-daemon', '--console=plain', '-p', APP, 'assembleRelease'], env=envs, capture_output=True, text=True, errors='replace', timeout=1500, shell=WIN)
    if r.returncode != 0:
        try:
            import cases; cases.mark('app.build')
        except Exception:
            pass
        print('✗ 빌드 실패(앱). 나온 말의 끝:\n' + (r.stdout + r.stderr).strip()[-700:]); return 1
    apk = os.path.join(APP, 'app', 'build', 'outputs', 'apk', 'release', 'app-release.apk')
    if not os.path.exists(apk):
        print('✗ APK 파일이 만들어지지 않았습니다.'); return 1
    os.makedirs(os.path.join(OUT, 'app'), exist_ok=True); shutil.copyfile(apk, os.path.join(OUT, 'app.apk'))
    size = os.path.getsize(apk); sha = hashlib.sha256(open(apk, 'rb').read()).hexdigest()[:16]
    page = PAGE.replace('__NAME__', name.replace('<', '&lt;')).replace('__COLOR__', color if re.fullmatch(r'#[0-9a-fA-F]{6}', color) else '#2f6b3f').replace('__VNAME__', vname).replace('__SIZE__', f'{size / 1048576:.1f}MB')
    open(os.path.join(OUT, 'app', 'index.html'), 'w', encoding='utf-8').write(page)
    json.dump({'code': vcode, 'name': vname, 'package': pkg, 'bytes': size, 'sha256_16': sha, 't': time.strftime('%Y-%m-%d %H:%M')}, open(vf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try:
        d = json.load(open(os.path.join(HERE, '진도.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, '진도.json')) else {'done': [], 'last': ''}
        d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': f'앱: APK {vname}'}); d['last'] = f'앱: APK {vname}'
        json.dump(d, open(os.path.join(HERE, '진도.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except Exception:
        pass
    print(f'✓ 빌드했습니다(앱): APK {size / 1024:.0f}KB · 서명됨 · {time.time() - t1:.0f}초 (전체 {time.time() - t0:.0f}초)')
    print(f'  파일: android_app/out/app.apk · 내려받기 화면: android_app/out/app/index.html')
    print('  인터넷에 올리려면 「올려 줘」 — 사이트의 /app/ 에 내려받기 화면과 APK 가 같이 올라갑니다. 휴대폰 설치는 그 주소를 휴대폰에서 열어 독자가 직접 합니다.')
    return 0


def cmd_state():
    vf = os.path.join(APP, 'version.json')
    if not os.path.exists(vf):
        print('아직 앱을 만들지 않았습니다. python run.py 앱 만들기'); return 0
    v = json.load(open(vf, encoding='utf-8'))
    print(f'앱: {v["package"]} · 버전 {v["name"]}({v["code"]}) · {v["bytes"] // 1024}KB · {v["t"]}\n서명 키: android_app/app.keystore ' + ('있음' if os.path.exists(os.path.join(APP, 'app.keystore')) else '없음'))
    return 0


def main():
    c = A[0] if A else ''
    if c == '환경':
        return cmd_env()
    if c == '만들기':
        return cmd_make()
    if c == '상태':
        return cmd_state()
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main())
