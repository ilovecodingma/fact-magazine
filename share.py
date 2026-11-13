# -*- coding: utf-8 -*-
"""프로젝트 공유: 독자가 「올려」 한 프로젝트 소개 글을 수업 사이트에 올린다(기본은 나만 보기). 파이썬 기본 기능만 쓴다.
python run.py 공유 올리기 <초안.json> [--공개] [--예]   올라갈 글을 그대로 보여 주고, --예 가 있을 때만 올린다. --공개 는 공개 신청(운영자가 확인한 뒤 공개)
python run.py 공유 내글                                  내가 올린 글 목록(나만 보기 포함)
python run.py 공유 수정 <글 id> <초안.json> [--예]        고쳐 올린다
python run.py 공유 삭제 <글 id> [--예]                    내 글을 지운다
초안.json 의 칸: title(4자 이상) what(무엇을 만들었나, 20자 이상) why tools success(성공 기준) problem solution learned link image nick
소스코드·작업 로그 원문 칸은 없다. 이름·메일·전화·파일 경로·토큰·손님 정보는 넣지 않는다. link·image 는 독자가 직접 말한 주소만(http·https) 넣는다.
토큰이 있어야 한다(`run.py 토큰`). 지침은 참고/공유_쓰는법.md."""
import json, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cases  # 서버 호출·토큰·개인 값 검사를 같이 쓴다

A = sys.argv[1:]
FIELDS = ('title', 'what', 'why', 'tools', 'success', 'problem', 'solution', 'learned', 'link', 'image', 'nick')
LABEL = {'title': '제목', 'what': '무엇을 만들었나', 'why': '왜', 'tools': '쓴 도구·환경', 'success': '내가 정한 성공 기준', 'problem': '겪은 문제', 'solution': '어떻게 풀었나', 'learned': '배운 것·다음에 할 것', 'link': '결과물 주소', 'image': '그림 주소', 'nick': '별명'}


def load(fp):
    if not fp or not os.path.exists(fp):
        print('초안 파일이 없습니다: ' + str(fp)); sys.exit(1)
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        print('초안 파일을 읽지 못했습니다(JSON 이 아님).'); sys.exit(1)
    return {k: str(d.get(k) or '').strip() for k in FIELDS}


def show(d, scope):
    print('━━ 수업 사이트에 올라갈 프로젝트 공유 (이 그대로 올라갑니다) ━━')
    for k in FIELDS:
        if d.get(k):
            print(f'{LABEL[k]}: {d[k]}')
    print('공개 범위: ' + ('공개 신청(운영자가 확인한 뒤 공개됩니다)' if scope == 'public' else '나만 보기(올린 사람만 봅니다)'))
    print('─' * 40)


def check(d):
    bad = cases.private('\n'.join(d[k] for k in FIELDS if k not in ('link', 'image')))
    if bad:
        print('✗ 올리지 않았습니다 — 글에 ' + ', '.join(bad) + ' 이(가) 들어 있습니다. 빼고 다시(결과물 주소는 link 칸에 독자가 말한 것만).'); return False
    for k in ('link', 'image'):
        if d[k] and not d[k].lower().startswith(('http://', 'https://')):
            print(f'✗ {LABEL[k]}는 http 또는 https 주소여야 합니다.'); return False
    if len(d['title']) < 4:
        print('✗ 제목은 4자 이상이어야 합니다.'); return False
    if len(d['what']) < 20:
        print(f'✗ 「무엇을 만들었나」는 20자 이상이어야 합니다(지금 {len(d["what"])}자).'); return False
    return True


def main():
    c = A[0] if A else ''
    tk = cases._token()
    if c in ('올리기', '수정', '삭제', '내글') and not tk:
        print('✗ 토큰이 없습니다. 독자가 「토큰 발급해 줘」 하면 python run.py 토큰'); return 1
    yes = '--예' in A; scope = 'public' if '--공개' in A else 'private'
    args = [a for a in A[1:] if not a.startswith('--')]
    if c == '올리기' or c == '수정':
        if c == '수정' and len(args) < 2:
            print('사용: python run.py 공유 수정 <글 id> <초안.json> [--예]'); return 1
        d = load(args[1] if c == '수정' else (args[0] if args else None))
        show(d, scope)
        if not check(d):
            return 1
        if not yes:
            print('아직 올리지 않았습니다. 독자에게 위 글을 그대로 보여 주고 「올려」라고 하면 같은 줄에 --예 를 붙여 다시 부릅니다.'); return 0
        body = dict({k: v for k, v in d.items() if v}, token=tk, scope=scope)
        if c == '수정':
            body['id'] = args[0]
        r = cases._call('POST', '/lms/share/update' if c == '수정' else '/lms/share', body)
        if r.get('ok') is False or r.get('_code'):
            print(f'✗ 올리지 못했습니다({r.get("_code", "")} {r.get("error", "")}).'); return 1
        st = r.get('status', '')
        print(f'✓ {"고쳤습니다" if c == "수정" else "올렸습니다"}(글 번호 {r.get("id", args[0] if c == "수정" else "")}) — ' + ('나만 보기로 저장되었습니다. 공개하려면 독자가 원할 때 --공개 로 다시 올립니다.' if st == 'private' else '공개 신청이 접수되었습니다. 운영자가 확인한 뒤 https://sungprofile.cloud/park/share/ 에 공개됩니다.' if st == 'pending' else f'상태: {st}'))
        return 0
    if c == '내글':
        r = cases._call('POST', '/lms/share/mine', {'token': tk})
        if r.get('_code') or r.get('ok') is False:
            print('✗ 내 글을 읽지 못했습니다.'); return 1
        L = r.get('shares') or r.get('items') or r.get('mine') or []
        print(f'내가 올린 글 {len(L)}개')
        for s in L:
            print(f'  [{s.get("id")}] {s.get("title", "")} — {s.get("status", "")}')
        return 0
    if c == '삭제':
        if not args:
            print('사용: python run.py 공유 삭제 <글 id> [--예]'); return 1
        if not yes:
            print(f'글 {args[0]} 을(를) 지웁니다. 독자가 지워도 된다고 한 뒤에 --예 를 붙여 다시 부릅니다.'); return 0
        r = cases._call('POST', '/lms/share/delete', {'token': tk, 'id': args[0]})
        print('✓ 지웠습니다.' if r.get('ok') else f'✗ 지우지 못했습니다({r.get("_code", "")} {r.get("error", "")}).')
        return 0 if r.get('ok') else 1
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main())
