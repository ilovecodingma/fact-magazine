# -*- coding: utf-8 -*-
"""대조: 확인 노트(notes/*.json)의 사실 문장마다 출처 주소를 다시 열어, 문장에 든 숫자·날짜가 원문에 그대로 있는지 본다.
하나라도 어긋나면 그 노트는 보류/ 폴더로 옮긴다. 이 단계 없이 자동으로 올리지 않는다.
사용: python check.py            (notes/ 전체 대조, 어긋난 노트는 보류/ 로 이동)
      python check.py --dry-run  (옮기지 않고 결과만 본다)
한계: 숫자·날짜 글자가 원문에 있는지만 본다. 뜻이 맞는지는 사람이 읽어야 한다.
      정책브리핑은 보기 쪽 요약문이 잘려 있어 목록 쪽 요약문까지 함께 본다(느슨한 대조 — 같은 숫자가 목록의 다른 글에 있어도 통과할 수 있다)."""
import json, os, re, sys, glob, shutil, time, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = re.compile(r'\d[\d,.]*')


def numbers(text):
    """문장에서 숫자 덩어리를 뽑는다. 쉼표·마침표 끝 장식은 떼고, 한 자리 수는 빼고 비교한다."""
    out = set()
    for m in NUM.findall(text):
        m = m.strip(',.')
        if len(m.replace(',', '')) >= 2:
            out.add(m.replace(',', ''))
    return out


def page_text(url):
    """출처 쪽 글자만 가져온다(태그·스크립트 제거, 쉼표 뺀 숫자 비교용으로 쉼표도 제거)."""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (fact-magazine check)'})
    raw = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    raw = re.sub(r'(?s)<style\b.*?</style>', ' ', raw)   # 스크립트 안 글자는 남긴다: 정책브리핑은 요약문이 <script> 안에 들어 있다
    return html.unescape(re.sub(r'<[^>]+>', ' ', raw)).replace(',', '')


def check_note(n):
    """노트 하나를 대조해 (통과 여부, 문제 목록)을 돌려준다."""
    problems, cache = [], {}
    if not n.get('facts'):
        if n.get('verdict') == '아직 확인 안 됨':
            return True, []   # 공식 자료에서 못 찾았다는 판정이면 대조할 사실 문장이 없는 게 정상
        return False, ['사실 문장(facts)이 없습니다']
    for f in n['facts']:
        url = f.get('url', '')
        if not url.startswith('http'):
            problems.append(f'출처 주소 없음: {f.get("text", "")[:30]}'); continue
        try:
            if url not in cache:
                cache[url] = page_text(url); time.sleep(1)
        except Exception as e:
            problems.append(f'출처 열기 실패({repr(e)[:40]}): {url}'); continue
        text = cache[url]
        if 'korea.kr/briefing/pressReleaseView' in url:   # 정책브리핑 보기 쪽 요약문은 뒤가 잘려 있어, 같은 날 보도자료 목록 쪽 요약문도 함께 본다(느슨한 대조: 목록 어디에든 숫자가 있으면 통과)
            lst = 'https://www.korea.kr/briefing/pressReleaseList.do'
            if lst not in cache:
                cache[lst] = page_text(lst); time.sleep(1)
            text += cache[lst]
        missing = [x for x in numbers(f['text']) if x not in text]
        if missing:
            problems.append(f'원문에 없는 숫자 {missing}: {f["text"][:40]}')
    return not problems, problems


def main():
    dry = '--dry-run' in sys.argv
    held = 0
    for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json'))):
        n = json.load(open(p, encoding='utf-8'))
        if n.get('example'):
            continue
        ok, pr = check_note(n)
        print(('통과' if ok else '보류'), os.path.basename(p))
        for x in pr:
            print('   -', x)
        if not ok and not dry:
            os.makedirs(os.path.join(HERE, '보류'), exist_ok=True)
            shutil.move(p, os.path.join(HERE, '보류', os.path.basename(p))); held += 1
    print(f'보류 {held}건')
    return 0


if __name__ == '__main__':
    sys.exit(main())
