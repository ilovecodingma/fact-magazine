# -*- coding: utf-8 -*-
"""1단계 수집: feeds.json 의 RSS 를 열어 제목·매체·시각·링크만 data/items.json 에 모은다.
기사 본문은 가져오지 않는다. 파이썬 기본 기능만 쓴다.  실행: python collect.py"""
import json, os, sys, time, datetime, email.utils, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')   # 윈도우에서 한글 출력이 깨지지 않게
except Exception:
    pass
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
KEEP_HOURS = 72   # 사흘 안의 기사만 남긴다


def parse_time(text):
    """RSS 날짜 글자를 datetime(한국시간 기준 글자)으로. 못 읽으면 지금."""
    try:
        d = email.utils.parsedate_to_datetime(text)
        return d.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    except Exception:
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))


def read_feed(feed):
    """피드 하나를 읽어 기사 목록을 돌려준다. 실패하면 (빈 목록, 이유)."""
    req = urllib.request.Request(feed['url'], headers={'User-Agent': 'Mozilla/5.0 (fact-magazine practice)'})
    try:
        raw = urllib.request.urlopen(req, timeout=25).read()
        root = ET.fromstring(raw)
    except Exception as e:
        return [], repr(e)[:120]
    out = []
    for it in root.iter('item'):
        title = (it.findtext('title') or '').strip()
        link = (it.findtext('link') or '').strip()
        if not title or not link.startswith('http'):
            continue
        t = parse_time(it.findtext('pubDate') or '')
        out.append({'source': feed['source'], 'section': feed['section'], 'kind': feed['kind'],
                    'title': title, 'link': link, 'time': t.strftime('%Y-%m-%d %H:%M')})
    return out, ''


def main():
    feeds = json.load(open(os.path.join(HERE, 'feeds.json'), encoding='utf-8'))['feeds']
    os.makedirs(DATA, exist_ok=True)
    old = []
    p = os.path.join(DATA, 'items.json')
    if os.path.exists(p):
        old = json.load(open(p, encoding='utf-8')).get('items', [])
    seen = {x['link']: x for x in old}
    log = []
    for f in feeds:
        items, err = read_feed(f)
        log.append({'source': f['source'], 'section': f['section'], 'count': len(items), 'error': err})
        for x in items:
            seen[x['link']] = x
        time.sleep(1)   # 한 곳씩 사람 속도로
    limit = (datetime.datetime.now() - datetime.timedelta(hours=KEEP_HOURS)).strftime('%Y-%m-%d %H:%M')
    items = sorted((x for x in seen.values() if x['time'] >= limit), key=lambda x: x['time'], reverse=True)
    json.dump({'collected_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'log': log, 'items': items},
              open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for x in log:
        print(f'  {x["source"]} {x["section"]}: {x["count"]}건' + (f'  (실패: {x["error"]})' if x['error'] else ''))   # 피드별 건수(새 피드를 넣고 열리는지 확인할 때 본다)
    bad = [x for x in log if x['error'] or not x['count']]
    print(f'기사 {len(items)}건, 피드 {len(log)}곳 중 문제 {len(bad)}곳')
    for x in bad:
        print('  문제:', x['source'], x['section'], x['error'] or '0건')
    return 1 if len(bad) == len(log) else 0


if __name__ == '__main__':
    sys.exit(main())
