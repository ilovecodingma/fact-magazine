# -*- coding: utf-8 -*-
"""2단계 묶기: 여러 매체가 함께 다룬 소식을 한 묶음으로 만든다 (data/items.json -> data/topics.json).
방법은 단순하다. 제목에서 두 글자 이상 낱말(숫자 포함)을 뽑고, 낱말이 충분히 겹치는 제목끼리 같은 묶음으로 본다.
묶음에 서로 다른 매체가 MIN_SOURCES 곳 이상 들어 있어야 「함께 다룬 소식」이다.  실행: python group.py"""
import json, os, re, datetime
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')   # 윈도우에서 한글 출력이 깨지지 않게
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
def _min_sources():
    """몇 개 매체가 다룬 묶음부터 남길지. 환경변수 MIN_SOURCES > site.json 의 min_sources > 3. 주제에 맞는 묶음이 0건이면 2로 낮춰 본다(런북 6절)."""
    try:
        return int(os.environ.get('MIN_SOURCES') or json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8')).get('min_sources', 3))
    except Exception:
        return 3


MIN_SOURCES = _min_sources()      # 이 수 이상의 매체가 다룬 묶음만 남긴다
MIN_SHARED = 2       # 묶음에 들어가려면 씨앗 기사와 겹치는 낱말이 최소 몇 개
MIN_RATIO = 0.4      # 그리고 짧은 쪽 제목 낱말의 이만큼 이상이 겹쳐야 한다
STOP = set('속보 단독 종합 포토 사진 영상 오늘 내일 이후 관련 대한 위해 통해 따른 있는 없는 하는 한다 했다 된다 예정 전망 가능 이번 지난 올해 내년 최대 최소 확대 추진 발표 정부 시장'.split())


def words(title):
    """제목에서 비교용 낱말 집합. 조사 한 글자는 떼고, 불용어는 버린다."""
    ws = set()
    for w in re.findall(r'[0-9A-Za-z가-힣%.]+', title):
        w = re.sub(r'(은|는|이|가|을|를|의|에|도|로|과|와)$', '', w) if len(w) > 2 else w
        if len(w) >= 2 and w not in STOP:
            ws.add(w)
    return ws


def main():
    data = json.load(open(os.path.join(HERE, 'data', 'items.json'), encoding='utf-8'))
    items = data['items']
    for x in items:
        x['w'] = words(x['title'])
    groups = []   # 각 묶음: {'words': 묶음 낱말 합집합, 'items': [...]}
    for x in items:
        best, best_n = None, 0
        for g in groups:
            n = len(x['w'] & g['seed'])   # 묶음의 첫 기사(씨앗)와만 비교한다 — 합집합과 비교하면 묶음이 점점 번져 다른 소식이 섞인다
            if n >= MIN_SHARED and n / min(len(x['w']), len(g['seed'])) >= MIN_RATIO and n > best_n:
                best, best_n = g, n
        if best:
            best['items'].append(x)
        else:
            groups.append({'seed': set(x['w']), 'items': [x]})
    topics = []
    for g in groups:
        srcs = sorted({y['source'] for y in g['items']})
        if len(srcs) < MIN_SOURCES:
            continue
        rep = max(g['items'], key=lambda y: sum(len(y['w'] & z['w']) for z in g['items'] if z is not y))   # 다른 기사들과 가장 많이 겹치는 제목을 대표로
        topics.append({'title': rep['title'], 'media_count': len(srcs), 'media': srcs,
                       'latest': max(y['time'] for y in g['items']),
                       'items': [{k: y[k] for k in ('source', 'title', 'link', 'time')} for y in sorted(g['items'], key=lambda y: y['time'], reverse=True)]})
    topics.sort(key=lambda t: (-t['media_count'], t['latest']), reverse=False)
    topics.sort(key=lambda t: -t['media_count'])
    for i, t in enumerate(topics, 1):
        t['id'] = f'{datetime.date.today():%Y%m%d}-{i:02d}'
    json.dump({'made_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'article_count': len(items), 'topics': topics},
              open(os.path.join(HERE, 'data', 'topics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'기사 {len(items)}건 -> 묶음 {len(groups)}개 -> {MIN_SOURCES}개 매체 이상 {len(topics)}개')
    for t in topics[:8]:
        print(f'  [{t["media_count"]}곳] {t["title"][:50]}')


if __name__ == '__main__':
    main()
