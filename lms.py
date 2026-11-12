# -*- coding: utf-8 -*-
"""학습 사이트 잇기(선택): 토큰을 받아 두면 관문이 열릴 때마다 「어디까지 했는지」만 학습 사이트에 알린다. 파이썬 기본 기능만 쓴다.
python run.py 토큰          토큰이 없으면 받아서 site.local.json 에 적고(이 파일은 git 에 올라가지 않는다), 토큰과 넣을 주소를 보여 준다
python run.py 토큰 끄기     토큰을 지운다(그 뒤로 아무것도 보내지 않는다)
보내는 것은 토큰과 단계 이름(예: ch1.made), 만든 것의 종류(글·가게) 뿐이다. 이름·메일·주소·파일 경로·사이트 주소는 보내지 않는다.
토큰이 없으면 아무것도 보내지 않는다. 학습 사이트가 응답하지 않아도 실습은 멈추지 않는다."""
import json, os, sys, time, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
API = os.environ.get('LMS_API', 'https://jupjup-lms.sung2011103.workers.dev').rstrip('/')
PAGE = 'https://sungprofile.cloud/park/start/'
LOCAL = os.path.join(HERE, 'site.local.json'); PROG = os.path.join(HERE, '진도.json')


def _load(fp, default):
    try:
        return json.load(open(fp, encoding='utf-8'))
    except Exception:
        return default


def _save(fp, d):
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def _post(path, body, timeout=8):
    try:
        req = urllib.request.Request(API + path, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'fact-magazine-harness/1'}, method='POST')
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
    except Exception:
        return None


def token():
    return (_load(LOCAL, {}).get('lms_token') or '').strip()


def steps():
    """진도.json 에 적힌 것에서 지금까지 열린 단계를 고른다(잰 것만)."""
    d = _load(PROG, {}); done = [x.get('what', '') for x in d.get('done', [])]
    out = [('start', '')]
    made = [w[2:].strip() for w in done if w.startswith('본 ')]
    ups = [w for w in done if w.startswith('올림: ')]
    if '글' in made:
        out.append(('ch1.made', '글 사이트'))
    if any('trycloudflare' not in w for w in ups):
        out.append(('ch1.uploaded', ''))
    if sum(1 for w in done if w.startswith('바꿈: ') and not w.startswith('바꿈: 기능 ')) >= 3:
        out.append(('ch1.changed', ''))
    if '가게' in made:
        out.append(('ch2.made', '가게'))
    if any('trycloudflare' in w for w in ups):
        out.append(('ch2.uploaded', ''))
    if any(w.startswith('바꿈: 기능 ') for w in done):
        out.append(('ch2.changed', ''))
    if any(w.startswith('자동 ') and '맛보기' in w for w in done):
        out.append(('ch3.ops', ''))
    return out


def sync(quiet=True):
    """토큰이 있을 때만, 아직 알리지 않은 단계를 알린다. 실패하면 조용히 넘어가고 다음에 다시 보낸다."""
    tk = token()
    if not tk:
        return 0
    d = _load(PROG, {'done': [], 'last': ''}); sent = set(d.get('lms_sent') or []); n = 0
    for step, note in steps():
        if step in sent:
            continue
        r = _post('/lms/progress', {'token': tk, 'step': step, 'note': note}, timeout=5)
        if not (r and r.get('ok')):
            break
        sent.add(step); n += 1
    if n:
        d = _load(PROG, {'done': [], 'last': ''}); d['lms_sent'] = sorted(sent); _save(PROG, d)
        if not quiet:
            print(f'학습 사이트에 진도 {n}단계를 알렸습니다.')
    return n


def main():
    A = sys.argv[1:]
    L = _load(LOCAL, {})
    if A and A[0] in ('끄기', '지우기'):
        if L.pop('lms_token', None):
            _save(LOCAL, L)
        d = _load(PROG, None)
        if d and d.pop('lms_sent', None) is not None:
            _save(PROG, d)
        print('토큰을 지웠습니다. 이제 학습 사이트에 아무것도 보내지 않습니다.'); return 0
    tk = token()
    if not tk:
        r = _post('/lms/issue', {}, timeout=15)
        if not (r and r.get('ok') and r.get('token')):
            print('✗ 지금은 토큰을 받지 못했습니다(학습 사이트가 응답하지 않습니다). 실습은 토큰 없이도 그대로 됩니다 — 나중에 다시 「토큰 발급해 줘」.'); return 1
        tk = r['token']; L['lms_token'] = tk; _save(LOCAL, L)
        print('✓ 토큰을 받았습니다.')
    else:
        print('이미 받은 토큰이 있습니다.')
    print(f'토큰: {tk}')
    print(f'넣을 곳: {PAGE}  — 열어서 토큰을 넣으면 지금 진도에 맞는 보기와 「다음에 할 말」이 나옵니다.')
    print('보내는 것은 토큰과 어디까지 했는지(단계 이름·만든 것의 종류)뿐입니다. 이름·메일·주소는 보내지 않습니다. 끄려면 python run.py 토큰 끄기')
    sync(quiet=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
