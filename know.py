# -*- coding: utf-8 -*-
"""꼭 알아야 할 것(top-k): 키트마다 kit.json 의 must_know 를 중요한 순서대로 위에서부터 k개 보여 준다. 근거 없는 일반 상식은 맨 뒤에 「일반」으로 표시한다.
사용: python know.py 계산기                 키트 이름으로(이름의 일부여도 됨) 위에서 5개
      python know.py calc 3                 3개
      python know.py 하네스                 저장소 전체에서 꼭 알아야 할 것(know/harness.json)
      python know.py --all 3               must_know 가 있는 모든 키트의 위 3개씩
      python know.py                       must_know 가 있는 키트 목록
항목 모양: {알것, 까닭, 모르면, 근거}. 근거는 이 저장소의 파일·기록(오늘 실제로 겪거나 코드가 그렇게 동작하는 것)이고, 근거가 「일반」이면 맨 뒤로 보낸다."""
import glob, json, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    out = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json'))):
        k = json.load(open(p, encoding='utf-8'))
        if k.get('must_know'):
            out[k['name']] = k
    hp = os.path.join(HERE, 'know', 'harness.json')
    if os.path.exists(hp):
        h = json.load(open(hp, encoding='utf-8')); out['하네스'] = h
    return out


def ordered(items):
    """근거가 있는 것을 앞에(원래 중요한 순서 유지), 「일반」은 맨 뒤로."""
    return [i for i in items if i.get('근거') != '일반'] + [i for i in items if i.get('근거') == '일반']


def show(k, n):
    items = ordered(k['must_know'])[:n]
    print(f'■ {k.get("title", k["name"])} — 꼭 알아야 할 것 {len(items)}가지 (중요한 순서)')
    for i, it in enumerate(items, 1):
        gen = '  [일반 — 이 저장소에 근거 없음]' if it.get('근거') == '일반' else ''
        print(f'{i}. {it["알것"]}{gen}\n   까닭: {it["까닭"]}\n   모르면: {it["모르면"]}\n   근거: {it["근거"]}')
    print('확인 물음(스스로 답해 보세요):')
    for i, it in enumerate(items[:3], 1):
        print(f'  Q{i}. 「{it["알것"][:30]}…」 — 모르면 어떤 일이 생길까요?')
    print()


def main():
    a = [x for x in sys.argv[1:]]
    K = load()
    if not a:
        print('must_know 가 있는 키트:', ', '.join(K)); print('사용: python know.py 키트이름 [k] · python know.py 하네스 · python know.py --all 3'); return
    if a[0] == '--all':
        n = int(a[1]) if len(a) > 1 and a[1].isdigit() else 3
        for k in K.values():
            show(k, n)
        return
    q = a[0]
    n = int(a[1]) if len(a) > 1 and a[1].isdigit() else 5
    alias = {'계산기': 'calc', '용어': 'glossary', '검색': 'search', '상태': 'status', '전자책': 'ebook', '게임': 'games', '쇼츠': 'shorts', '잡지': 'issue', '메일': 'mail', '확인 노트': 'news', '확인노트': 'news', '노트': 'news', '뉴스': 'news', '카드': 'cards', '퀴즈': 'quiz', '일정': 'schedule', '인기 키워드': 'trends'}
    key = alias.get(q, q)
    hit = K.get(key) or next((v for kk, v in K.items() if key in kk or key in v.get('title', '')), None)
    if not hit:
        sys.exit(f'「{q}」 의 must_know 가 없습니다. 있는 키트: ' + ', '.join(K))
    show(hit, n)


if __name__ == '__main__':
    main()
