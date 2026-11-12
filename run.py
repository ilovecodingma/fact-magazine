# -*- coding: utf-8 -*-
"""하나의 진입점: 트리거(Claude Code 명령)가 부르는 일을 같은 이름으로 직접 돌릴 수 있다. 파이썬 기본 기능만 쓴다.
사용: python run.py 시작                     환경 점검 + 키트 전부 점검표
      python run.py 키트 계산기               그 키트 실습(꼭 알아야 할 것 → 보이는 브라우저에서 스스로 시험 → 바꿔 보기 제안)
      python run.py 키트 전부                 키트를 차례로(시험이 적힌 키트)
      python run.py 섞기 계산기 용어 게임      고른 키트만 켜고 찍어 메뉴를 하나씩 눌러 보기(한글 이름 가능, 조립 예시 둘을 합칠 때는 섞기 도구함+동네정보)
      python run.py 조립 도구함               조립 예시 하나를 찍어 메뉴를 하나씩 눌러 보기(목록은 python run.py 조립)
      python run.py 사이클                    하루 한 바퀴(올리기·메일 빼고)를 단계별로 돌리기
      python run.py 알기 계산기 5             꼭 알아야 할 것 top-k   (python run.py 알기 하네스)
      python run.py 점검                      doctor
      python run.py 예제정리 [--yes]          주제를 바꿀 때 notes/ 의 예제 노트를 예제/ 로 옮김(독자에게 먼저 묻는다)
      python run.py 올리기전                  구문 검사 + 장·키트·조립·사이클 명령을 한 번씩 실제로 돌려 보기(올리기 전 필수)
      python run.py 진도 [보기|기록 글]        어디까지 했는지
      python run.py 장 1                      장 진행 파일 경로(코스/1장.md)
      python run.py 묶음 [이름]               기능 지도의 여덟 묶음(이름 없으면 목록). 이름을 주면 그 묶음 키트를 켜서 붙이고 하나씩 시험
      python run.py 켜기 계산기 [용어 …]       키트를 켜고 다시 찍어 메뉴·쪽에 생겼는지 한 줄로 확인(끄기 도 같은 모양)
      python run.py 지금                      내 사이트에 지금 켜져 있는 것 목록과 메뉴
      python run.py 전부 [--yes]              묻지 않고 여덟 묶음을 끝까지(묻는 자리는 기본값: 켜 둔다)
      python run.py 다듬기 [번호|다음] [--안 A|B] [--shots 폴더]   투박한 출발 모습을 걸음마다 고품질로(안 없이 부르면 안 A·B 미리보기만, --안 을 주면 적용하고 전·후 화면과 점수)
      python run.py 되돌리기 <번호>            그 다듬기 걸음을 끈다(출발 모습 쪽으로)
      python run.py 만듦새 [--shots 폴더]      첫 화면·글 쪽·휴대폰을 재서 점수(빈 영역·그림·최소 글자·대비·넘침·정보량)
      python run.py 비교 [종류]                참고 사이트 화면과 내 첫 화면을 나란히 한 장으로(인터넷 필요)
      python run.py 생각 · 정리 "<독자의 말>" [--한줄 …] [--정함 a;b] [--미정 …] [--미룸 …]   독자의 생각을 정리해 생각.md 에 남기기
      python run.py 열기                      받자마자 내 PC 에서 열고 10분 한 바퀴(방문자의 길·운영자의 하루) · 변환 <종류> · 쉬는시간
      python run.py 나누기 [레퍼런스 [조각 번호] | 새로 "<사이트>"]   레퍼런스 사이트를 기능 조각으로 나눠 보기
      python run.py 조각 [레퍼런스 번호 켜기|끄기]   나누기에서 본 조각 하나만 내 사이트에 켰다 끄기 · 분류 ["이름=낱말,낱말" …|기본]   독자가 말한 분류를 분류 탭으로 · 참고 미디엄   그 사이트가 무엇으로 버는지
      python run.py 운영                      게시판·장터·순위 사이트에서 오늘 사람이 볼 것(승인 대기·주문 문의·별 요약, 읽기만) — 사이클 끝에도 나옴
      python run.py 손잡이 [이름 [값]]         플랫폼의 핵심 장치를 돌려 보기(본문폭·본문글자·줄높이·목록열·읽는시간·저장·듣기)
      python run.py 본 [글|게시판|장터|순위]    유명 플랫폼을 본뜬 출발점을 한 번에 띄우기(튜토리얼의 첫 화면)
      python run.py 준비 [--보기만]            필요한 프로그램(git·Node.js·브라우저·ffmpeg) 점검, 빠진 것은 묻지 않고 winget·brew·apt 로 바로 깖
      python run.py 데이터 현황|백업|목록|복구 [파일] --예|주문표|발송목록   운영 자료를 한 장으로 보고, 통째로 백업·복구, 주문을 표로
      python run.py 메일 [--send] [--to 주소]   소식 메일 미리보기(기본) · 사람이 「보내」 한 뒤에만 --send
      python run.py 운영기록 받기|목록|찾기 <낱말>   저자 팀의 한 달 운영 기록(가린 판)을 받아 참고/운영기록/ 에 놓고 찾기 — 분석은 세션이(참고/운영기록_읽는법.md)
      python run.py 토큰 [끄기]                학습 사이트(sungprofile.cloud/park/start/)에 넣을 토큰을 받는다 — 받아 두면 관문이 열릴 때 진도(단계 이름)만 알림. 선택
      python run.py 올려 가게                  켜져 있는 가게(화면+백엔드)에 바깥 주소를 붙인다 — 로그인 없이, 이 PC 가 켜져 있는 동안 열림(닫기: 가게 공유 끄기)
      python run.py 올려 [상태]                지금 사이트를 찍어 남에게 보여 줄 주소를 받는다(Vercel — 로그인 없이도 60분짜리 임시 주소가 바로 나오고, 로그인돼 있으면 사라지지 않는 주소)
      python run.py 가게 품절 <번호|이름> [풀기] · 가게 홍보 <번호|이름>   품절이면 화면에 표시되고 담기지 않음 · 상품 하나로 홍보 글·문구·카드 그림(올리지 않음)
      python run.py 가게 켜기|끄기|상태|시험|상품다시 · 붙여 <기능> · 떼 <기능> · 기능   종합 쇼핑몰을 본뜬 틀(화면 Next.js + 백엔드 파이썬 + 앱, 결제 없음): 켜고, 기능 묶음을 붙였다 뗀다
      python run.py 자동 맛보기 [--뒤 분] | 방송 | 예약 [시각|끄기|상태] [--예]   사람 없이 하루 한 바퀴와 알릴 글·그림·영상까지 → 넘김/자리비운동안.md · 방송 화면 · 날마다 저절로
      python run.py 바꿔 "<독자가 한 말>" → (세션이 무엇이든 고침) → 바꿨다   말 한 줄로 수정하고 자동 확인(구문·찍기) · 되돌리기 [처음|목록|걸음 번호]   무엇을 바꿔도 한 줄로 돌아감
      python run.py 레퍼런스 [바꾸기 <이름> | 값 키=값 …]   레퍼런스(히트한 플랫폼, 지금은 미디엄)를 잰 값과 우리 사이트의 지금 값 차이표
      python run.py 맺음                      걸음·장을 맺을 때 「오늘 배운 것 세 줄 + 헷갈려 한 것 + 다음에 할 것」 초안(내_서비스.md·고른 것에서)
      python run.py 방식 프런트|백엔드|바꾸기   화면을 만드는 방식·방문자가 남기는 것을 받는 방식(서비스의 말로 묻고, 세션은 경우만 말하고, 독자가 고른다)
      python run.py 내서비스 [칸 "<칸>" "<정리한 말>"]   상담하며 정리한 「내 서비스 한 장」(내_서비스.md)의 어느 칸이 채워졌는지 보기·적기
      python run.py 고름 <걸음> <고른 것> [까닭]   독자가 고른 것을 기록(1·2장은 독자가 고르기 전에는 적용하지 않는다) · 고른것 [--shots] · 미룬것
      python run.py 서버 [끄기|상태|다시|로그|암호]   도커로 백엔드(사이트 제공+API+PostgreSQL) 켜기 · 도커 [열기|확인|설치]   PC 를 보고 추천 → 독자가 고르면 공식 사이트로 · 자료 <모음> · 실험 좋아요|롤백|색인|제약|백업 · 내놓기 [24시간|클라우드]
      python run.py 참고 [종류]               참고 사이트(실제 사이트와 「이렇게 번다」). --shots 폴더 면 그 사이트 화면을 headless 로 찍어 둔다
      python run.py 기획서                     기획서 한 장(기획서.md, 없으면 양식)
      python run.py 서비스 <종류> [단계 1~9]   서비스 하나를 끝까지: ㉠참고 ㉡기획서 ㉢기능 붙이기 ㉣내용 채우기 ㉤돈 자리 ㉥필수 쪽 ㉦겉모습 ㉧휴대폰 ㉨올릴 준비(종류: 정보 매거진·도구 모음·요리법 모음·가계부 앱)
      python run.py 독자 [설정 키=값 …]        독자.json(수업 눈높이) 보기·고치기      python run.py 복습   진도·헷갈린 것에서 물음 3개
      python run.py 혼동 <키트> <적을 말>       헷갈려 한 것을 진도에 적기
옵션: --headless(창 없이) --slow 초(단계 간격) --shots 폴더(단계마다 화면을 png 로 저장, 사이클은 단계 결과 쪽) · 보이는 창 위치는 환경변수 SELFTEST_POS=2000,100
설명: 이 파일은 얇은 껍데기다 — 실제 일은 doctor.py·selftest.py·know.py·mix.py·demo.py·run_daily.py 가 한다. 올리기·메일 발송·로그인은 하지 않는다."""
import glob, json, os, re, subprocess, sys, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
A = sys.argv[1:]
PY = [sys.executable, '-X', 'utf8']
FLAGS = [a for a in A if a in ('--headless',)] + (['--slow', A[A.index('--slow') + 1]] if '--slow' in A else []) + (['--shots', os.path.abspath(A[A.index('--shots') + 1])] if '--shots' in A and len(A) > A.index('--shots') + 1 else [])
POS = [a for i, a in enumerate(A) if not a.startswith('--') and (i == 0 or A[i - 1] not in ('--slow', '--shots', '--이름', '--소개', '--까닭', '--고른이', '--안', '--한줄', '--정함', '--미정', '--미룸'))]
SHOTS = os.path.abspath(A[A.index('--shots') + 1]) if '--shots' in A and len(A) > A.index('--shots') + 1 else None
PROG = os.path.join(HERE, '진도.json')


def sh(args, check=False):
    return subprocess.run(PY + args, cwd=HERE).returncode


def prog_load():
    return json.load(open(PROG, encoding='utf-8')) if os.path.exists(PROG) else {'done': [], 'last': ''}


def prog_add(text):
    d = prog_load(); d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': text}); d['last'] = text
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def kits():
    out = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json'))):
        k = json.load(open(p, encoding='utf-8')); out[k['name']] = k
    return out


LAST_OUT = {}   # 사이클 단계별 출력(점검 결과를 화면으로 찍는 데 쓴다)


def text_png(br, title, blocks, out):
    """글을 읽기 좋은 쪽으로 그려 찍는다(폴더 목록이나 파일 경로가 화면에 나오지 않게)."""
    import html as H, tempfile
    body = ''.join(f'<h2>{H.escape(h)}</h2><pre>{H.escape(t)}</pre>' for h, t in blocks)
    doc = ('<!doctype html><meta charset="utf-8"><title>' + H.escape(title) + '</title><style>body{margin:0;background:#f6f4ef;font:17px/1.7 "Malgun Gothic",system-ui,sans-serif;color:#111}'
           'main{max-width:860px;margin:0 auto;padding:28px 24px}h1{font-size:26px;border-bottom:3px double #111;padding-bottom:10px}h2{font-size:15px;color:#b5532a;margin:22px 0 6px}'
           'pre{white-space:pre-wrap;word-break:break-word;font:inherit;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px 16px;margin:0}</style><main><h1>' + H.escape(title) + '</h1>' + body + '</main>')
    f = os.path.join(tempfile.mkdtemp(), 't.html'); open(f, 'w', encoding='utf-8').write(doc)
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1100,900', f'--screenshot={out}', 'file:///' + f.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)


def cycle_shot(i, title, script):
    """사이클 단계가 끝난 뒤 그 결과를 headless 로 찍는다: 1 첫 화면·호·새 노트, 2 알림 문구·블로그 글(읽기 좋게 그린 쪽), 3 카드 그림, 4 점검 결과(상태 쪽이 켜져 있으면 그 쪽도)."""
    import selftest as T, shutil
    docs = os.path.join(HERE, 'docs')
    br = T.find_browser()
    if not br:
        print('  (브라우저가 없어 화면 저장을 건너뜁니다)'); return
    os.makedirs(SHOTS, exist_ok=True)
    pages = []
    if i == 1:
        pages = [p for p in ('index.html', 'issue/index.html') if os.path.exists(os.path.join(docs, p))]
        nd = os.path.join(docs, 'n')   # 확인 노트 쪽은 n/<노트 id>/
        if os.path.isdir(nd):
            pages += ['n/' + n + '/index.html' for n in sorted(os.listdir(nd), reverse=True)[:1] if os.path.exists(os.path.join(nd, n, 'index.html'))]
    elif i == 4 and os.path.exists(os.path.join(docs, 'status', 'index.html')):
        pages = ['status/index.html']
    if pages:
        srv, port = T.start_server(docs)
        try:
            for n, p in enumerate(pages, 1):
                out = os.path.join(SHOTS, f'사이클_{i}_{n}_{p.replace("/", "_").replace(".html", "")}.png')
                subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1100,900', f'--screenshot={out}', f'http://127.0.0.1:{port}/{p}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
                print('  화면 저장:', os.path.basename(out), flush=True)
        finally:
            srv.shutdown()
    if i == 2:
        d = os.path.join(HERE, 'promo_out')
        subs = sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)))[:1] if os.path.isdir(d) else []
        for sdir in subs:
            blocks = []
            for f in ('알림_짧게.txt', '알림_보통.txt', '블로그글.md'):
                fp = os.path.join(d, sdir, f)
                if os.path.exists(fp):
                    t = open(fp, encoding='utf-8').read().strip()
                    blocks.append((f.replace('_', ' ').rsplit('.', 1)[0], chr(10).join(t.splitlines()[:14]) + (chr(10) + '…' if len(t.splitlines()) > 14 else '')))
            out = os.path.join(SHOTS, f'사이클_2_1_promo_{sdir}.png'); text_png(br, '알림 문구와 블로그 글 — ' + sdir, blocks, out); print('  화면 저장:', os.path.basename(out), flush=True)
    if i == 3:
        d = os.path.join(HERE, 'cards')
        for n, f in enumerate([f for f in sorted(os.listdir(d)) if f.endswith('.png')][:2] if os.path.isdir(d) else [], 1):
            shutil.copy(os.path.join(d, f), os.path.join(SHOTS, f'사이클_3_{n}_{f}')); print('  그림 저장:', f, flush=True)
    if i == 4 and LAST_OUT.get(4):
        out = os.path.join(SHOTS, '사이클_4_점검결과.png'); text_png(br, '점검(audit) 결과', [('python audit.py', LAST_OUT[4][-2500:])], out); print('  화면 저장:', os.path.basename(out), flush=True)


def info_on():
    """site.json(+site.local.json)에서 뉴스(info) 부품이 켜져 있나."""
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    return bool((S.get('parts') or {}).get('info', True))



GFILE = os.path.join(HERE, 'groups.json')
READER = os.path.join(HERE, '독자.json')


def gload():
    return json.load(open(GFILE, encoding='utf-8'))


def kit_json(name):
    p = os.path.join(HERE, 'kits', name, 'kit.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def own_part(kj):
    """이 키트를 켜고 끌 때 바꾸는 부품(site.json parts 의 키): 키트 이름이 부품이면 그것, 아니면 kit.json parts 의 첫 번째."""
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    if kj['name'] in S['parts']:
        return kj['name']
    return (kj.get('parts') or [None])[0]


def set_parts(names, on):
    """독자 폴더의 선택은 site.local.json(git 추적 제외)에만 쓴다 — 추적되는 site.json 은 건드리지 않는다. site.local.json 에 parts 가 없으면 site.json 의 parts 를 복사해 시작한다."""
    S0 = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    fp = os.path.join(HERE, 'site.local.json')
    d = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    if 'parts' not in d:
        d['parts'] = dict(S0.get('parts') or {})
    for n in names:
        d['parts'][n] = on
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def eff_parts():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    parts = dict(S.get('parts') or {})
    if os.path.exists(lp):
        parts.update(json.load(open(lp, encoding='utf-8')).get('parts') or {})
    return parts


def rebuild_local():
    out = os.path.join(HERE, 'site_local')
    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=out)
    r = subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print('✗ 사이트 찍기에 실패했습니다(이 오류를 그대로 알려 주세요):', (r.stderr or '')[-500:], flush=True)
    return out, (r.stdout.strip().splitlines() or [''])[-1], r.returncode


def menu_of(out):
    """site_local 첫 화면의 메뉴 칸(이름)과 모든 링크 주소."""
    import re as _re
    ip = os.path.join(out, 'index.html')
    h = open(ip, encoding='utf-8').read() if os.path.exists(ip) else ''
    nav = _re.search(r'<nav class="menu">(.*?)</nav>', h, _re.S)
    labels = _re.findall(r'<a href="[^"]*">([^<]+)</a>', nav.group(1)) if nav else []
    return labels, set(_re.findall(r'href="(/[^"]*)"', h))


def find_kit(word):
    sys.path.insert(0, HERE); import selftest as T
    k = T.resolve(word)
    return kit_json(k['name']) if k else None


def toggle(words, on):
    G = gload()['paths']
    if not words:
        print('사용: python run.py ' + ('켜기' if on else '끄기') + ' 계산기 [용어 …]'); return 1
    rc = 0
    for w in words:
        kj = find_kit(w)
        if not kj:
            print(f'「{w}」 키트를 찾지 못했습니다(python run.py 키트 로 목록)'); rc = 1; continue
        op = own_part(kj)
        if not op:
            print(f'「{kj["title"]}」 은(는) 사이트 화면에 붙는 기능이 아니라 돌려서 파일을 만드는 도구라 켜고 끌 것이 없습니다. python run.py 키트 {kj["name"]} 로 돌려 보세요.'); continue
        before_labels, _ = menu_of(os.path.join(HERE, 'site_local')) if os.path.isdir(os.path.join(HERE, 'site_local')) else ([], set())
        if SHOTS:
            ob, lb_, rb_ = rebuild_local(); _shot_site(ob, [''], f'{"켜기" if on else "끄기"}_{kj["name"]}_1전')
        set_parts(list(kj.get('parts') or [op]) if on else [op], on)
        out, last, rcb = rebuild_local()
        if rcb != 0:
            print(f'✗ 다시 찍기에 실패했습니다: {last}'); rc = 1; continue
        labels, links = menu_of(out)
        if SHOTS:
            _shot_site(out, [''], f'{"켜기" if on else "끄기"}_{kj["name"]}_2후')
        path = G.get(kj['name'])
        present = ('/' + path in links) if path else None
        name = kj.get('title', kj['name'])
        if path is None:
            print(f'{"✓" if on else "✓"} 「{name}」 {"켰습니다" if on else "껐습니다"}(화면에 따로 쪽이 생기지 않는 기능입니다). 지금 메뉴: {" · ".join(labels)}')
        elif on:
            print(('✓' if present else '△') + f' 「{name}」 켰습니다 — ' + ('쪽 /' + path + ' 이 사이트 링크에 생겼습니다' if present else '링크가 첫 화면에 보이지 않습니다(자료가 비어 있거나 메뉴 밖일 수 있음)') + f'. 지금 메뉴: {" · ".join(labels)}')
        else:
            print(('✓' if not present else '△') + f' 「{name}」 껐습니다 — ' + ('메뉴·링크에서 빠졌습니다' if not present else '아직 링크가 남아 있습니다(다른 기능이 같은 쪽을 쓸 수 있음)') + f'. 지금 메뉴: {" · ".join(labels)}')
        prog_group_toggle(kj['name'], on)
    return rc


def prog_group_toggle(kit, on):
    d = prog_load(); d.setdefault('toggles', {})[kit] = '켬' if on else '끔'
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': f'{"켜기" if on else "끄기"} {kit}'}); d['last'] = d['done'][-1]['what']
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def now_list():
    G = gload(); P = eff_parts(); out = os.path.join(HERE, 'site_local')
    if not os.path.isdir(out):
        rebuild_local()
    labels, _ = menu_of(out)
    on_kits = []
    for g in G['groups']:
        for kn in g['kits']:
            kj = kit_json(kn)
            if kj and own_part(kj) and P.get(own_part(kj)):
                on_kits.append((g['name'], kj.get('title', kn)))
    print('지금 내 사이트에 켜져 있는 것:', len(on_kits), '개')
    cur = None
    for gn, t in on_kits:
        if gn != cur:
            print(f'  [{gn}]', end=' '); cur = gn
        print(t, end=' · ')
    print('\n메뉴(첫 화면 위):', ' · '.join(labels) or '(없음)')
    print('내 PC 에서 열려면: python serve.py --open')


def group_find(word):
    G = gload()['groups']
    if word.isdigit() and 1 <= int(word) <= len(G):
        return G[int(word) - 1]
    w = word.replace(' ', '')
    return next((g for g in G if w in (g['key'], g['name'].replace(' ', '')) or (w and w in g['name'].replace(' ', ''))), None)


def run_group(g, headless_flags):
    print(f'━━ 묶음 「{g["name"]}」 ━━\n{g["intro"]}\n', flush=True)
    kits_ = [kit_json(k) for k in g['kits']]; kits_ = [k for k in kits_ if k]
    off = {k for k, v in (prog_load().get('toggles') or {}).items() if v == '끔'}
    skipped_off = [k['name'] for k in kits_ if k['name'] in off]
    kits_ = [k for k in kits_ if k['name'] not in off]
    if skipped_off:
        print('독자가 꺼 둔 기능은 건너뜁니다(다시 켜지 않음):', ', '.join(skipped_off), '\n', flush=True)
    # ㉠ 화면에 붙는 키트를 한꺼번에 켜서 내 PC 사이트에 붙인다
    ons = []
    for kj in kits_:
        op = own_part(kj)
        if op:
            ons += list(kj.get('parts') or [op])
    if ons:
        set_parts(sorted(set(ons)), True); out, last, rcb = rebuild_local()
        print(f'㉠ 이 묶음의 화면 기능을 내 사이트에 붙였습니다({last})', flush=True)
    labels, _ = menu_of(os.path.join(HERE, 'site_local'))
    print('   메뉴:', ' · '.join(labels), '\n', flush=True)
    ok = skip = bad = 0
    sys.path.insert(0, HERE); import selftest as T
    for n, kj in enumerate(kits_, 1):
        print(f'── ({n}/{len(kits_)}) {kj.get("title", kj["name"])} ──', flush=True)
        for m in (kj.get('must_know') or [])[:1]:
            print('㉢ 설명:', m.get('알것', ''), flush=True)
        r = subprocess.run(PY + ['selftest.py', kj['name']] + headless_flags, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
        outp = r.stdout.strip()
        print('\n'.join('   ' + l for l in outp.splitlines()[-9:]), flush=True)
        dirty = subprocess.run(['git', 'status', '--porcelain', 'kits/' + kj['name'] + '/data'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if '건너뜀' in outp and '단계 가운데' not in outp:
            skip += 1
        elif r.returncode == 0:
            ok += 1
        elif dirty:
            ok += 1; print('   ※ 독자가 바꾼 자료라 시험의 ✗ 는 예시 값과 달라서 나온 것입니다(고장 아님). 바꾼 값은 python serve.py --open 으로 직접 확인하세요.', flush=True)
        else:
            bad += 1
        if kj.get('try_change'):
            print('㉣ 해 볼 일:', kj['try_change'], flush=True)
        print(f'   ㉤ 이 기능은 켜 둘까요, 끌까요?  →  끄려면 python run.py 끄기 {kj["name"]}', flush=True)
    print(f'\n묶음 「{g["name"]}」 결과: 통과 {ok} · 건너뜀 {skip} · 안 됨 {bad}', flush=True)
    now_list()
    d = prog_load(); d.setdefault('groups', {})[g['key']] = {'t': time.strftime('%Y-%m-%d %H:%M'), 'ok': ok, 'skip': skip, 'bad': bad}
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': f'묶음 {g["name"]}(통과 {ok}·건너뜀 {skip}·안 됨 {bad})'}); d['last'] = d['done'][-1]['what']
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0 if bad == 0 else 1


def reader_cmd(rest):
    d = json.load(open(READER, encoding='utf-8')) if os.path.exists(READER) else {}
    if rest and rest[0] == '설정':
        for kv in rest[1:]:
            if '=' in kv:
                k, v = kv.split('=', 1); d[k.strip()] = v.strip()
        json.dump(d, open(READER, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('독자.json 에 적었습니다')
    print('독자.json:', json.dumps(d, ensure_ascii=False) if d else '(아직 없음 — 과외.md 의 「처음에 독자를 묻는다」 를 따라 한 번 묻고 `python run.py 독자 설정 해본것=… 만들고싶은것=… 시간=…` 로 적습니다)')
    return 0


def review_cmd():
    import random
    d = prog_load(); G = gload(); pool = []
    seen = [x['what'] for x in d['done'] if x['what'].startswith('키트 ')]
    names = [w.split()[1] for w in seen if len(w.split()) > 1]
    for c in d.get('confused', [])[-6:]:
        kj = kit_json(c['kit'])
        if kj:
            pool += [(0, kj, m) for m in (kj.get('must_know') or [])[:2]]
    for nm in names[-6:]:
        kj = kit_json(nm)
        if kj:
            pool += [(1, kj, m) for m in (kj.get('must_know') or [])]
    if not pool:
        print('아직 복습할 진도가 없습니다. python run.py 키트 계산기 처럼 한 가지를 먼저 해 보세요.'); return 0
    pool.sort(key=lambda x: x[0]); picked, used = [], set()
    for pr, kj, m in pool:
        if m['알것'] in used:
            continue
        used.add(m['알것']); picked.append((kj, m))
        if len(picked) == 3:
            break
    print('복습 물음 3개(답은 독자가 먼저 말하게 하고, 이 줄 아래 「정답 메모」는 에이전트만 봅니다):')
    for i, (kj, m) in enumerate(picked, 1):
        print(f'Q{i}. [{kj.get("title", kj["name"])}] 「{m["알것"][:40]}」 를 모르면 어떤 일이 생길까요?')
    print('— 정답 메모(에이전트용) —')
    for i, (kj, m) in enumerate(picked, 1):
        print(f'A{i}. {m.get("모르면", "")} (까닭: {m.get("까닭", "")})')
    return 0


def confuse_cmd(rest):
    if len(rest) < 2:
        print('사용: python run.py 혼동 <키트> <헷갈려 한 말>'); return 1
    d = prog_load(); d.setdefault('confused', []).append({'t': time.strftime('%Y-%m-%d %H:%M'), 'kit': rest[0], 'what': ' '.join(rest[1:])})
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('적었습니다'); return 0


def all_cmd():
    G = gload(); rc = 0
    fl = FLAGS if FLAGS else ['--headless']
    for g in G['groups']:
        rc |= run_group(g, fl)
    print('\n━━ 여덟 묶음을 끝까지 돌았습니다(묻는 자리는 기본값: 통과한 기능은 켜 둠) ━━'); now_list(); return rc


KINDS = {
    '정보 매거진': dict(alias=['매거진', '정보', 'magazine'], parts=['info', 'issue', 'search', 'prefs', 'monetize'], theme=('paper', ''), ref='정보 매거진',
        fill='독자 주제의 공식 자료(정부·기관 사이트)를 열어 확인 노트 한 건을 쓴다(notes/ 형식은 런북.md 3절, `python check.py` 로 대조, 예제 노트는 `python run.py 예제정리`로 먼저 옮길지 묻는다). 공식 자료에서 온 숫자는 출처, 못 찾은 것은 「아직 확인 안 됨」.'),
    '도구 모음': dict(alias=['도구', 'tools'], parts=['calc', 'glossary', 'compare', 'search', 'prefs', 'monetize'], theme=('doc', '#2f6fed'), ref='도구 모음',
        fill='독자가 쓰는 계산 하나를 정한다 → kits/calc/data/calculators.json 에 식과 입력칸을 쓴다(식의 근거를 설명에 적고, 모르는 숫자는 「예시」 표시). 용어 3개(glossary)와 비교표 한 장(compare)도 독자 주제로 바꾼다.'),
    '요리법 모음': dict(alias=['요리법', '요리', 'recipes'], parts=['recipes', 'search', 'prefs', 'monetize'], theme=('card', '#e4572e'), ref='요리법 모음',
        fill='독자가 말한 요리 다섯 개의 이름·재료·순서를 kits/recipes/data/recipes.json 에 쓴다(분량·시간은 「예시」 표시).'),
    '가계부 앱': dict(alias=['가계부', 'ledger'], parts=['ledger', 'calc', 'dday', 'prefs', 'pwa', 'monetize'], theme=('card', '#0ea5e9'), ref='가계부 앱',
        fill='계산기 식 하나(예: 이번 달 남은 돈)와 기다리는 날짜 3개(kits/dday/data/dates.json)를 독자 것으로 바꾼다. 가계부 입력은 방문자가 이 기기에서 직접 적는다.'),
}


def kind_find(word):
    w = (word or '').replace(' ', '')
    for k, v in KINDS.items():
        if w == k.replace(' ', '') or w in [a.replace(' ', '') for a in v['alias']]:
            return k
    return None


def _ref_hint(kind):
    """변환 상담에서 안내할 참고 명령: 본이 있는 틀은 조각 표로, 아니면 참고 사이트 종류가 있을 때만."""
    for k, v in (('날마다 순위', '깃허브트렌딩'), ('커뮤니티', '해커뉴스'), ('쇼핑몰', '검로드'), ('한 장 링크', '링크트리')):
        if kind.startswith(k):
            return f'본을 조각으로 보기: python run.py 나누기 {v}'
    w = kind.split()[0]
    if any(w in r['kind'] for r in ref_load()):
        return f'참고: python run.py 참고 {w}'
    return '참고 사이트 목록: python run.py 참고'


def ref_load():
    p = os.path.join(HERE, '참고', '서비스.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def ref_cmd(rest):
    R = ref_load()
    if not R:
        print('참고/서비스.json 이 없습니다.'); return 1
    kinds = [r['kind'] for r in R]
    if not rest:
        print('참고 사이트가 있는 종류:'); [print(f'  - {r["kind"]} ({len(r["sites"])}곳)') for r in R]; print('\n사용: python run.py 참고 정보 매거진 [--shots 폴더]'); return 0
    w = ' '.join(rest).replace(' ', '')
    pdir = os.path.join(HERE, '참고', '조각')
    pk = next((f for f in sorted(os.listdir(pdir)) if f.endswith('.json') and w and w in f.replace(' ', '')), None) if os.path.isdir(pdir) else None
    if pk:   # 조각 표가 있는 레퍼런스: 그 사이트가 무엇으로 버는지(확인된 것만)
        d = json.load(open(os.path.join(pdir, pk), encoding='utf-8')); e = d.get('earns')
        print(f'━━ 참고: {d["name"]} ━━\n{d.get("one_line", "")}')
        if not e:
            print('버는 길: 아직 확인해 적어 둔 것이 없습니다(조각 표의 「왜」 칸에 조각별로만 있습니다).' + (f'\n※ {d["biggest_diff"]}' if d.get('biggest_diff') else '')); return 0
        print('\n[이렇게 번다 — 확인된 것]'); [print('  · ' + x) for x in e['confirmed']]
        print(f'  (근거: {e["source"]})')
        if e.get('unconfirmed'):
            print('[확인하지 못한 것] ' + ' / '.join(e['unconfirmed']))
        print(f'\n우리는: {e["ours"]}\n[물음] 내 사이트는 무엇으로 벌 수 있을까요 — 지금 정하지 않아도 됩니다(미뤄 두기: python run.py 고름 …).')
        prog_add('참고 ' + d['name']); return 0
    hit = [r for r in R if w in r['kind'].replace(' ', '') or r['kind'].replace(' ', '') in w]
    if not hit:
        print('그 종류가 없습니다:', ', '.join(kinds)); return 1
    r = hit[0]
    print(f'━━ 참고 사이트: {r["kind"]} ━━')
    br = None
    if SHOTS:
        sys.path.insert(0, HERE); import selftest as T; br = T.find_browser(); os.makedirs(SHOTS, exist_ok=True)
    for i, s_ in enumerate(r['sites'], 1):
        print(f'\n[{i}] {s_["url"]}\n  무엇을 하는 곳: {s_["what"]}\n  이렇게 번다: {s_["earns"]}\n  (확인: {s_["checked"]})', flush=True)
        if br:
            host = re.sub(r'[^a-z0-9]+', '_', s_['url'].split('//')[1].lower()).strip('_')[:30]
            out = os.path.join(SHOTS, f'참고_{r["kind"].replace(" ", "")}_{i}_{host}.png')
            try:
                subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,860', '--virtual-time-budget=8000', f'--screenshot={out}', s_['url']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                print('  화면 저장:', os.path.basename(out), flush=True)
            except Exception:
                print('  (화면 저장 실패: 이 사이트는 건너뜁니다)')
    print(f'\n우리는: {r["ours"]}')
    prog_add('참고 사이트 ' + r['kind']); return 0


def plan_cmd():
    p = os.path.join(HERE, '기획서.md')
    if os.path.exists(p):
        print(open(p, encoding='utf-8').read())
    else:
        print('기획서.md 가 아직 없습니다. 아래 양식을 독자와 한 칸씩 채워 기획서.md 로 저장하세요(한 번에 한 칸씩 묻기).\n'); print(open(os.path.join(HERE, '기획서_양식.md'), encoding='utf-8').read())
    return 0


def apply_name():
    """기획서.md 의 ⑥칸(「이름 — 한 줄 소개」) 또는 --이름/--소개 옵션을 site.local.json 의 name·tagline 에 넣는다."""
    name = tag = None
    if '--이름' in A and len(A) > A.index('--이름') + 1:
        name = A[A.index('--이름') + 1]
    if '--소개' in A and len(A) > A.index('--소개') + 1:
        tag = A[A.index('--소개') + 1]
    p = os.path.join(HERE, '기획서.md')
    if not name and os.path.exists(p):
        for ln in open(p, encoding='utf-8').read().splitlines():
            if ln.strip().startswith('|') and '⑥' in ln:
                cells = [c.strip() for c in ln.strip().strip('|').split('|')]
                if len(cells) >= 2 and cells[1]:
                    parts = re.split(r'\s+[—–-]\s+|\s*/\s*|\s*·\s*', cells[1], maxsplit=1)
                    name = parts[0].strip(); tag = tag or (parts[1].strip() if len(parts) > 1 else None)
    if not name:
        return None
    sp = os.path.join(HERE, 'site.local.json'); d = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    d['name'] = name
    if tag:
        d['tagline'] = tag
    json.dump(d, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return name, tag


def _text_shot(title, blocks, tag):
    """글을 읽기 좋은 한 장으로 그려 SHOTS 에 저장."""
    if not SHOTS:
        return
    import selftest as T
    br = T.find_browser()
    if not br:
        return
    os.makedirs(SHOTS, exist_ok=True); out = os.path.join(SHOTS, f'서비스_{tag}.png'); T.text_png(br, title, blocks, out); print('  화면 저장:', os.path.basename(out), flush=True)


def _shot_site(out_dir, pages, tag, width=1280, height=860):
    """site_local 의 쪽들을 headless 로 찍어 SHOTS 에 저장(--shots 가 없으면 건너뜀). 폭이 좁으면 휴대폰 흉내."""
    if not SHOTS:
        return
    import selftest as T
    os.makedirs(SHOTS, exist_ok=True)
    outs = [os.path.join(SHOTS, f'서비스_{tag}_{n}.png') for n in range(1, len(pages) + 1)]
    if T.shoot_pages(out_dir, pages, outs, width, height, mobile=width < 600):
        for o in outs:
            print('  화면 저장:', os.path.basename(o), flush=True)


def service_cmd(rest):
    if not rest:
        print('종류: ' + ' · '.join(KINDS) + '\n사용: python run.py 서비스 정보 매거진 [단계 1~9] [--shots 폴더]\n단계: 1 참고 사이트 · 2 기획서 · 3 기능 붙이기 · 4 내용 채우기 · 5 돈이 나올 자리 · 6 꼭 있어야 할 쪽 · 7 겉모습 · 8 휴대폰으로 보기 · 9 올릴 준비 점검(「올릴까요」에서 멈춤)\n나머지 예시(`python run.py 조립`)는 「이런 것도 붙일 수 있다」 목록입니다.'); return 0
    step = None
    if rest[-1].isdigit():
        step = int(rest[-1]); rest = rest[:-1]
    kind = kind_find(' '.join(rest))
    if not kind:
        print('종류를 찾지 못했습니다:', ' · '.join(KINDS)); return 1
    K = KINDS[kind]; steps = [step] if step else list(range(1, 10)); rc = 0
    for st in steps:
        print(f'\n━━ [{kind}] 걸음 {st}/9 ━━', flush=True)
        if st == 1:
            rc |= ref_cmd(kind.split())
        elif st == 2:
            print('기획서 한 장을 독자와 쓴다(누구에게·무엇을·날마다/주마다 무엇이 새로 실리나·돈이 나올 길·내가 쓸 시간). 한 번에 한 칸씩 묻고 기획서.md 로 저장.'); plan_cmd()
            pp = os.path.join(HERE, '기획서.md'); src_ = pp if os.path.exists(pp) else os.path.join(HERE, '기획서_양식.md')
            _text_shot('기획서 한 장' + ('' if os.path.exists(pp) else ' (양식 — 독자와 채울 칸)'), [('기획서.md' if os.path.exists(pp) else '기획서_양식.md', open(src_, encoding='utf-8').read())], f'{kind.replace(" ", "")}_2기획서')
        elif st == 3:
            nm = apply_name()
            if nm:
                print(f'기획서 ⑥칸의 이름을 사이트에 넣었습니다: 「{nm[0]}」' + (f' — {nm[1]}' if nm[1] else ''))
            else:
                print('(아직 사이트 이름이 정해지지 않았습니다 — 기획서 ⑥칸을 받거나 `--이름 "…" --소개 "…"` 를 주면 이 걸음부터 그 이름으로 찍습니다)')
            allp = list(json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))['parts'])
            set_parts(allp, False); set_parts(K['parts'], True); out, last, rcb = rebuild_local()
            labels, _ = menu_of(out)
            print(f'기획서에 맞는 기능을 붙였습니다: {", ".join(K["parts"])}  ({last})\n메뉴: {" · ".join(labels)}\n왜 이 기능들인지를 독자에게 한 줄씩 말한다(과외.md 5절).'); _shot_site(out, ['', 'calc/' if 'calc' in K['parts'] else ('recipes/' if 'recipes' in K['parts'] else 'search/')], f'{kind.replace(" ", "")}_3붙이기')
            prog_add(f'서비스 {kind}: 기능 붙임')
        elif st == 4:
            print('내용을 실제로 채운다 — 예시 자료를 지우고 독자 주제로 세션이 자료를 만든다:\n ' + K['fill'] + '\n지어낸 숫자는 「예시」 표시, 공식 자료에서 온 것은 출처를 적는다. 채운 뒤 python serve.py 로 열어 확인.')
            _text_shot('내용 채우기 — ' + kind, [('이 종류에서 채울 것', K['fill']), ('원칙', '예시 자료는 지우고 독자 주제로 바꾼다. 지어낸 숫자는 「예시」 표시, 공식 자료에서 온 것은 출처를 적는다. 모르는 것은 독자에게 묻고 지어내지 않는다.')], f'{kind.replace(" ", "")}_4내용')
        elif st == 5:
            apply_name(); set_parts(['monetize'], True); out, last, rcb = rebuild_local()
            print('돈이 나올 자리를 만들었습니다(광고 칸·제휴 링크 칸(고지 자동)·후원/문의 링크 칸·소식 받기 칸). 값은 site.local.json 의 monetize 에 넣습니다(kits/monetize/README.md).\n광고·제휴·후원 서비스의 가입과 심사는 사람이 합니다 — 에이전트는 안내만 합니다.'); _shot_site(out, [('calc/' if 'calc' in K['parts'] else ('recipes/' if 'recipes' in K['parts'] else 'search/')) + '@bottom', 'disclosure/'], f'{kind.replace(" ", "")}_5돈자리')
        elif st == 6:
            out = os.path.join(HERE, 'site_local')
            if not os.path.isdir(out):
                rebuild_local()
            need = ['about/', '소개'], ['contact/', '문의'], ['privacy/', '개인정보 처리방침'], ['disclosure/', '광고·제휴 고지(광고·제휴가 있을 때)']
            for pth, nm in need:
                ok = os.path.exists(os.path.join(out, pth, 'index.html'))
                print(('✓' if ok else '✗') + f' {nm}  (/{pth})')
            S_ = {}
            try:
                S_ = json.load(open(os.path.join(HERE, 'site.local.json'), encoding='utf-8'))
            except Exception:
                pass
            about = S_.get('about') or ''
            print('소개문(about):', ('있음(' + str(len(about)) + '자)' if about else '없음 — 독자에게 두세 문장으로 받아 site.local.json 의 about 에 넣는다'))
            _shot_site(out, ['about/', 'contact/', 'privacy/', 'disclosure/'], f'{kind.replace(" ", "")}_6필수쪽')
        elif st == 7:
            th, ac = K['theme']
            if SHOTS:   # 고르기 전에 틀 여섯 가지로 첫 화면을 찍어 나란히 보인다
                import selftest as T, tempfile
                names = {'paper': '신문형', 'card': '카드 잡지형', 'shop': '가게형', 'doc': '문서형', 'play': '놀이터형', 'one': '한 장짜리'}
                os.makedirs(SHOTS, exist_ok=True)
                for ti, tn in enumerate(names, 1):
                    tmpd = tempfile.mkdtemp(prefix='theme_')
                    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=tmpd, SITE_THEME=tn, SITE_ACCENT=(ac if (tn == th and ac) else ''))
                    subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
                    o = os.path.join(SHOTS, f'서비스_{kind.replace(" ", "")}_7겉모습_{ti}_{tn}.png')
                    if T.shoot_pages(tmpd, [''], [o], 1280, 860):
                        print(f'  화면 저장: {os.path.basename(o)}  ({names[tn]})', flush=True)
            print(f'겉모습 후보(독자와 고른다): 신문형 paper · 카드 잡지형 card · 가게형 shop · 문서형 doc · 놀이터형 play · 한 장짜리 one. 이 종류의 추천: {th} {ac}\n고르면 site.local.json 에 "theme": "…", "accent": "#색" 을 넣고 다시 찍는다(python run.py 지금 → serve).')
            if '--적용' in A:
                pth = os.path.join(HERE, 'site.local.json'); d = json.load(open(pth, encoding='utf-8')) if os.path.exists(pth) else {}
                d['theme'] = th
                if ac:
                    d['accent'] = ac
                json.dump(d, open(pth, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); out, last, rcb = rebuild_local(); print('추천 틀을 적용했습니다:', last); _shot_site(out, [''], f'{kind.replace(" ", "")}_7겉모습')
        elif st == 8:
            out = os.path.join(HERE, 'site_local')
            if not os.path.isdir(out):
                rebuild_local()
            print('휴대폰 폭(390px)으로도 열어 봅니다.'); _shot_site(out, ['', 'search/'], f'{kind.replace(" ", "")}_8휴대폰', 390, 844)
        elif st == 9:
            rb = subprocess.run(PY + ['audit.py', '--dir', 'site_local'], cwd=HERE, env=dict(os.environ, SITE_BASE='/'), capture_output=True, text=True, encoding='utf-8', errors='replace'); print((rb.stdout + rb.stderr).strip()[-900:])
            print('\n주소 값(site.json 의 url·base)과 올릴 곳은 독자가 정합니다. 올리기는 하지 않았습니다.\n▶ 올릴까요? (이 자리에서 멈춥니다 — 독자가 「올려」라고 할 때만, 가입·로그인은 독자 몫)')
    return rc


POLFILE = os.path.join(HERE, '다듬기.json')
THINK = os.path.join(HERE, '생각.md')
MEAS = os.path.join(HERE, '만듦새.json')


def pol_steps():
    return json.load(open(POLFILE, encoding='utf-8'))['steps']


def local_load():
    fp = os.path.join(HERE, 'site.local.json')
    return json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}


def local_save(d):
    json.dump(d, open(os.path.join(HERE, 'site.local.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def cur_polish():
    return {str(k): v for k, v in (local_load().get('polish') or {}).items() if v}


def build_tmp(polish=None, parts=None, extra_env=None):
    """지금 설정(site.local.json)으로 임시 폴더에 찍는다. polish 를 주면 그 층 설정으로(미리보기)."""
    import tempfile
    out = tempfile.mkdtemp(prefix='polish_')
    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=out)
    if polish is not None:
        env['SITE_POLISH'] = json.dumps(polish)
    if parts is not None:
        env['PARTS'] = json.dumps(parts)
    if extra_env:
        env.update(extra_env)
    subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return out


def newest_note(out):
    nd = os.path.join(out, 'n')
    ids = sorted(os.listdir(nd), reverse=True) if os.path.isdir(nd) else []
    return ids[0] if ids else None


def score_site(out):
    """첫 화면(PC)·글 쪽(PC)·휴대폰 첫 화면의 만듦새 측정. {'pc':…, 'note':…, 'mobile':…}"""
    import selftest as T
    nid = newest_note(out); res = {}
    pcs = T.measure_site(out, [''] + ([f'n/{nid}/'] if nid else []), 1280, 860, False)
    res['pc'] = pcs[0] if pcs else {}
    if nid and len(pcs) > 1:
        res['note'] = pcs[1]
    mob = T.measure_site(out, [''], 390, 844, True)
    res['mobile'] = mob[0] if mob else {}
    return res


def grade_lines(res):
    import selftest as T
    lines = []; ok_n = tot = 0
    for lab, key in (('PC 첫 화면', 'pc'), ('PC 글 쪽', 'note'), ('휴대폰 첫 화면', 'mobile')):
        m = res.get(key)
        if not m:
            continue
        textual = bool(eff_parts().get('board')) and not eff_parts().get('info')   # 글자 위주 게시판(레퍼런스: 해커 뉴스)은 그림 수를 재지 않는다
        gl = T.grade(m, imgs_needed=(key != 'note' and not textual), empty_needed=(key != 'note'), min_imgs=((1 if key == 'mobile' else 3) if not eff_parts().get('info') else (2 if key == 'mobile' else 4)), cats_needed=(key != 'note' and bool(eff_parts().get('info'))))
        row = []
        for k, nm, v, th, ok in gl:
            tot += 1; ok_n += 1 if ok else 0
            row.append(f'{nm} {v}{"" if ok else " ✗(" + th + ")"}')
        lines.append(f'  {lab}: ' + ' · '.join(row))
    return lines, ok_n, tot


def shots_for(out, tag):
    if not SHOTS:
        return
    import selftest as T
    os.makedirs(SHOTS, exist_ok=True); nid = newest_note(out)
    jobs = [(['', ], [os.path.join(SHOTS, f'다듬기_{tag}_PC첫화면.png')], 1280, 860, False)]
    if nid:
        jobs.append(([f'n/{nid}/'], [os.path.join(SHOTS, f'다듬기_{tag}_글쪽.png')], 1280, 860, False))
    jobs.append((['', ], [os.path.join(SHOTS, f'다듬기_{tag}_휴대폰.png')], 390, 844, True))
    for pages, outs, w, h, mob in jobs:
        ok = T.shoot_pages(out, pages, outs, w, h, mob) or T.shoot_pages(out, pages, outs, w, h, mob)   # 한 번 실패하면 다시
        print(('  화면 저장: ' + outs[0]) if ok and os.path.exists(outs[0]) else ('  ✗ 화면 저장 실패: ' + outs[0]), flush=True)


def polish_cmd(rest):
    steps = pol_steps(); cur = cur_polish()
    opt = A[A.index('--안') + 1].upper() if '--안' in A and len(A) > A.index('--안') + 1 else None
    if not rest:
        print('다듬기 걸음(출발 모습 → 고품질). 지금 적용: ' + (', '.join(f'{k}{v}' for k, v in sorted(cur.items(), key=lambda x: int(x[0]))) or '없음(출발 모습)'))
        for st in steps:
            mark = ('적용 ' + cur[str(st['n'])]) if str(st['n']) in cur else ('준비됨' if st['status'] == 'ready' else '준비 중')
            print(f'  {st["n"]:>2}. {st["title"]}  [{mark}]')
        print('\n사용: python run.py 다듬기 1  (안 A·B 미리보기) → 독자가 고르면 python run.py 다듬기 1 --안 A --shots 폴더'); return 0
    if rest[0] == '0':
        print('━━ 다듬기 0. 이름과 한 줄 소개 ━━\n[상담: 먼저 물을 것] 이 사이트를 한 문장으로 소개하면 뭐라고 하시겠어요? 누가 보러 오나요?\n독자에게 먼저 묻는다: 「사이트 이름을 무엇으로 할까요? 한 줄로 소개하면?」 → 생각.md 에 정리 → 「이렇게 이해했습니다: … 이대로 적용할까요?」 → 독자가 예 하면 python run.py 고름 다듬기0 적용 \"<까닭>\" → python run.py 다듬기 0 --이름 \"…\" --소개 \"…\"')
        if '--이름' in A or os.path.exists(os.path.join(HERE, '기획서.md')) and False:
            if not need_choice('다듬기0', '적용'):
                return 1
            nm = apply_name()
            if nm:
                print(f'적용했습니다: 이름 「{nm[0]}」' + (f' — {nm[1]}' if nm[1] else '')); out, last, rcb = rebuild_local(); shots_for(out, '0_이름'); prog_add(f'다듬기 0 이름 {nm[0]}')
            print('\n[물음] 이 이름을 본 방문자가 이 사이트를 어떤 곳이라고 짐작할까요?\n여기서 멈추고 독자에게 묻습니다.')
        else:
            print('\n여기서 멈추고 독자에게 묻습니다.')
        return 0
    if rest[0] in ('다음', 'next'):
        nxt = next((st for st in steps if st['status'] == 'ready' and str(st['n']) not in cur and not chosen(f'다듬기{st["n"]}')), None)
        if nxt and nxt['n'] > 1 and not chosen(f'다듬기{nxt["n"] - 1}') and f'다듬기{nxt["n"] - 1}' not in choices():
            prev = next((x for x in steps if x['n'] == nxt['n'] - 1), None)
            if prev and prev['status'] == 'ready' and str(prev['n']) not in cur:
                print(f'멈춥니다 — 앞 걸음({prev["n"]}. {prev["title"]})을 아직 고르지 않았습니다. 하겠다/나중에/건너뜀 중 독자가 고른 뒤에 열립니다.'); return 1
        if not nxt:
            print('준비된 걸음을 모두 적용했습니다.'); return 0
        n = nxt['n']
    elif rest[0].isdigit():
        n = int(rest[0])
    else:
        print('사용: python run.py 다듬기 [번호|다음]'); return 1
    st = next((x for x in steps if x['n'] == n), None)
    if not st:
        print('그런 걸음이 없습니다'); return 1
    if st['status'] != 'ready':
        print(f'걸음 {n} 「{st["title"]}」 은(는) 아직 준비 중입니다.'); return 0
    if n == 10 and '7' not in cur:
        print('걸음 10 은 걸음 7(글 쪽) 위에 얹습니다. 먼저 걸음 7 을 독자와 고르세요.'); return 1
    import refcmp as RC
    rname = RC.current()[0]
    print(f'━━ 다듬기 {n}. {st["title"]} ━━\n[상담: 먼저 물을 것] {st.get("q", "")}\n[독자에게 말할 것(왜)] {st["why"]}\n[레퍼런스({rname})는 이렇게 합니다] {st["ref"]}')
    print('안: ' + ' / '.join(f'{k}) {v}' for k, v in st['options'].items()), flush=True)
    pre = build_tmp(cur); shots_for(pre, f'{n}_전')
    try:
        import selftest as T_
        nid_ = newest_note(pre); sl = RC.step_lines(n, RC.ours(T_, pre, f'n/{nid_}/' if nid_ else None))
        if sl:
            print('[레퍼런스 잰 값 / 우리 사이트의 지금 값]'); print('\n'.join(sl))
    except Exception as e_:
        print('(레퍼런스 차이를 재지 못했습니다:', repr(e_)[:60], ')')
    if st.get('follow'):
        print(f'[어떤 경우에 따르고 어떤 경우에 다르게 가나] {st["follow"]}')
    if opt is None:   # 미리보기: 안마다 첫 화면을 찍어 독자가 고르게 한다
        import selftest as T
        for o in st['options']:
            out = build_tmp({**cur, str(n): o})
            if SHOTS:
                os.makedirs(SHOTS, exist_ok=True); fp = os.path.join(SHOTS, f'다듬기_{n}_안{o}_PC첫화면.png')
                if T.shoot_pages(out, [''], [fp], 1280, 860):
                    print(f'  미리보기 저장: {fp}  ({o}안)', flush=True)
        print('\n[독자가 「뭐가 좋아요?」「아무거나」라고 하면 이렇게 말합니다] ' + ask_sentence({o: x.split(' → ')[0] if ' → ' in x else x for o, x in st['options'].items()}))
        print(f'\n[고를 것] 안 {" · ".join(st["options"])} 또는 나중에/건너뜀(이것도 고르는 것입니다)\n독자에게 먼저 묻는다: 「어느 쪽이 마음에 드나요? 왜요?」 → 정리해서 생각.md 에 적고(python run.py 정리 …), 「이렇게 이해했습니다: … 이대로 적용할까요?」 확인 뒤 python run.py 다듬기 {n} --안 A|B')
        return 0
    if opt not in st['options']:
        print('안은 ' + ' · '.join(st['options']) + ' 중 하나입니다'); return 1
    if not need_choice(f'다듬기{n}', opt):
        return 1
    sb = score_site(pre)
    import play; play.snap(f'다듬기 {n} {opt}안')
    d = local_load(); d.setdefault('polish', {})[str(n)] = opt; local_save(d)
    out, last, rcb = rebuild_local()
    shots_for(out, f'{n}_후')
    sa = score_site(out)
    ref_msg = ''
    try:
        import refcmp as RC2, selftest as T2
        nb, na = newest_note(pre), newest_note(out)
        ob = RC2.ours(T2, pre, f'n/{nb}/' if nb else None); oa = RC2.ours(T2, out, f'n/{na}/' if na else None)
        ch = RC2.changes(ob, oa); sb_, sa_ = RC2.same_count(ob), RC2.same_count(oa)
        ref_msg = f'[레퍼런스와의 차이] 같은 항목 {sb_[0]}/{sb_[1]} → {sa_[0]}/{sa_[1]}' + (''.join(f'\n  {"✓" if ok_ else "·"} {nm_}: {a_} → {b_}' for nm_, a_, b_, ok_ in ch) if ch else '\n  (이 걸음은 차이표의 항목을 바꾸지 않았습니다)')
    except Exception as e_:
        ref_msg = '(레퍼런스 차이를 재지 못했습니다: ' + repr(e_)[:60] + ')'
    lb, ob, tb = grade_lines(sb); la, oa, ta = grade_lines(sa)
    print(f'\n적용했습니다: 걸음 {n} · {opt}안 — 기본 점검 {ob}/{tb} → {oa}/{ta}'); print(ref_msg); print('[기본 점검 — 전]'); print('\n'.join(lb)); print('[기본 점검 — 후]'); print('\n'.join(la))
    json.dump(sa, open(MEAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    other = ', '.join(f'{k}) {v}' for k, v in st['options'].items() if k != opt)
    print(f'\n[방금 일어난 일] 걸음 {n} 「{st["title"]}」 {opt}안을 적용했습니다. 고르지 않은 안은: {other}')
    print(f'[독자가 해 볼 일] 화면(전·후 두 장)을 보고 마음에 안 드는 곳이 있는지 말하기, 또는 python run.py 되돌리기 {n} 로 끄고 다른 안 고르기')
    print(f'[물음] 먼저 「왜 그쪽을 고르셨나요?」 한 줄을 묻습니다. 그다음: {st["ask"]}   (답을 먼저 말하지 않는다 — 힌트: {st["ask_hint"]})')
    if st.get('expand'):
        print(f'[넓혀 보기(독자가 고르면 「해 볼 것」, 아니면 「미룬 것」에 적는다)] {st["expand"]}')
    if st.get('card'):
        print(f'[내_서비스.md] 이 걸음으로 채워질 칸: 「{st["card"]}」 → 독자의 답을 되말하고 python run.py 내서비스 칸 "{st["card"]}" "<정리한 말>" 로 적습니다.')
    nx = next((x for x in steps if x['n'] > n and x['status'] == 'ready'), None)
    print(f'[다음 걸음] ' + (f'{nx["n"]}. {nx["title"]} — 독자가 이 걸음을 하겠다/나중에/건너뛴다 중 고른 뒤에 python run.py 다듬기 {nx["n"]}' if nx else '다듬기 걸음을 모두 보았습니다.') + '\n\n여기서 멈추고 독자에게 묻습니다.')
    prog_add(f'다듬기 {n} {st["title"]} {opt}안')
    return 0


def undo_cmd(rest):
    if not rest or not rest[0].isdigit():
        import play; return play.undo_cmd(sys.modules[__name__], rest)
    d = local_load(); p = d.get('polish') or {}
    if str(int(rest[0])) not in p:
        print('그 걸음은 적용돼 있지 않습니다'); return 0
    p.pop(str(int(rest[0]))); d['polish'] = p; local_save(d)
    out, last, rcb = rebuild_local()
    if SHOTS:
        shots_for(out, f'되돌리기{rest[0]}')
    print(f'걸음 {rest[0]} 를 되돌렸습니다({last}). 지금 적용: ' + (', '.join(f'{k}{v}' for k, v in sorted(p.items(), key=lambda x: int(x[0]))) or '없음(출발 모습)')); prog_add(f'다듬기 {rest[0]} 되돌림'); return 0


def quality_cmd():
    out, last, rcb = rebuild_local()
    res = score_site(out); lines, ok_n, tot = grade_lines(res)
    print(f'━━ 만듦새 ① 기본 점검(잘림·넘침·대비·글자·그림) — {ok_n}/{tot} ━━'); print('\n'.join(lines))
    try:
        import refcmp as RC, selftest as T_
        nid_ = newest_note(out); tl, same, alln = RC.table(RC.ours(T_, out, f'n/{nid_}/' if nid_ else None))
        print('━━ 만듦새 ② 레퍼런스와의 차이 ━━'); print('\n'.join(tl))
    except Exception as e_:
        print('(레퍼런스 차이를 재지 못했습니다:', repr(e_)[:60], ')')
    bad = []
    for lab, key in (('PC 첫 화면', 'pc'), ('휴대폰 첫 화면', 'mobile')):
        m = res.get(key) or {}
        if m.get('minFontEl') and m.get('minFont', 99) < 13:
            bad.append(f'가장 작은 글자 {m["minFont"]}px: {m["minFontEl"]}')
        if m.get('minContrastEl') and m.get('minContrast', 99) < 4.5:
            bad.append(f'낮은 대비 {m["minContrast"]}: {m["minContrastEl"]}')
    for b in bad[:4]:
        print('  ✗', b)
    shots_for(out, '만듦새')
    json.dump(res, open(MEAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('다듬기로 올릴 수 있는 것: python run.py 다듬기'); return 0 if ok_n == tot else 1


def compare_cmd(rest):
    """레퍼런스 사이트를 옆에 두고 본다: 본의 화면과 우리 화면을 같은 크기로 찍어 나란히 한 장(내 PC 에만 저장, 저장소에는 넣지 않는다 — 남의 사이트 화면이므로)."""
    import refcmp as RC, selftest as T
    name, R = RC.current(); url = (R.get('url') or '').split(' ')[0]
    which = rest[0] if rest else '목록'
    if R.get('trend'):
        ours = 'trend/' if which != '글' else 'trend/meta-astryx/'; ref = url if which != '글' else (A[A.index('--본') + 1] if '--본' in A else url)
    elif R.get('board'):
        ours = 'board/' if which != '글' else 'board/?id=s1'
        ref = url if which != '글' else (A[A.index('--본') + 1] if '--본' in A else url)
    else:
        ours = ''; ref = url
        if which == '글':
            nid_ = newest_note(os.path.join(HERE, 'site_local')) if os.path.isdir(os.path.join(HERE, 'site_local')) else None
            ours = f'n/{nid_}/' if nid_ else ''; ref = A[A.index('--본') + 1] if '--본' in A else url
    if not ref.startswith('http'):
        print('레퍼런스 주소가 없습니다(python run.py 레퍼런스 값 url=https://…)'); return 1
    br = T.find_browser(); d = SHOTS or os.path.join(HERE, '비교'); os.makedirs(d, exist_ok=True)
    out, last, rc = rebuild_local(); mine = os.path.join(d, f'옆에두기_{which}_우리.png'); refp = os.path.join(d, f'옆에두기_{which}_본.png')
    T.shoot_pages(out, [ours], [mine], 1280, 860)
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,860', '--virtual-time-budget=8000', f'--screenshot={refp}', ref], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    side_by_side(refp, mine, os.path.join(d, f'옆에두기_{which}_나란히.png'), f'본: {name} ({ref})', '우리(지금)')
    print(f'본({name})과 우리 화면을 나란히 두었습니다 → {d}  (글 쪽은: python run.py 비교 글 --본 <본의 글 주소>)\n[독자와 볼 것] 어디가 같고 어디가 다른가 → 다른 곳을 본처럼 맞출지, 내 것답게 바꿀지는 독자가 고릅니다.\n※ 남의 사이트 화면이라 이 그림은 내 PC 에만 두고 저장소·책에 그대로 올리지 않습니다.'); return 0


def think_cmd():
    print(open(THINK, encoding='utf-8').read() if os.path.exists(THINK) else '생각.md 가 아직 없습니다. 독자가 하고 싶은 말을 받으면 python run.py 정리 "<독자의 말>" 로 남기세요.'); return 0


def organize_cmd(rest):
    def opt(k):
        return A[A.index(k) + 1] if k in A and len(A) > A.index(k) + 1 else ''
    words = [w for i, w in enumerate(rest) if not w.startswith('--') and (i == 0 or not rest[i - 1].startswith('--'))]
    said = ' '.join(words).strip()
    if not said:
        print('사용: python run.py 정리 "<독자의 말>" --한줄 "<세션이 정리한 한 줄>" --정함 "a;b" --미정 "c" --미룸 "d"'); return 1
    new = not os.path.exists(THINK)
    with open(THINK, 'a', encoding='utf-8') as f:
        if new:
            f.write('# 생각 — 독자의 말과 세션이 정리한 것\n> 세션이 곧바로 만들지 않고 먼저 정리한 기록입니다. 다음에 열면 이것부터 읽고 「지난번에 이렇게 정하셨습니다」로 시작합니다. 기획서.md 는 여기서 뽑아 만듭니다.\n')
        f.write(f'\n## {time.strftime("%Y-%m-%d %H:%M")}\n- **독자의 말**: {said}\n- **정리한 한 줄**: {opt("--한줄") or "(아직)"}\n')
        for lab, k in (('정한 것', '--정함'), ('아직 안 정한 것', '--미정'), ('미룬 것', '--미룸')):
            if opt(k):
                f.write(f'- **{lab}**: ' + '; '.join(x.strip() for x in opt(k).split(';') if x.strip()) + '\n')
    print('생각.md 에 적었습니다. 확인받기: 「이렇게 이해했습니다: … 이대로 만들까요?」'); return 0



# ---------------------------------------------------------------- 고르기(1·2장은 독자가 고르지 않으면 넘어가지 못한다)
def choices():
    return prog_load().get('choices') or {}


def chosen(key):
    c = choices().get(key)
    return c['pick'] if c else None


def record_choice(key, pick, why='', by='독자'):
    d = prog_load(); d.setdefault('choices', {})[key] = {'pick': pick, 'why': why, 'by': by, 't': time.strftime('%Y-%m-%d %H:%M')}
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': f'고름 {key}={pick}'}); d['last'] = d['done'][-1]['what']
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(THINK, 'a', encoding='utf-8') as f:
        if not os.path.exists(THINK) or os.path.getsize(THINK) == 0:
            f.write('# 생각 — 독자의 말과 세션이 정리한 것\n')
        f.write(f'\n## {time.strftime("%Y-%m-%d %H:%M")} 고름\n- **걸음**: {key}\n- **정함**: {pick}\n- **까닭(독자의 말)**: {why or "(아직 안 물음)"}\n')


VALID_KEY = re.compile(r'^(다듬기\d{1,2}|방식프런트|방식백엔드|변환|내놓기|도커|서버|백엔드)$')


def ask_sentence(options):
    """독자가 「뭐가 좋아요?」「아무거나」라고 할 때 세션이 그대로 읽어 줄 수 있는 말(독자가 앞서 한 말에 비추어 경우만 짚고, 정하지 않는다)."""
    d = svc_load(); said = ''
    for c in ('누구에게', '무엇을 주나', '왜 다시 오나'):
        if d.get(c):
            said = d[c][-1][2:]; break
    cases = ' / '.join(f'{k}안은 「{v[:46]}」 경우' for k, v in options.items())
    return (f'앞서 「{said}」라고 하셨으니, ' if said else '아직 서비스 얘기를 많이 못 들었지만, ') + f'{cases}에 맞습니다. ' + ('지금까지 하신 말로는 어느 경우에 더 가까운가요? ' if said else '어떤 분이 어떻게 보실 것 같은지 먼저 한 가지만 말씀해 주시겠어요? ') + '어느 쪽으로 할까요?'


def wrap_up_cmd():
    """걸음·장을 맺을 때: 내_서비스.md 와 고른 것에서 「오늘 배운 것 세 줄 + 헷갈려 한 것 + 다음에 할 것」 초안."""
    d = svc_load(); ch = choices(); done = prog_load().get('done', [])[-12:]
    lines = []
    for c in ('누구에게', '무엇을 주나', '왜 다시 오나', '무엇으로 버나'):
        if d.get(c):
            lines.append(f'{c}: {d[c][-1][2:]}')
    for k, v in list(ch.items())[-3:]:
        lines.append(f'{k} 에서 「{v["pick"]}」를 골랐고 까닭은 「{v.get("why") or "미기록"}」')
    lines = lines[:3] if len(lines) >= 3 else lines + ['(독자와 함께 이 칸을 더 채우면 세 줄이 됩니다)'] * (3 - len(lines))
    conf = [f'{c["kit"]}: {c["what"]}' for c in prog_load().get('confused', [])[-3:]]
    empty = [c for c in ('왜 다시 오나', '무엇으로 버나') if not d.get(c)]
    print('━━ 맺음 — 초안(독자와 다듬어 말합니다) ━━\n[오늘 배운 것 세 줄]'); [print(f'  {i}. {x}') for i, x in enumerate(lines, 1)]
    print('[헷갈려 한 것] ' + ('; '.join(conf) if conf else '(없음)'))
    print('[다음에 할 것] ' + (f'내_서비스.md 의 비어 있는 칸 — {", ".join(empty)} — 을 다음 걸음의 상담 물음에서 묻습니다' if empty else '다음 걸음을 독자가 고릅니다'))
    for c in empty:
        print(f'   ☐ 「{c}」 칸이 비었습니다 → python run.py 내서비스 칸 "{c}" "<정리한 말>"')
    print('\n독자와 말로 다듬은 뒤 python run.py 진도 기록 "<세 줄 요약>" 으로 남깁니다.'); return 0


def key_ok(key):
    return bool(VALID_KEY.match(key))


KEY_HELP = '걸음 키: 다듬기0 ~ 다듬기12 · 방식프런트 · 방식백엔드 · 변환 · 내놓기 · 도커 · 서버 · 백엔드  (예: python run.py 고름 다듬기1 A "읽기 편해서")'


def choose_cmd(rest):
    if rest and not key_ok(rest[0]):
        print(f'걸음 키가 맞지 않습니다: 「{rest[0]}」\n{KEY_HELP}'); return 1
    if len(rest) < 2:
        print('사용: python run.py 고름 <걸음> <고른 것> [까닭 한 줄]   예: 고름 다듬기1 A "읽기 편해서"   (나중에·건너뜀 도 고르는 것입니다)'); return 1
    record_choice(rest[0], rest[1], ' '.join(rest[2:]))
    print(f'기록했습니다: {rest[0]} = {rest[1]}' + ('' if len(rest) > 2 else '\n다음 할 일: 세션이 「왜 그쪽을 고르셨나요?」 한 줄을 묻고 python run.py 고름 으로 까닭을 덧붙인 뒤, 적용 명령을 부릅니다.')); return 0


def need_choice(key, opt):
    """--안 을 줄 때 독자가 고른 기록이 있어야 한다. 없으면 --고른이 독자 --까닭 으로 한 번에 기록할 수 있지만 독자의 말 없이는 부르지 않는다."""
    if not key_ok(key):
        print(f'내부 오류: 걸음 키 {key} 는 허용되지 않습니다. {KEY_HELP}'); return False
    if '--고른이' in A and len(A) > A.index('--고른이') + 1 and A[A.index('--고른이') + 1] == '독자':
        why = A[A.index('--까닭') + 1] if '--까닭' in A and len(A) > A.index('--까닭') + 1 else ''
        record_choice(key, opt, why); return True
    c = chosen(key)
    if c == opt:
        return True
    print(f'멈춥니다 — 이 걸음은 독자가 직접 고르는 걸음입니다.\n먼저 독자에게 묻고(안을 보여 주고 장단을 말한 뒤) 독자의 말을 python run.py 정리 "<말>" 로 생각.md 에 적으세요.\n그다음 python run.py 고름 {key} {opt} "<까닭 한 줄>" 로 기록해야 적용됩니다.' + (f'\n(지금 기록된 선택: {c})' if c else ''))
    return False


def chosen_cmd():
    ch = choices(); rows = []
    for k, v in ch.items():
        rows.append(f'- {k}: {v["pick"]}  ← {v.get("why") or "(까닭 없음)"}  ({v["t"]})')
    text = '# 내가 고른 것\n' + ('\n'.join(rows) if rows else '(아직 고른 것이 없습니다)')
    open(os.path.join(HERE, '고른것.md'), 'w', encoding='utf-8').write(text + '\n'); print(text)
    if SHOTS:
        _text_shot('내가 고른 것', [('고른 안과 까닭', '\n'.join(rows) or '(없음)')], '고른것')
    return 0


def deferred_cmd():
    rows = [f'- {k}: {v["pick"]} ({v.get("why") or ""})' for k, v in choices().items() if v['pick'] in ('나중에', '건너뜀')]
    print('미뤄 둔 것:\n' + ('\n'.join(rows) if rows else '(없음)') + '\n\n다시 하려면 해당 걸음을 다시 부르고 새로 고릅니다(python run.py 고름 … 로 덮어씀).'); return 0


# ---------------------------------------------------------------- 도커·서버
def sh_out(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        return r.returncode, (r.stdout or '').strip()
    except Exception as e:
        return 1, repr(e)[:80]


def pc_info():
    """읽기만: 운영체제·판·CPU·메모리·디스크·가상화·WSL2·도커 상태."""
    import platform
    sysn = platform.system(); info = {'system': sysn, 'arch': platform.machine(), 'release': platform.release()}
    ram = None
    if sysn == 'Windows':
        import ctypes
        class MS(ctypes.Structure):
            _fields_ = [('l', ctypes.c_ulong), ('m', ctypes.c_ulong), ('t', ctypes.c_ulonglong), ('a', ctypes.c_ulonglong), ('pt', ctypes.c_ulonglong), ('pa', ctypes.c_ulonglong), ('vt', ctypes.c_ulonglong), ('va', ctypes.c_ulonglong), ('ae', ctypes.c_ulonglong)]
        m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); ram = m.t / 2 ** 30
        rc, cap = sh_out(['powershell', '-NoProfile', '-Command', '(Get-CimInstance Win32_OperatingSystem).Caption'])
        info['edition'] = cap if rc == 0 else 'Windows ' + platform.release()
        rc, v = sh_out(['powershell', '-NoProfile', '-Command', '(Get-CimInstance Win32_Processor | Select -First 1).VirtualizationFirmwareEnabled'])
        info['virt'] = (v.strip().lower() == 'true') if rc == 0 and v.strip().lower() in ('true', 'false') else None
        rc, w = sh_out(['wsl', '--status'])
        rc2, w2 = sh_out(['wsl', '-l', '-v'])
        info['wsl'] = '있음' if (rc2 == 0 and w2) or rc == 0 else '없음'
    elif sysn == 'Darwin':
        rc, v = sh_out(['sysctl', '-n', 'hw.memsize']); ram = int(v) / 2 ** 30 if rc == 0 and v.isdigit() else None
        rc, pv = sh_out(['sw_vers', '-productVersion']); info['edition'] = 'macOS ' + pv
    else:
        try:
            for ln in open('/proc/meminfo'):
                if ln.startswith('MemTotal'):
                    ram = int(ln.split()[1]) / 2 ** 20
        except Exception:
            pass
        try:
            info['edition'] = [ln.split('=', 1)[1].strip().strip('"') for ln in open('/etc/os-release') if ln.startswith('PRETTY_NAME')][0]
        except Exception:
            info['edition'] = 'Linux'
    info['ram'] = ram
    import shutil as _sh
    info['disk'] = _sh.disk_usage(HERE).free / 2 ** 30
    dk = _sh.which('docker'); info['docker_cmd'] = bool(dk)
    if dk:
        rc, v = sh_out(['docker', 'version', '--format', '{{.Server.Version}}'], 15); info['engine'] = v if rc == 0 and v else None
        rc, v = sh_out(['docker', 'compose', 'version', '--short'], 15); info['compose'] = v if rc == 0 else None
    else:
        info['engine'] = info['compose'] = None
    return info


DOCKER_URLS = {'Windows': 'https://docs.docker.com/desktop/setup/install/windows-install/', 'Darwin': 'https://docs.docker.com/desktop/setup/install/mac-install/', 'Linux': 'https://docs.docker.com/engine/install/'}


def docker_recommend(i):
    sysn, arch = i['system'], (i['arch'] or '').lower(); arm = arch in ('arm64', 'aarch64'); warn = []
    if sysn == 'Windows':
        pick = 'Docker Desktop(WSL2 방식) — 윈도우 ' + ('ARM64' if arm else 'x64(AMD64)') + ' 판'; btn = '「Docker Desktop for Windows – ' + ('ARM64' if arm else 'x86_64 / AMD64') + '」'
    elif sysn == 'Darwin':
        pick = 'Docker Desktop — 맥 ' + ('Apple silicon' if arm else 'Intel chip') + ' 판'; btn = '「Docker Desktop for Mac – ' + ('Apple silicon' if arm else 'Intel chip') + '」'
    else:
        pick = 'Docker Engine + compose 플러그인(배포판 공식 절차)'; btn = '배포판 이름(Ubuntu·Debian·Fedora …)을 고르는 쪽'
    if i['ram'] is not None and i['ram'] < 8:
        warn.append(f'메모리가 {i["ram"]:.0f}GB 라 도커가 느리거나 다른 프로그램이 답답해질 수 있습니다 → 선택지: ① 그래도 쓰기(다른 프로그램을 닫고) ② 가벼운 설정(도커 설정에서 메모리를 2GB 로 제한) ③ 도커 없이 계속하기')
    if i['disk'] < 20:
        warn.append(f'남은 디스크가 {i["disk"]:.0f}GB 입니다(도커 이미지는 수 GB). 정리하거나 도커 없이 계속하는 길이 있습니다')
    if i.get('virt') is False and not i.get('engine'):   # 도커 엔진이 이미 떠 있으면 가상화는 켜져 있는 것(윈도우가 펌웨어 값을 거짓으로 알릴 수 있음)
        warn.append('가상화가 꺼져 있습니다 → 컴퓨터 설정(BIOS/UEFI)에서 Virtualization(Intel VT-x / AMD-V·SVM)을 켜야 합니다(제조사마다 방법이 달라 안내만 합니다) 또는 도커 없이 계속하기')
    return pick, btn, warn


def docker_cmd(rest):
    i = pc_info(); pick, btn, warn = docker_recommend(i)
    sub_ = rest[0] if rest else '보기'
    if sub_ == '확인':
        print('━━ 도커 확인 ━━'); print(f'  docker 명령: {"✓" if i["docker_cmd"] else "✗ 없음"}'); print(f'  엔진: {"✓ " + i["engine"] if i["engine"] else "✗ 안 떠 있음(Docker Desktop 을 실행해 고래 아이콘이 안정될 때까지 기다리세요)"}'); print(f'  compose: {"✓ " + i["compose"] if i["compose"] else "✗"}')
        if '--실행' in A and i['engine']:
            rc, o = sh_out(['docker', 'run', '--rm', 'hello-world'], 180); print('  hello-world:', '✓ 상자가 돌았습니다' if rc == 0 and 'Hello from Docker' in o else '✗ ' + o[-200:])
        elif i['engine']:
            print('  다음: 독자에게 「hello-world 로 한 번 돌려 볼까요(이미지를 내려받습니다)?」 묻고, 예면 python run.py 도커 확인 --실행')
        print('\n여기서 멈추고 결과를 독자에게 말합니다. 다 되면 python run.py 서버 로 이어갑니다.' if i['engine'] else '\n여기서 멈춥니다: 엔진이 안 떠 있으면 어느 단계에서 왜 막혔는지 같이 봅니다.'); return 0
    if sub_ == '열기':
        if '--예' not in A:
            print('독자가 「공식 사이트를 열어 주세요」라고 한 뒤에만 열립니다. 독자에게 「공식 사이트를 열까요?」 물어보고, 예면 python run.py 도커 열기 --예'); return 1
        import webbrowser
        url = DOCKER_URLS.get(i['system'], DOCKER_URLS['Linux']); webbrowser.open(url)
        print(f'독자의 브라우저로 공식 설치 쪽을 열었습니다: {url}\n누를 곳: {btn}\n앞으로 나올 창을 미리 말해 줍니다: 내려받은 설치 파일 실행 → (관리자 승인 창) → WSL2 설치/업데이트 안내(윈도우) → 재부팅 요청 → Docker Desktop 첫 실행 약관 동의(회사 PC·큰 회사는 유료 조건이 있습니다) → 고래 아이콘이 안정될 때까지 기다림.\n설치와 창 진행은 독자가 합니다. 끝났다고 하면 python run.py 도커 확인'); return 0
    if sub_ == '설치':
        if '--예' not in A or '--명령' not in A:
            print('명령으로 설치하는 둘째 길은 독자가 「명령으로 해 주세요」라고 했을 때만입니다(관리자 승인 창·재부팅이 따라옵니다). 독자에게 묻고, 예면 python run.py 도커 설치 --예 --명령'); return 1
        cmd = {'Windows': ['winget', 'install', '-e', '--id', 'Docker.DockerDesktop'], 'Darwin': ['brew', 'install', '--cask', 'docker']}.get(i['system'])
        if not cmd:
            print('이 운영체제는 배포판 공식 절차를 따릅니다: ' + DOCKER_URLS['Linux']); return 0
        print('실행:', ' '.join(cmd)); return subprocess.run(cmd).returncode
    # 보기(기본): PC 를 읽고 추천을 말한 뒤 멈춤
    print('━━ 도커 — 먼저 왜 쓰는지 ━━\n[독자에게 말할 것] 도커는 프로그램을 「상자」에 담아 돌리는 도구입니다. 내 PC 를 어지르지 않고, 나중에 클라우드에 올릴 때도 같은 상자를 그대로 가져갑니다.')
    print('\n[지금 이 PC(읽기만 했습니다)]')
    print(f'  운영체제: {i.get("edition")} · CPU: {i["arch"]} · 메모리: {("%.0f GB" % i["ram"]) if i["ram"] else "알 수 없음"} · 남은 디스크: {i["disk"]:.0f} GB')
    if i['system'] == 'Windows' and not i['engine']:
        print(f'  가상화: {"켜짐" if i.get("virt") else ("꺼짐" if i.get("virt") is False else "알 수 없음")} · WSL2: {i.get("wsl")}')
    print(f'  도커: 명령 {"있음" if i["docker_cmd"] else "없음"} · 엔진 {i["engine"] or "안 떠 있음/없음"} · compose {i["compose"] or "없음"}')
    if i['engine'] and i['compose']:
        print('\n[판단] 이미 도커가 있고 엔진도 떠 있습니다. 설치는 필요 없습니다. → python run.py 서버'); print('\n여기서 멈추고 독자에게 「도커가 이미 있습니다. 서버를 켜 볼까요?」 묻습니다.'); return 0
    print(f'\n[추천] 이 PC 는 {i.get("edition")} · {i["arch"]} 입니다. {pick} 이 맞습니다. 이것으로 할까요?')
    for w in warn:
        print('  ⚠', w)
    print(f'\n[고를 것] ① 이 판으로 공식 사이트를 열기(내려받기·설치는 독자가) ② 명령으로 설치(둘째 길) ③ 도커 없이 계속하기(백엔드 걸음만 건너뛰고 나중에 이어서)')
    print('\n여기서 멈추고 독자에게 묻습니다: 「도커를 써 볼까요?」 → 「이 판을 추천합니다, 이것으로 할까요?」 → 「공식 사이트를 열까요?」 (한 번에 하나, 답을 python run.py 고름 도커 … 로 기록)'); return 0


def env_ensure():
    p = os.path.join(HERE, '.env')
    if not os.path.exists(p):
        import secrets as _s
        open(p, 'w').write('DB_PASSWORD=' + _s.token_hex(12) + '\n')


def server_cmd(rest):
    sub_ = rest[0] if rest else '켜기'
    if sub_ == '암호':
        import hashlib, threading
        pw = os.environ.get('FM_ADMIN_PW', '')
        if not pw:
            real = False
            if os.name == 'nt':
                try:
                    import ctypes
                    mode = ctypes.c_ulong(); real = bool(ctypes.windll.kernel32.GetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-10), ctypes.byref(mode)))
                except Exception:
                    real = False
            else:
                real = sys.stdin.isatty()
            if not real:
                print('이 셸에서는 암호를 입력받을 수 없습니다(입력이 연결돼 있지 않음).\n독자가 직접: ! python run.py 서버 암호   (세션 입력창에서 ! 를 앞에 붙여 실행하면 독자가 암호를 칠 수 있습니다) — 또는 환경변수 FM_ADMIN_PW 로 주고 실행.'); return 1
            import getpass
            box = {}
            t = threading.Thread(target=lambda: box.setdefault('pw', getpass.getpass('운영자 암호(8자 이상, 화면에 안 보임): ')), daemon=True); t.start(); t.join(90)
            if t.is_alive():
                print('90초 동안 입력이 없어 끝냅니다. 독자가 직접: ! python run.py 서버 암호'); return 1
            pw = box.get('pw', '')
        if len(pw) < 8:
            print('암호는 8자 이상이어야 합니다.'); return 1
        os.makedirs(os.path.join(HERE, 'data', 'app'), exist_ok=True); salt = os.urandom(8).hex()
        json.dump({'salt': salt, 'iters': 120000, 'hash': hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 120000).hex()}, open(os.path.join(HERE, 'data', 'app', 'admin.json'), 'w'))
        print('운영자 암호를 정했습니다(파일에는 해시만 저장됩니다).')
        rc, o = sh_out(['docker', 'compose', 'ps', '--status', 'running', '-q', 'app'], 15)
        if rc == 0 and o.strip():   # ⑩ 서버가 이미 떠 있으면 다시 띄워 새 암호가 바로 쓰이게
            subprocess.run(['docker', 'compose', 'restart', 'app'], cwd=HERE, capture_output=True); print('떠 있던 서버를 다시 띄워 새 암호가 바로 쓰이게 했습니다.')
        return 0
    dc = ['docker', 'compose']
    env_ensure()
    if sub_ in ('끄기', 'down'):
        return subprocess.run(dc + ['down'], cwd=HERE).returncode
    if sub_ in ('상태', 'ps'):
        subprocess.run(dc + ['ps'], cwd=HERE)
        try:
            import urllib.request as ur
            print(ur.urlopen('http://127.0.0.1:8080/api/health', timeout=3).read().decode()[:200])
        except Exception:
            print('서버가 응답하지 않습니다(꺼져 있거나 아직 뜨는 중).')
        return 0
    if sub_ == '로그':
        return subprocess.run(dc + ['logs', '--tail', '40', 'app'], cwd=HERE).returncode
    i = pc_info()
    if not (i['engine'] and i['compose']):
        print('멈춥니다 — 도커가 없거나 엔진이 안 떠 있습니다.\n독자에게: 「도커가 있으면 서버(백엔드) 걸음을 할 수 있습니다. 설치해 볼까요, 아니면 백엔드 없이 계속할까요?」 → python run.py 도커 로 PC 를 보고 추천하거나, 백엔드 걸음을 건너뜀으로 고르고(python run.py 고름 백엔드 건너뜀 "도커 없음") 계속합니다.'); return 1
    if sub_ == '다시':
        subprocess.run(dc + ['restart'], cwd=HERE); return 0
    if not os.path.exists(os.path.join(HERE, 'data', 'app', 'admin.json')):
        print('멈춥니다 — 운영자 암호가 아직 없습니다. 독자가 직접 정합니다: ! python run.py 서버 암호'); return 1
    P_ = eff_parts()
    if not P_.get('backend'):
        print('백엔드 키트가 꺼져 있습니다. 먼저 python run.py 켜기 backend 로 켜세요(필요하면 댓글·문의·소식 받기도).'); return 1
    env_ensure(); t0 = time.time(); stamp = lambda: f'{time.time() - t0:.0f}초'
    print('[1/4] 사이트를 찍는 중…', flush=True); out, last, rcb = rebuild_local()
    print(f'[2/4] 서버 상자를 만들고 필요한 이미지를 내려받는 중(처음에는 3~5분, 두 번째부터는 몇 초) — {stamp()}', flush=True)
    import threading
    alive = {'on': True}
    def beat():
        while alive['on']:
            time.sleep(15)
            if alive['on']:
                print(f'      … 아직 하는 중입니다({stamp()} 지남)', flush=True)
    threading.Thread(target=beat, daemon=True).start()
    r1 = subprocess.run(dc + ['build', '--progress', 'plain'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r1.returncode != 0:
        alive['on'] = False; print('상자 만들기에 실패했습니다:\n' + (r1.stdout + r1.stderr)[-600:]); return r1.returncode
    print(f'[3/4] 데이터베이스와 서버를 켜는 중 — {stamp()}', flush=True)
    rc = subprocess.run(dc + ['up', '-d'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    alive['on'] = False
    if rc.returncode != 0:
        print('도커 실행에 실패했습니다:\n' + (rc.stdout + rc.stderr)[-500:] + '\npython run.py 서버 로그 로 이유를 같이 봅니다.'); return rc.returncode
    print(f'[4/4] 뜰 때까지 기다리는 중 — {stamp()}', flush=True)
    import urllib.request as ur
    for _ in range(60):
        try:
            h = ur.urlopen('http://127.0.0.1:8080/api/health', timeout=3).read().decode(); break
        except Exception:
            time.sleep(2)
    else:
        print('아직 안 떴습니다. python run.py 서버 상태 / 서버 로그'); return 1
    print(f'서버가 켜졌습니다 → http://127.0.0.1:8080/   운영자 화면 → http://127.0.0.1:8080/admin/\n{h}\n끄기: python run.py 서버 끄기 · 상태: 서버 상태 · 로그: 서버 로그\n\n여기서 멈추고 독자에게 보여 줍니다: 사이트를 열어 댓글 칸이 켜진 것을 보고, 자료가 어디에 쌓이는지(JSON 문서) 설명합니다.'); return 0


def docs_cmd(rest):
    col = rest[0] if rest else 'comments'
    rc, o = sh_out(['docker', 'compose', 'exec', '-T', 'app', 'python', '/app/app.py', '--dump', col], 30)
    print(o if rc == 0 else '서버가 꺼져 있거나 모음 이름이 틀렸습니다(모음: visits·comments·likes·contacts·subscribers·poll_votes·kv). python run.py 서버 로 켜세요.'); return 0 if rc == 0 else 1


def lab_cmd(rest):
    import lab
    if not rest or rest[0] not in lab.EXPS:
        print('실험: ' + ' · '.join(lab.EXPS) + '\n사용: python run.py 실험 좋아요 [--shots 폴더]  (임시 폴더에서만 돌고 끝나면 지웁니다. PostgreSQL 에서도 같은 개념입니다)'); return 0
    r = lab.EXPS[rest[0]]()
    print(f'━━ {r["title"]} ━━\n[독자에게 말할 것] {r["say"]}\n[눈앞의 결과]'); [print('  ' + x) for x in r['show']]
    print(f'\n[물음] {r["ask"]}\n[힌트·풀이(독자가 답한 뒤에)] {r["hint"]}\n\n여기서 멈추고 독자에게 묻습니다.')
    _text_shot(r['title'], [('독자에게 말할 것', r['say']), ('눈앞의 결과', '\n'.join(r['show'])), ('물음', r['ask'])], '실험_' + rest[0])
    prog_add('실험 ' + rest[0]); return 0 if r['ok'] else 1


def release_cmd(rest):
    w = ' '.join(rest)
    if not rest:
        print('━━ 내놓기 — 먼저 묻습니다 ━━\n「이 PC 를 24시간 켜 둘 수 있나요?」\n  예 → python run.py 내놓기 24시간  (지금 그대로 둔 채 바깥에서 들어오게만 연다)\n  아니오 → python run.py 내놓기 클라우드  (화면과 백엔드를 클라우드에 올린다)\n\n여기서 멈추고 독자에게 묻습니다. 답은 python run.py 고름 내놓기 24시간|클라우드 로 기록. 실제로 바깥에 여는 일은 이 도구가 하지 않습니다(자세한 안내: 올리기.md).'); return 0
    P_ = eff_parts(); ok = lambda c: '✓' if c else '☐'
    adm = os.path.exists(os.path.join(HERE, 'data', 'app', 'admin.json'))
    if '24' in w:
        print('━━ 내놓기 · 24시간 PC 길 점검표 ━━'); print(f'{ok(adm)} 운영자 암호를 정함(python run.py 서버 암호)'); print(f'{ok(P_.get("backend"))} backend 키트 켜짐'); print(f'{ok(os.path.exists(os.path.join(HERE, ".env")))} 데이터베이스 암호(.env) 만들어짐(서버를 한 번 켜면 생김)')
        print('사람이 할 것(가입·로그인·공유기 설정은 독자 몫): ☐ PC 가 꺼지지 않게 절전 끄기·재부팅 뒤 저절로 다시 뜨게 ☐ 바깥 주소 붙이기(터널 서비스 또는 공유기 포트 설정, 도메인은 선택) ☐ 바깥에 열 때: 운영자 화면 암호가 강한지·/admin/ 주소를 알리지 않기·쓰기 횟수 제한 확인 ☐ db 백업 한 줄(실험 백업 참고)')
    elif '클라우드' in w or 'cloud' in w:
        print('━━ 내놓기 · 클라우드 길 점검표 ━━'); print(f'{ok(True)} 같은 상자(Dockerfile·compose.yaml)를 그대로 올릴 수 있게 준비됨'); print(f'{ok(adm)} 운영자 암호'); print('사람이 할 것(가입·결제는 독자 몫, 세션은 안내와 준비까지): ☐ 올릴 곳 고르기(올리기.md 의 선택지와 드는 돈) ☐ 클라우드 db 만들고 DATABASE_URL 넣기 ☐ 백업 파일(JSON)을 클라우드 db 에 넣기 ☐ 올린 뒤 site.json 의 url·base 에 주소 넣고 다시 찍기')
    else:
        print('24시간 또는 클라우드 중에서 고르세요'); return 1
    print('\n여기서 멈춥니다(바깥에 여는 일은 하지 않았습니다).'); return 0


SVC = os.path.join(HERE, '내_서비스.md')
SVC_CARDS = ['누구에게', '무엇을 주나', '왜 다시 오나', '무엇으로 버나', '날마다 쓸 시간', '하지 않을 것', '닮고 싶은 곳', '만드는 방식', '해 볼 것', '미룬 것']


def svc_load():
    d = {}
    if os.path.exists(SVC):
        cur = None
        for ln in open(SVC, encoding='utf-8').read().splitlines():
            if ln.startswith('## '):
                cur = ln[3:].strip(); d[cur] = []
            elif cur and ln.strip() and not ln.startswith('> '):
                d[cur].append(ln.strip())
    return d


def svc_save(d):
    out = '# 내 서비스 한 장\n> 상담하며 독자의 답을 되말하고 정리한 것입니다. 2장의 기획서와 3장의 운영 규칙은 이 한 장에서 나옵니다.\n'
    for c in SVC_CARDS:
        out += f'\n## {c}\n' + ''.join(f'{x}\n' for x in d.get(c, []))
    open(SVC, 'w', encoding='utf-8').write(out)


def service_card_cmd(rest):
    d = svc_load()
    if rest and rest[0] == '칸':
        if len(rest) < 3 or rest[1] not in SVC_CARDS:
            print('사용: python run.py 내서비스 칸 "<칸 이름>" "<정리한 말>"   칸: ' + ' · '.join(SVC_CARDS)); return 1
        line = '- ' + ' '.join(x for x in rest[2:] if x != '--바꾸기')
        if '--바꾸기' in A:
            d[rest[1]] = [line]; msg = '바꿨습니다'
        elif line in d.get(rest[1], []):
            msg = '같은 말이 이미 있어 그대로 둡니다'
        else:
            d.setdefault(rest[1], []).append(line); msg = '적었습니다'
        svc_save(d); print(f'「{rest[1]}」 칸에 {msg}. (같은 칸의 말을 바꾸려면 --바꾸기)')
    d = svc_load()
    print('━━ 내 서비스 한 장 — 어느 칸이 채워졌나 ━━')
    for c in SVC_CARDS:
        v = d.get(c) or []
        print(f'  {"✓" if v else "☐"} {c}' + (': ' + ' / '.join(x[2:] for x in v)[:90] if v else ''))
    ch = choices()
    if ch:
        print('  지금까지 고른 것: ' + ' · '.join(f'{k}={v["pick"]}' for k, v in ch.items()))
    empty = [c for c in SVC_CARDS[:7] if not d.get(c)]
    print('\n비어 있는 칸은 다음 걸음의 상담 물음에서 채웁니다: ' + (', '.join(empty) if empty else '모두 채워졌습니다')); return 0



# ---------------------------------------------------------------- 만드는 방식(프런트엔드·백엔드) — 서비스의 말로 묻고, 세션은 경우를 말하고, 독자가 고른다
WAYS = {
    '프런트': dict(key='방식프런트', title='화면을 만드는 방식', q='방문자가 이 서비스에서 주로 무엇을 하나요? 읽고 가나요, 직접 만지나요(계산·입력·게임), 날마다 열어 쓰나요?',
        opts={'가': dict(name='미리 찍어 두는 화면(지금 방식)', good='글과 정보가 중심이고, 빠르게 열려야 하고, 돈을 안 들이고, 검색에서 잘 잡히길 바랄 때', hard='방문자가 값을 넣고 바로 바뀌는 것(계산기·가계부)이 중심이면 그 쪽은 따로 얹어야 합니다', parts_on=[], preview=''),
              '나': dict(name='누르면 그 자리에서 바뀌는 화면을 얹기', good='도구·가계부·퀴즈·게임처럼 방문자가 만지는 것이 중심일 때(지금 틀 위에 그런 쪽만 따로 붙입니다)', hard='만질 것을 하나하나 만들어야 해서 손이 더 가고, 글 중심 사이트에는 필요 없습니다', parts_on=['calc', 'quiz'], preview='calc/'),
              '다': dict(name='앱처럼 쓰는 화면(홈 화면 설치·오프라인)', good='방문자가 날마다 여는 도구이고, 인터넷이 없어도 열려야 하고, 홈 화면에 두고 싶을 때', hard='처음 열 때 저장하는 쪽을 관리해야 하고, 갱신이 반영되기까지 시간이 걸릴 수 있습니다', parts_on=['pwa', 'prefs'], preview='app/')}),
    '백엔드': dict(key='방식백엔드', title='방문자가 남기는 것을 받는 방식', q='방문자가 이 서비스에 남기게 하고 싶은 것이 있나요(댓글·문의·소식 받기 주소)? 받으면 운영에서 무엇이 늘까요(날마다 확인·답·관리)?',
        opts={'가': dict(name='받지 않는다(백엔드 없음)', good='읽고 가는 서비스이고, 운영 손을 가장 적게 쓰고 싶고, 개인정보를 맡고 싶지 않을 때(도커를 못 쓰는 PC 도 이 길로 끝까지 갑니다)', hard='방문자의 목소리와 방문 수를 알기 어렵습니다', parts_off=['backend', 'comments', 'contact', 'subscribe'], preview=''),
              '나': dict(name='내 PC 의 도커 서버로 받는다(PostgreSQL·JSON 문서)', good='댓글·통계·문의·소식 받기·운영자 화면이 필요하고, 방문자와 이어지는 서비스를 하고 싶을 때', hard='PC 를 켜 두거나 클라우드로 옮겨야 하고, 남의 글과 메일 주소를 맡는 책임이 생기며, 날마다 확인할 것이 늘어납니다', parts_on=['backend', 'comments', 'contact', 'subscribe'], preview='contact/'),
              '다': dict(name='바깥 서비스에 맡긴다(댓글·양식·통계를 대신해 주는 곳)', good='서버를 두기 싫지만 댓글·문의는 받고 싶을 때', hard='준비 중입니다(가입은 사람 몫이고 자료가 남의 곳에 쌓입니다)', parts_on=None, preview='')})}


def ways_cmd(rest):
    if not rest or rest[0] not in WAYS:
        if rest and rest[0] == '바꾸기':
            for k, v in WAYS.items():
                record = choices().get(v['key'])
                print(f'  {k}: {record["pick"] + " ← " + (record.get("why") or "") if record else "(아직 안 고름)"}')
            print('\n바꾸려면 python run.py 방식 프런트(또는 백엔드) 로 다시 미리보기 → 독자가 새로 고르고 python run.py 고름 … 기록 → --안 으로 적용.'); return 0
        print('방식 걸음: 프런트(화면을 만드는 방식) · 백엔드(방문자가 남기는 것을 받는 방식)\n사용: python run.py 방식 프런트 [--shots 폴더]  /  방식 바꾸기'); return 0
    k = rest[0]; W = WAYS[k]; opt = A[A.index('--안') + 1] if '--안' in A and len(A) > A.index('--안') + 1 else None
    print(f'━━ 방식 · {W["title"]} ━━\n[상담: 먼저 물을 것] {W["q"]}')
    d = svc_load(); print('[독자가 앞에서 한 말(내_서비스.md)] ' + (' / '.join(f'{c}: {d[c][0][2:]}' for c in ("누구에게", "무엇을 주나", "왜 다시 오나") if d.get(c))[:200] or '(아직 없음 — 먼저 물어서 채웁니다)'))
    print('\n[고를 것 — 세션은 고르지 않고, 어떤 경우에 어느 쪽이 좋은지만 말합니다]')
    for o, v in W['opts'].items():
        print(f'  ({o}) {v["name"]}\n      이런 경우에 좋습니다: {v["good"]}\n      이런 경우에는 손이 더 갑니다: {v["hard"]}')
    if opt is None:
        print('\n[독자가 「뭐가 좋아요?」라고 하면 이렇게 말합니다] ' + ask_sentence({o: x['good'] for o, x in W['opts'].items()}))
        if SHOTS:
            import selftest as T
            base = dict(eff_parts()); os.makedirs(SHOTS, exist_ok=True)
            for o, v in W['opts'].items():
                if v.get('parts_on') is None:
                    continue
                pr = dict(base)
                for p_ in (v.get('parts_on') or []):
                    pr[p_] = True
                for p_ in (v.get('parts_off') or []):
                    pr[p_] = False
                out = build_tmp(None, pr); fp = os.path.join(SHOTS, f'방식_{k}_{o}안.png')
                mob = (k == '프런트' and o == '다')
                if T.shoot_pages(out, [v['preview'] or ''], [fp], 390 if mob else 1280, 844 if mob else 860, mob):
                    print(f'  미리보기 저장: {fp}  ({o}안)', flush=True)
        print(f'\n독자에게 묻습니다: 「지금까지 말씀하신 것으로는 어느 경우에 가깝나요? 어느 쪽으로 할까요?」 — 독자가 「뭐가 좋아요?」라고 물으면 독자가 앞에서 한 말에 비추어 어느 경우에 해당하는지를 짚어 주되, 정해 주지는 않습니다.\n답을 python run.py 정리 로 적고, python run.py 고름 {W["key"]} <가|나|다> "<까닭>" 로 기록한 뒤 python run.py 방식 {k} --안 <가|나|다>\n\n여기서 멈추고 독자에게 묻습니다.'); return 0
    if opt not in W['opts']:
        print('안은 가·나·다 중 하나입니다'); return 1
    v = W['opts'][opt]
    if k == '백엔드' and opt == '다':
        print('(다)안은 준비 중입니다. 지금은 (가)(나) 중에서 고르거나, 나중에를 고릅니다.'); return 0
    if not need_choice(W['key'], opt):
        return 1
    if v.get('parts_off'):
        set_parts(v['parts_off'], False)
    if v.get('parts_on'):
        set_parts(v['parts_on'], True)
    if k == '백엔드' and opt == '가' and not any(eff_parts().get(p_) for p_ in ('backend', 'comments', 'contact', 'subscribe')):
        last = '적용할 것 없음 — 이미 백엔드가 꺼져 있어 기록만 남깁니다'
    else:
        out, last, rcb = rebuild_local()
    d = svc_load(); d.setdefault('만드는 방식', []).append(f'- {W["title"]}: ({opt}) {v["name"]} ← {(choices().get(W["key"]) or {}).get("why") or "까닭 미기록"}'); svc_save(d)
    other = ' / '.join(f'({o}) {x["name"]}' for o, x in W['opts'].items() if o != opt)
    print(f'\n[방금 일어난 일] ({opt}) {v["name"]} 을 적용했습니다({last}). 고르지 않은 안: {other}')
    if k == '백엔드' and opt == '나':
        print('[다음] 도커 갈림: python run.py 도커 로 PC 를 보고(이미 있으면 바로) → python run.py 서버. 도커를 못 쓰는 PC 면 (가) 로 돌아가 같은 길을 끝까지 갑니다.')
    if k == '백엔드' and opt == '가':
        print('[다음] 댓글·통계·운영자 화면 걸음은 이 길에서는 나오지 않습니다. 3장의 운영자 화면 자리는 상태 쪽과 쉬는시간 출력이 대신합니다.')
    print('[물음] 이 방식을 고르니 서비스가 누구에게 더 맞아졌나요? 운영하는 나의 하루는 어떻게 달라지나요?\n[내_서비스.md] 「만드는 방식」 칸에 까닭과 함께 적었습니다.\n\n여기서 멈추고 독자에게 묻습니다.')
    prog_add(f'방식 {k} {opt}'); return 0



# ---------------------------------------------------------------- 2장 변환: 다듬은 사이트를 다른 종류로(글자·색·짜임은 물려받고 기능 조합·메뉴만 갈아 끼움)
def convert_kinds():
    import kinds as KN
    D = json.load(open(os.path.join(HERE, 'demos', 'demos.json'), encoding='utf-8')); byk = {d['key']: d for d in D}
    out = {}
    def entry(kind, parts, d, labels, kd):
        return dict(parts=parts, name=(d or {}).get('name', ''), tagline=(d or {}).get('tagline', ''), kits_dir=(d or {}).get('kits_dir', ''), labels=labels, kind=kd, note=((d or {}).get('tagline') or '')[:40])
    for kind, cfg in KN.CFG.items():
        d = byk.get(cfg['demo']); out[kind] = entry(kind, cfg['parts'], d, cfg['labels'], kind)
    for k, v in KINDS.items():
        if k in out:
            continue
        key = {'정보 매거진': 'magazine', '도구 모음': 'tools', '가계부 앱': 'ledger'}.get(k)
        d = byk.get(key); out[k] = entry(k, v['parts'], d if key != 'magazine' else None, (d or {}).get('labels', {}), None)
    for d in D:
        nm = d['mix']
        if nm in out or d['key'] in ('magazine', 'tools', 'recipes', 'ledger', 'newsletter', 'shop'):
            continue
        ps = []
        for kk in d['kits']:
            kj = kit_json(kk)
            if kj and kj.get('parts'):
                ps += list(kj['parts'])
        out[nm] = entry(nm, sorted(set(ps + ['prefs'])), d, d.get('labels', {}), None)
    return out


def convert_cmd(rest):
    K = convert_kinds()
    if not rest:
        print('━━ 변환 — 다듬은 사이트를 다른 종류로 ━━\n[독자에게 말할 것] 1장에서 다듬은 글자·색·짜임은 그대로 물려받고, 기능 조합·메뉴 이름·첫 화면 구획·예시 내용만 그 종류에 맞게 갈아 끼웁니다. 같은 바탕에서 몇 분이면 다른 사이트가 됩니다.\n종류:'); [print(f'  - {k}  ({v["note"]})') for k, v in K.items()]
        print('\n사용: python run.py 변환 <종류> [--shots 폴더]  → 미리보기에서 멈춤 / 독자가 고르면 python run.py 고름 변환 바꿈 "<까닭>" 후 python run.py 변환 <종류> --적용 [--이름 "…" --소개 "…"] / python run.py 변환 되돌리기'); return 0
    if rest[0] == '되돌리기':
        prev = prog_load().get('convert_prev')
        if not prev:
            print('되돌릴 변환이 없습니다'); return 0
        pp = prev['parts']; allp = list(json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))['parts']); set_parts(allp, False); set_parts([p for p, v in pp.items() if v], True)
        d_ = local_load()
        for kk in ('kind', 'kits_dir', 'labels', 'name', 'tagline'):
            if prev.get(kk) in (None, '', {}):
                d_.pop(kk, None)
            else:
                d_[kk] = prev[kk]
        local_save(d_)
        out, last, rcb = rebuild_local(); d = prog_load(); d.pop('convert_prev', None); json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print(f'변환을 되돌렸습니다({last}).'); return 0
    w = ' '.join(rest).replace(' ', ''); kind = next((k for k in K if w == k.replace(' ', '') or (w and w in k.replace(' ', ''))), None)
    if not kind:
        print('그런 종류가 없습니다: ' + ' · '.join(K)); return 1
    E_ = K[kind]; apply_ = '--적용' in A
    base = dict(eff_parts()); pr = {p: False for p in base}
    for p in E_['parts']:
        pr[p] = True
    kd = os.path.join(HERE, E_['kits_dir']) if E_['kits_dir'] else ''
    print(f'━━ 변환 · {kind} ━━\n[상담: 먼저 물을 것] 지금 사이트를 「{kind}」로 바꾼다면 방문자는 누구이고, 무엇을 하러 오나요? 새 이름과 한 줄 소개는요? 돈은 어디서 나올 것 같나요? ({_ref_hint(kind)})')
    keep = ', '.join(f'{k}{v}' for k, v in sorted(cur_polish().items(), key=lambda x: int(x[0]))) or '없음(출발 모습)'
    off = [p for p, v in base.items() if v and not pr.get(p)]; on = [p for p, v in pr.items() if v and not base.get(p)]
    print(f'[그대로인 것] 다듬기 층({keep}) — 글자·색·제호 모양, 겉모습 틀\n[바뀌는 것] 켜지는 기능: {", ".join(on) or "없음"} / 꺼지는 기능: {", ".join(off) or "없음"} / 첫 화면 구획·메뉴 이름·예시 내용' + (f' / 예시 이름 「{E_["name"]}」(받기 전 임시, 「예시 이름」 표시)' if E_['name'] else ''))
    if not apply_:
        if SHOTS:
            import selftest as T
            env = {'SITE_NAME': (E_['name'] or '내 사이트') + ' (예시 이름)', 'SITE_TAGLINE': E_['tagline'], 'SITE_KIND': E_['kind'] or '', 'SITE_LABELS': json.dumps(E_['labels'], ensure_ascii=False)}
            if kd:
                env['KITS_DIR'] = kd
            out = build_tmp(None, pr, env); os.makedirs(SHOTS, exist_ok=True); n_ = kind.replace(' ', '')
            for nm_, w_, h_, mob in (('PC첫화면', 1280, 860, False), ('휴대폰', 390, 844, True)):
                fp = os.path.join(SHOTS, f'변환_{n_}_{nm_}.png')
                if T.shoot_pages(out, [''], [fp], w_, h_, mob):
                    print('  미리보기 저장:', fp, flush=True)
        print(f'\n[고를 것] 이 종류로 바꿀지 / 나중에 / 안 바꿈. 세션은 정하지 않고, 독자가 앞에서 한 말(내_서비스.md)에 비추어 어느 경우에 해당하는지만 짚어 줍니다.\n독자가 고르면 python run.py 고름 변환 바꿈 "{kind} 로 바꿔 보려는 까닭" → python run.py 변환 {kind} --적용 [--이름 "새 이름" --소개 "한 줄"]\n\n여기서 멈추고 독자에게 묻습니다.'); return 0
    if not need_choice('변환', '바꿈'):
        return 1
    import play; play.snap(f'변환 {kind}')
    t0 = time.time(); d = prog_load(); L = local_load()
    before_png = None
    if SHOTS:
        import selftest as T0
        os.makedirs(SHOTS, exist_ok=True); before_png = os.path.join(SHOTS, f'변환_{kind.replace(" ", "")}_전.png'); T0.shoot_pages(build_tmp(cur_polish()), [''], [before_png], 1280, 860)
    d['convert_prev'] = {'parts': base, 'kind': L.get('kind'), 'kits_dir': L.get('kits_dir'), 'labels': L.get('labels'), 'name': L.get('name'), 'tagline': L.get('tagline')}; json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    allp = list(base); set_parts(allp, False); set_parts(E_['parts'], True); L = local_load()
    L['kind'] = E_['kind'] or ''; L['kits_dir'] = E_['kits_dir']; L['labels'] = E_['labels']
    nm_ = A[A.index('--이름') + 1] if '--이름' in A and len(A) > A.index('--이름') + 1 else None; tg_ = A[A.index('--소개') + 1] if '--소개' in A and len(A) > A.index('--소개') + 1 else None
    L['name'] = nm_ or E_['name'] or L.get('name', '내 사이트'); L['tagline'] = tg_ or E_['tagline'] or L.get('tagline', '')
    if not L['kind']:
        L.pop('kind', None)
    if not L['labels']:
        L.pop('labels', None)
    if not L['kits_dir']:
        L.pop('kits_dir', None)
    local_save(L); out, last, rcb = rebuild_local()
    shots_for(out, '변환_' + kind.replace(' ', ''))
    if SHOTS and before_png and os.path.exists(before_png):
        import selftest as T1, base64, tempfile
        after_png = os.path.join(SHOTS, f'변환_{kind.replace(" ", "")}_후.png'); T1.shoot_pages(out, [''], [after_png], 1280, 860)
        br = T1.find_browser(); res = os.path.join(SHOTS, f'변환_{kind.replace(" ", "")}_전후.png')
        if br and os.path.exists(after_png):
            h_ = '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#222;color:#fff;font:16px "Malgun Gothic",sans-serif}div{display:flex;gap:12px;padding:12px}figure{margin:0;flex:1}img{width:100%;display:block;border:2px solid #fff}figcaption{padding:6px 0;font-weight:700}</style><div>'
            for cap, fp in (('바꾸기 전(바탕)', before_png), (f'바꾼 뒤 — {kind}', after_png)):
                h_ += f'<figure><figcaption>{cap}</figcaption><img src="data:image/png;base64,{base64.b64encode(open(fp, "rb").read()).decode()}"></figure>'
            hf = os.path.join(tempfile.mkdtemp(), 'c.html'); open(hf, 'w', encoding='utf-8').write(h_ + '</div>')
            subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=2600,1000', f'--screenshot={res}', 'file:///' + hf.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            print('  전·후 나란히:', res, flush=True)
    print(f'\n[방금 일어난 일] 「{kind}」로 바꿨습니다({last}) — 걸린 시간 {time.time() - t0:.0f}초. 되돌리려면 python run.py 변환 되돌리기')
    if not nm_:
        print(f'[알림] 이름은 예시 이름 「{L["name"]}」 그대로입니다. 독자에게 새 이름·소개를 받아 python run.py 변환 {kind} --적용 --이름 "…" --소개 "…" 로 다시 적용하거나 내서비스 칸에 정리하세요.')
    try:
        res = score_site(out); lines, ok_n, tot = grade_lines(res)
        bad = [l for l in lines if '✗' in l]
        print(f'[만듦새] 통과 {ok_n}/{tot}' + (' — 아직 다듬을 것:' if bad else ''))
        for l in bad:
            print(l)
    except Exception as e:
        print('(만듦새를 재지 못했습니다:', repr(e)[:60], ')')
    print('[다음 걸음] 내 주제의 내용으로 채우기(예시 자료 → 독자 자료) → 돈이 나올 자리 → 둘째 변환을 해 보거나 되돌리기. 독자의 말로 내_서비스.md 가 어떻게 바뀌는지 같이 봅니다.\n\n여기서 멈추고 독자에게 묻습니다.'); prog_add('변환 ' + kind); return 0


# ---------------------------------------------------------------- 3장 쉬는시간: 지금 사람이 볼 것만(올릴 묶음·정할 것·어긋난 것·어제 대비)
def break_cmd(rest):
    def cnt(d):
        p = os.path.join(HERE, d)
        return len([f for f in os.listdir(p) if not f.startswith('.')]) if os.path.isdir(p) else 0
    hh = time.localtime().tm_hour; part = '아침' if hh < 11 else ('점심' if hh < 17 else '저녁')
    print(f'━━ 쉬는시간 ({part}) — 지금 사람이 볼 것만 ━━')
    out = os.path.join(HERE, 'site_local')
    if not os.path.isdir(out):
        out, last, rcb = rebuild_local()
    nid = newest_note(out)
    print('① 올릴 묶음(만들어져 있고 아직 안 올린 것)')
    for d, ch in (('promo_out', '블로그·알림 문구'), ('cards', '공유 카드 그림'), ('shorts', '쇼츠 영상'), ('넘김', '다른 역할이 넘긴 파일')):
        print(f'   - {ch}: {cnt(d)}개 ({d}/)')
    print('② 정해야 하는 것(사람만 정함)')
    todo = []
    if cnt('promo_out'):
        todo.append('올릴까요? — 올릴 채널별 묶음을 보고 「올려」 한마디(올리기·로그인은 사람 몫)')
    ch = choices()
    later = [k for k, v in ch.items() if v['pick'] in ('나중에', '건너뜀')]
    if later:
        todo.append('미뤄 둔 선택: ' + ', '.join(later))
    print('   ' + ('\n   '.join('- ' + t for t in todo) if todo else '- 지금 정할 것이 없습니다'))
    print('③ 어긋난 것')
    rb = subprocess.run(PY + ['audit.py', '--dir', 'site_local'], cwd=HERE, env=dict(os.environ, SITE_BASE='/'), capture_output=True, text=True, encoding='utf-8', errors='replace'); print('   ' + (rb.stdout + rb.stderr).strip().splitlines()[-1][:120])
    mt = os.path.join(HERE, '만듦새.json')
    print('④ 어제 대비 바뀐 것')
    lg = os.path.join(HERE, 'logs', 'daily.md')
    print('   ' + (open(lg, encoding='utf-8').read().strip().splitlines()[-1][:120] if os.path.exists(lg) else '- 하루 한 바퀴 기록이 아직 없습니다(python run.py 사이클)'))
    print('\n[운영자 화면] 서버가 켜져 있으면 http://127.0.0.1:8080/admin/ (오늘 방문·새 댓글·문의), 꺼져 있으면 이 출력과 상태 쪽이 그 자리를 대신합니다.')
    prog_add('쉬는시간 ' + part); return 0


def open_cmd(rest):
    print('━━ 열기 — 먼저 한 바퀴(10분) ━━\n[방문자의 길] 첫 화면 → 글 → 관련 글 → 도구(계산기·용어) → 소식 받기\n[운영자의 하루] 새 소식 모으기 → 확인 노트 쓰기 → 올릴 묶음 만들기 → 쉬는시간에 정하기\n내 PC 에서 사이트를 엽니다(멈추려면 Ctrl+C). 열리면 독자와 이 길을 따라 걸으며 「누가 이 길로 오나요?」부터 묻습니다.', flush=True)
    if '--headless' in A:   # 창이 없는 조건: 찍기만 하고 여는 법만 알려 준 뒤 끝낸다(서버를 붙들고 있지 않는다)
        out, last, rc = rebuild_local(); print(f'사이트를 찍었습니다({last}). 여는 법: python serve.py --no-demo → http://127.0.0.1:8000/ (포트가 쓰이는 중이면 다음 번호)'); return rc
    return subprocess.run(PY + ['serve.py', '--open', '--no-demo'], cwd=HERE).returncode



def reference_cmd(rest):
    import refcmp as RC, selftest as T
    if rest and rest[0] == '바꾸기':
        if len(rest) < 2:
            print('사용: python run.py 레퍼런스 바꾸기 <이름>   (지금 있는 것: ' + ', '.join(RC.load()['refs']) + ')'); return 1
        print(RC.switch(' '.join(rest[1:]))); return 0
    if rest and rest[0] == '값':
        print(RC.set_values([a for a in A if '=' in a])); return 0
    out, last, rcb = rebuild_local(); nid = newest_note(out)
    lines, same, alln = RC.table(RC.ours(T, out, f'n/{nid}/' if nid else None))
    print('━━ 레퍼런스와 우리 사이트 — 차이표 ━━'); print('\n'.join(lines))
    print('\n레퍼런스를 바꾸려면: python run.py 레퍼런스 바꾸기 <이름> (값은 독자 세션이 그 사이트를 열어 재서 넣습니다 — 남의 사이트 화면은 저장소에 넣지 않습니다)')
    if SHOTS:
        _text_shot('레퍼런스와 우리 사이트 — 차이표', [('차이표', '\n'.join(lines))], '레퍼런스_차이표')
    return 0


def side_by_side(a, b, out, cap_a, cap_b):
    """그림 두 장을 나란히 붙인 한 장."""
    import selftest as T, base64, tempfile
    br = T.find_browser()
    if not (br and os.path.exists(a) and os.path.exists(b)):
        return
    h_ = '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#222;color:#fff;font:16px "Malgun Gothic",sans-serif}div{display:flex;gap:12px;padding:12px}figure{margin:0;flex:1}img{width:100%;display:block;border:2px solid #fff}figcaption{padding:6px 0;font-weight:700}</style><div>'
    for cap, fp in ((cap_a, a), (cap_b, b)):
        h_ += f'<figure><figcaption>{cap}</figcaption><img src="data:image/png;base64,{base64.b64encode(open(fp, "rb").read()).decode()}"></figure>'
    hf = os.path.join(tempfile.mkdtemp(), 'c.html'); open(hf, 'w', encoding='utf-8').write(h_ + '</div>')
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=2600,1000', f'--screenshot={out}', 'file:///' + hf.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    print('  전·후 나란히:', out, flush=True)


def find_demo(word):
    """조립 예시를 키(tools)·조합 이름(도구 모음)·사이트 이름(한입 도구함)으로 찾는다. 공백 무시, 하나로 좁혀질 때만."""
    D = json.load(open(os.path.join(HERE, 'demos', 'demos.json'), encoding='utf-8'))
    w = word.replace(' ', '')
    for f in (lambda d: [d['key']], lambda d: [d['mix'], d['name']]):
        hit = [d for d in D if w in [x.replace(' ', '') for x in f(d)]]
        if len(hit) == 1:
            return hit[0]
    hit = [d for d in D if w and any(w in x.replace(' ', '') for x in (d['key'], d['mix'], d['name']))]
    return hit[0] if len(hit) == 1 else None


def one_kit(name):
    sys.path.insert(0, HERE)
    import selftest as T
    k = T.resolve(name)
    if not k:
        print(f'「{name}」 키트를 찾지 못했습니다. 목록: python run.py 키트'); return 1
    print(f'━━ {k.get("title", k["name"])} ━━')
    print('① 꼭 알아야 할 것(위에서부터 3가지)')
    mk = (kit_json(k['name']) or {}).get('must_know') or []
    for m_ in mk[:3]:
        print('  -', m_.get('알것', ''))
        if '--풀이' in A:
            print('    까닭:', m_.get('까닭', ''), '/ 모르면:', m_.get('모르면', ''), '/ 근거:', m_.get('근거', ''))
    print('확인 물음(스스로 답해 보세요 — 답은 독자가 먼저 말하게 합니다):')
    for qi, m_ in enumerate(mk[:3], 1):
        print(f'  Q{qi}. 「{m_.get("알것", "")[:40]}」 — 모르면 어떤 일이 생길까요?')
    print('② 보는 앞에서 스스로 시험'); rc = sh(['selftest.py', k['name']] + FLAGS)
    ex = os.path.join(HERE, 'kits', k['name'], '설명.md')
    if os.path.exists(ex):
        print(f'③ 설명 뼈대: kits/{k["name"]}/설명.md (에이전트가 독자 눈높이로 풀어 설명할 것)')
    if k.get('try_change'):
        print('④ 바꿔 보기 제안:', k['try_change'])
    print(f'⑤ 내 PC 에서 직접 열려면: python mix.py --add {k["name"]}  →  python serve.py --open')
    note = ''
    if rc != 0:
        dirty = subprocess.run(['git', 'status', '--porcelain', 'kits/' + k['name']], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if dirty:
            note = '(바꾼 자료 때문)'
            print('※ 이 키트의 자료를 바꾸셨습니다. 자가 시험은 예시 값(기본 자료)을 기준으로 하므로, 바꾼 뒤의 ✗ 는 고장이 아니라 「예시 값과 달라서」 나오는 것입니다. 바꾼 값으로 화면이 열리는지는 python serve.py --open 으로 직접 확인하세요.')
    prog_add(f'키트 {k["name"]} 실습' + ('' if rc == 0 else '(시험에 실패한 단계 있음' + note + ')'))
    return rc


def main():
    if not POS:
        print(__doc__); return 0
    cmd, rest = POS[0], POS[1:]
    if cmd in ('시작', 'start'):
        rc = sh(['doctor.py', '--quick'])   # 환경 점검도 doctor 가 맨 앞에서 한다
        prog_add('시작(환경·키트 점검)'); print('\n다음: python run.py 키트 계산기  /  python run.py 조립  /  python run.py 사이클'); return rc
    if cmd in ('점검', 'doctor'):
        return sh(['doctor.py'] + (['--quick'] if '--quick' in A else []))
    if cmd in ('키트', 'kit'):
        if not rest:
            K = kits(); print('키트(자가 시험이 있는 것에 ✓):'); [print(f'  {"✓" if k.get("selftest") else " "} {n:20} {k["title"]}') for n, k in K.items()]
            print('\n사용: python run.py 키트 계산기  ·  python run.py 키트 전부'); return 0
        if rest[0] == '전부':
            rc = 0; n = 0
            for k in kits().values():
                if k.get('selftest'):
                    rc |= one_kit(k['name']); n += 1
            print(f'\n키트 {n}개 실습 끝. 점검표: python run.py 점검'); return rc
        return one_kit(rest[0])
    if cmd in ('섞기', 'mix'):
        if not rest:
            print('사용: python run.py 섞기 계산기 용어 게임'); return 1
        sys.path.insert(0, HERE); import selftest as T
        names = []   # 키트 이름 + 조립 예시 이름(「도구함+동네정보」처럼 +로 이으면 예시들의 키트를 합친다)
        for r in rest:
            for w in r.split('+'):
                d = find_demo(w); k = T.resolve(w)
                got = k['name'] if k else None
                for n in ([got] if got else (d['kits'] if d else [w])):
                    if n not in names:
                        names.append(n)
        print('켜는 키트:', ' '.join(names))
        sh(['mix.py'] + names); out = os.path.join(HERE, 'site_local')
        env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=out)
        r = subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace'); print((r.stdout.strip().splitlines() or [''])[-1])
        rc = sh(['selftest.py', '--tour', out, '섞은 사이트(' + ' + '.join(rest) + ')'] + FLAGS)
        print('내 PC 에서 직접 열려면: python serve.py --open'); prog_add('섞기 ' + ' '.join(rest)); return rc
    if cmd in ('조립', 'assemble'):
        D = json.load(open(os.path.join(HERE, 'demos', 'demos.json'), encoding='utf-8'))
        if not rest:
            print('조립 예시:'); [print(f'  {d["key"]:12} {d["name"]} — {d["tagline"][:50]}') for d in D]; print('\n사용: python run.py 조립 <이름>'); return 0
        d0 = find_demo(' '.join(rest))
        if not d0:
            print('조립 예시를 찾지 못했습니다. 목록: python run.py 조립 (이름은 도구함·동네 정보처럼 한글도 됩니다)'); return 1
        rest = [d0['key']]
        out = os.path.join(HERE, 'site_demo_' + rest[0])
        if sh(['demo.py', '--only', rest[0], '--out', out]) != 0:
            return 1
        rc = sh(['selftest.py', '--tour', out, '조립 예시 ' + rest[0]] + FLAGS)
        print(f'내 PC 에서 직접 열려면: python -m http.server --directory site_demo_{rest[0]} 또는 python serve.py (조립 예시 목록 /demo/)'); prog_add('조립 ' + rest[0]); return rc
    if cmd in ('사이클', 'cycle'):
        print('━━ 하루 한 바퀴(올리기·메일 제외) ━━', flush=True)
        steps = [('수집·묶기·대조·화면·호·쇼츠', ['run_daily.py'], '수집 건수·묶음·대조 결과·쪽 수·호 PDF·쇼츠는 위 출력의 단계별 줄'), ('알림 문구·블로그 글(promo)', ['promo.py'], 'promo_out/ 폴더'), ('공유용 카드 그림', ['card.py', '--square'], 'cards/ 폴더(png·svg)'), ('점검(audit)', ['audit.py'], '아래 점검 결과 줄')]
        for i, (t, a, where) in enumerate(steps, 1):
            print(f'\n[{i}/{len(steps)}] {t} — {time.strftime("%H:%M:%S")}  (결과는 {where})', flush=True)
            if i in (2, 3) and not info_on():
                print('  건너뜀: 이 사이트는 뉴스 기능이 꺼져 있어 확인 노트가 없습니다(알림 문구·카드는 노트로 만듭니다).', flush=True); continue
            if i == 4:
                r4 = subprocess.run(PY + a, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace'); print(r4.stdout + r4.stderr, flush=True); LAST_OUT[4] = r4.stdout + r4.stderr
            else:
                sh(a)
            sys.stdout.flush()
            if SHOTS:
                cycle_shot(i, t, a[0])
        if any(eff_parts().get(k) for k in ('board', 'market', 'trend')):   # 방문자가 남긴 것을 받는 사이트: 오늘 사람이 볼 것
            print('\n[덧붙임] 운영자의 하루 일', flush=True); sh(['ops.py'])
        print('\n올릴 묶음(만들어져 있는 것, 아직 올리지 않았습니다):', flush=True)
        for d, what in (('promo_out', '알림 문구·블로그 글'), ('cards', '공유용 카드 그림'), ('shorts', '쇼츠 영상'), ('넘김', '역할끼리 넘긴 파일')):
            p = os.path.join(HERE, d)
            n = len([f for f in os.listdir(p) if not f.startswith('.')]) if os.path.isdir(p) else 0
            print(f'  - {d}/ ({what}): {n}개', flush=True)
        print('\n여기서 사람이 올립니다: 블로그·영상·인스타에 올리기와 소식지 메일 발송은 사람 승인 후에(이 사이클은 올리지 않았습니다). 결과 화면은 python serve.py --open 으로 열어 볼 수 있습니다.', flush=True)
        prog_add('사이클 한 바퀴(예행)'); return 0
    if cmd in ('올리기전', 'precheck'):
        import ast
        bad = 0
        for f in sorted(glob.glob(os.path.join(HERE, '*.py'))):
            try:
                ast.parse(open(f, encoding='utf-8').read())
            except SyntaxError as e:
                bad += 1; print(f'✗ 구문 오류 {os.path.basename(f)} {e.lineno}행: {e.msg}')
        print('구문 검사:', '모두 통과' if not bad else f'{bad}개 파일에 오류')
        for t in (['장', '1'], ['장', '2'], ['장', '3'], ['진도'], ['키트'], ['조립'], ['알기', '계산기', '1'], ['키트', '계산기', '--headless', '--slow', '0.1'], ['조립', 'tools', '--headless', '--slow', '0.1']):
            r = subprocess.run(PY + ['run.py'] + t, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
            ok = r.returncode == 0 and 'Traceback' not in r.stderr and '없습니다' not in r.stdout.split(chr(10))[0]
            bad += 0 if ok else 1; print(('✓' if ok else '✗'), 'run.py ' + ' '.join(t))
        r = subprocess.run(PY + ['run_daily.py', '--dry'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace'); ok = r.returncode == 0
        bad += 0 if ok else 1; print(('✓' if ok else '✗'), 'run_daily.py --dry')
        print(chr(10) + '올려도 됩니다' if not bad else chr(10) + f'올리지 마세요: {bad}건 실패'); return 1 if bad else 0
    if cmd in ('예제정리', 'cleanup'):
        import re as _re, shutil
        nd = os.path.join(HERE, 'notes'); ex = os.path.join(HERE, '예제')
        fs = [f for f in sorted(os.listdir(nd)) if _re.match(r'\d{4}-\d{2}-\d{2}-', f)] if os.path.isdir(nd) else []
        print('옮길 예제 노트(날짜로 시작하는 작성자의 노트):', len(fs), '개  ※ 예시-수출.json 은 화면 시험용이라 그대로 둡니다')
        for f in fs[:8]:
            print('  -', f)
        if '--yes' in A:
            os.makedirs(ex, exist_ok=True)
            for f in fs:
                shutil.move(os.path.join(nd, f), os.path.join(ex, f))
            print('예제/ 로 옮겼습니다(지우지 않았습니다).'); prog_add('예제 노트를 예제/ 로 옮김')
        else:
            print('옮기려면 독자에게 먼저 묻고: python run.py 예제정리 --yes')
        return 0
    if cmd in ('켜기', 'on'):
        return toggle(rest, True)
    if cmd in ('끄기', 'off'):
        return toggle(rest, False)
    if cmd in ('지금', 'now'):
        now_list(); return 0
    if cmd in ('묶음', 'group'):
        G = gload()['groups']
        if not rest:
            print('기능 지도의 여덟 묶음:'); [print(f'  {i}. {g["name"]} ({len(g["kits"])}개) — {g["intro"][:40]}') for i, g in enumerate(G, 1)]
            print('\n사용: python run.py 묶음 도구와자료  (또는 번호)'); return 0
        g = group_find(' '.join(rest))
        if not g:
            print('묶음을 찾지 못했습니다: python run.py 묶음'); return 1
        return run_group(g, FLAGS or ['--headless'])
    if cmd in ('전부', 'all'):
        if '--예' not in A:
            print('이 장은 고르면서 가는 장입니다. 그래도 한꺼번에 할까요? (독자가 예라고 한 뒤에만: python run.py 전부 --예)'); return 1
        return all_cmd()
    if cmd in ('독자', 'reader'):
        return reader_cmd(rest)
    if cmd in ('복습', 'review'):
        return review_cmd()
    if cmd in ('혼동', 'confused'):
        return confuse_cmd(rest)
    if cmd in ('변환', 'convert'):
        return convert_cmd(rest)
    if cmd in ('쉬는시간', 'break'):
        return break_cmd(rest)
    if cmd in ('열기', 'open'):
        return open_cmd(rest)
    if cmd in ('맺음', 'wrapup'):
        return wrap_up_cmd()
    if cmd in ('나누기', 'split'):
        import play; return play.split_cmd(sys.modules[__name__], rest)
    if cmd in ('운영', 'ops'):
        return sh(['ops.py'] + rest)
    if cmd in ('조각', 'piece'):
        import play as PLY
        return PLY.piece_cmd(sys.modules[__name__], POS[1:])
    if cmd in ('분류', 'cats'):
        import play as PLY
        return PLY.cats_cmd(sys.modules[__name__], POS[1:])
    if cmd in ('손잡이', 'knob'):
        import play; return play.knob_cmd(sys.modules[__name__], rest)
    if cmd in ('준비', 'setup'):
        return sh(['setup.py'] + A[1:])
    if cmd in ('데이터', 'data'):
        return sh(['data.py'] + A[1:])
    if cmd in ('메일', 'mail'):
        return sh(['mail.py'] + [x for x in A[1:] if x != '미리보기'])
    if cmd in ('올려', 'deploy'):
        rc = sh(['shop.py', '공유'] + A[2:]) if rest and rest[0] == '가게' else sh(['deploy.py'] + A[1:])
        if rc == 0 and (not rest or rest[0] == '가게'):
            import play; play.status_cmd(sys.modules[__name__])
        return rc
    if cmd in ('가게', 'shop'):
        rc = sh(['shop.py'] + A[1:])
        if rc == 0 and rest and rest[0] == '켜기':
            import play; prog_add('본 가게'); play.status_cmd(sys.modules[__name__])
        return rc
    if cmd in ('붙여', '떼', '기능'):
        rc = sh(['shop.py'] + A)
        if rc == 0 and cmd != '기능' and rest:
            prog_add(f'바꿈: 기능 {rest[0]} {"붙임" if cmd == "붙여" else "뗌"}')
        return rc
    if cmd in ('운영기록', 'archive'):
        return sh(['archive.py'] + A[1:])
    if cmd in ('토큰', 'token'):
        return sh(['lms.py'] + A[1:])
    if cmd in ('상태창', 'status'):
        import play; return play.status_cmd(sys.modules[__name__], rest)
    if cmd in ('자동', 'auto'):
        rc = sh(['auto.py'] + A[1:])
        if rc == 0 and rest and not ('예약' in rest and '--예' not in A) and '상태' not in rest:
            import play; prog_add('자동 ' + ' '.join(rest[:2])); play.status_cmd(sys.modules[__name__])
        return rc
    if cmd in ('본', '원본', 'mirror'):
        import play; return play.mirror_cmd(sys.modules[__name__], rest)
    if cmd in ('바꿔', 'change'):
        import play; return play.change_cmd(sys.modules[__name__], rest)
    if cmd in ('바꿨다', 'changed'):
        import play; return play.changed_cmd(sys.modules[__name__], rest)
    if cmd in ('레퍼런스', 'reference'):
        return reference_cmd(rest)
    if cmd in ('방식', 'way'):
        return ways_cmd(rest)
    if cmd in ('내서비스', 'mysvc'):
        return service_card_cmd(rest)
    if cmd in ('고름', 'pick'):
        return choose_cmd(rest)
    if cmd in ('고른것', 'chosen'):
        return chosen_cmd()
    if cmd in ('미룬것', 'deferred'):
        return deferred_cmd()
    if cmd in ('도커', 'docker'):
        return docker_cmd(rest)
    if cmd in ('서버', 'server'):
        return server_cmd(rest)
    if cmd in ('자료', 'docs'):
        return docs_cmd(rest)
    if cmd in ('실험', 'lab'):
        return lab_cmd(rest)
    if cmd in ('내놓기', 'release'):
        return release_cmd(rest)
    if cmd in ('다듬기', 'polish'):
        return polish_cmd(rest)
    if cmd in ('되돌리기', 'undo'):
        return undo_cmd(rest)
    if cmd in ('만듦새', 'quality'):
        return quality_cmd()
    if cmd in ('비교', 'compare'):
        return compare_cmd(rest)
    if cmd in ('생각', 'think'):
        return think_cmd()
    if cmd in ('정리', 'organize'):
        return organize_cmd(rest)
    if cmd in ('참고', 'ref'):
        return ref_cmd(rest)
    if cmd in ('기획서', 'plan'):
        return plan_cmd()
    if cmd in ('서비스', 'service'):
        return service_cmd(rest)
    if cmd in ('알기', 'know'):
        return sh(['know.py'] + rest)
    if cmd in ('진도', 'progress'):
        if rest and rest[0] == '기록':
            prog_add(' '.join(rest[1:]) or '진행'); print('기록했습니다'); return 0
        d = prog_load(); print('마지막:', d['last'] or '(없음)')
        for x in d['done'][-12:]:
            print(' ', x['t'], x['what'])
        return 0
    if cmd in ('장', 'chapter'):
        n = rest[0] if rest else '1'
        p = os.path.join(HERE, '코스', f'{n}장.md'); print(p if os.path.exists(p) else f'코스/{n}장.md 가 없습니다'); return 0
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())
