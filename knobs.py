# -*- coding: utf-8 -*-
"""손잡이: 레퍼런스 플랫폼의 핵심 장치를 독자가 돌려 보는 값. site.local.json 의 "knobs" 에 저장되고 build.py 가 css() 를 얹는다. 파이썬 기본 기능만 쓴다.
python run.py 손잡이            목록·지금 값·레퍼런스 값과 그렇게 해 둔 까닭
python run.py 손잡이 본문폭 760  돌려 보기(다시 찍고, --shots 면 전·후 화면)"""

DEFS = {
    '본문폭': dict(key='body_width', vals=[560, 620, 680, 760, 840], ref=680, unit='px', why='한 줄이 너무 길면 다음 줄을 찾다 눈이 줄을 놓치고, 너무 짧으면 자주 꺾여 읽기가 끊깁니다. 미디엄은 680px(글자 크기의 34배)로 두었습니다.'),
    '본문글자': dict(key='body_px', vals=[16, 17, 18, 20, 22], ref=20, unit='px', why='미디엄은 20px 입니다. 긴 글을 오래 읽어도 눈이 덜 피곤하라고 보통 사이트(16px)보다 크게 둡니다. 숫자·표가 많은 글은 조금 작아야 한눈에 들어옵니다.'),
    '줄높이': dict(key='line_height', vals=[1.5, 1.6, 1.75, 1.9], ref=1.6, unit='배', why='미디엄은 글자의 1.6배입니다. 한글은 글자가 꽉 차 보여서 영문보다 조금 넓게(1.7 안팎) 두는 곳이 많습니다.'),
    '목록열': dict(key='cols', vals=[2, 3, 4], ref=3, unit='열', why='미디엄 목록은 3열 그림 카드입니다. 열이 많으면 한 화면에 많이 보이지만 카드 제목이 작아지고, 적으면 한 건 한 건이 크게 보입니다.'),
    '읽는시간': dict(key='readtime', vals=['켬', '끔'], ref='켬', unit='', why='미디엄은 글 머리에 「2 min read」를 둡니다. 읽기 전에 얼마나 걸릴지 알면 시작하는 사람이 늘어납니다.'),
    '저장': dict(key='save', vals=['켬', '끔'], ref='켬', unit='', why='미디엄은 글마다 저장(북마크)을 둡니다. 저장해 둔 글을 읽으러 다시 옵니다. 우리는 서버 없이 이 기기의 브라우저에만 저장합니다.'),
    '듣기': dict(key='listen', vals=['켬', '끔'], ref='켬', unit='', why='미디엄은 글을 읽어 주는 듣기 단추를 둡니다. 읽을 수 없는 시간(걷기·운전)에도 쓰게 하려는 것입니다.'),
}
DEFS.update({
    '순위셈법': dict(key='gravity', vals=[1.2, 1.8, 2.5], ref=1.8, unit='', why='해커 뉴스는 점수를 올린 뒤 지난 시간의 거듭제곱으로 나눠 순서를 정합니다(공식 안내의 설명). 널리 알려진 값은 1.8 이고 공식 안내에 숫자는 없습니다. 값이 크면 글이 빨리 내려가 새 글이 자주 올라오고, 작으면 좋은 글이 오래 머뭅니다.'),
    '한쪽줄수': dict(key='per_page', vals=[10, 20, 30, 50], ref=30, unit='줄', why='해커 뉴스 첫 화면은 한 쪽에 30줄입니다. 줄이 많으면 훑어볼 것이 많고, 적으면 위쪽 글에 눈이 모입니다.'),
    '게시판글자': dict(key='board_font', vals=['본', '크게'], ref='본', unit='', why='해커 뉴스는 제목 10pt(13.3px)·아랫줄 7pt(9.3px)의 작은 글자로 한 화면에 30줄을 넣습니다(휴대폰에서는 11pt·9pt). 영문 기준이라 한글은 답답할 수 있어 「크게」(16px·13px)를 고를 수 있습니다. 크게 하면 한 화면에 보이는 줄이 줄어듭니다.'),
    '공개방식': dict(key='moderation', vals=['승인뒤', '바로'], ref='바로', unit='', why='해커 뉴스는 올리면 바로 보이고, 신고(flag)와 운영자가 나중에 걸러 냅니다. 혼자 운영하는 작은 게시판은 지켜보는 눈이 적어 「승인 뒤 공개」가 안전합니다(그만큼 날마다 확인할 일이 생깁니다).'),
})
DEFS.update({
    '사는단추': dict(key='buy_mode', vals=['주문문의', '바깥주소'], ref='결제', unit='', why='검로드의 「I want this!」는 바로 결제 화면으로 갑니다(검로드가 결제·세금을 맡고 수수료를 뗍니다 — 가격 쪽: 직접 판매 10% + 50센트, 둘러보기를 거친 판매 30%). 혼자서는 결제·정산을 다루기 어려워, 이 틀은 주문 문의를 받거나(서버가 운영자 화면에 쌓음) 바깥 판매 주소로 보냅니다.'),
    '값정하기': dict(key='pwyw', vals=['켬', '끔'], ref='켬', unit='', why='검로드에는 사는 사람이 값을 정하는 상품이 있습니다(값 뒤에 + 표시). 최소 값만 정해 두고 더 내고 싶은 사람은 더 냅니다. 켜 두면 「+」가 붙은 상품의 주문 문의에 「내고 싶은 값」 칸이 생깁니다.'),
    '상품열': dict(key='market_cols', vals=[2, 3, 4], ref=3, unit='열', why='검로드 둘러보기는 왼쪽 거르기 상자 옆에 3열 카드입니다. 열을 줄이면 그림이 커지고 늘리면 한 화면에 더 많이 보입니다.'),
    '딱지색': dict(key='market_color', vals=['#ff90e8', '#90a8ed', '#ffc900', '#23a094'], ref='#ff90e8', unit='', why='검로드의 값 딱지와 사는 단추는 분홍(#ff90e8)이 기본이고, 판매자가 자기 색으로 바꿀 수 있습니다(본 상품 쪽은 파랑이었습니다).'),
})
DEFS.update({
    '순위기간': dict(key='trend_period', vals=['오늘', '이번주', '이번달'], ref='오늘', unit='', why='깃허브 트렌딩은 처음 열면 「오늘(Today)」 순위이고, 이번 주·이번 달로 바꿔 볼 수 있습니다. 기간이 짧으면 날마다 얼굴이 바뀌어 자주 올 까닭이 생기고, 길면 순위가 차분해지지만 올 때마다 같은 얼굴입니다. 올라오는 것이 적은 작은 사이트는 「이번주」가 덜 비어 보입니다.'),
    '순위줄수': dict(key='trend_rows', vals=[10, 15, 25], ref=10, unit='줄', why='깃허브 트렌딩 한 쪽은 받아 본 날 10줄이었습니다(다음 쪽이 없습니다). 줄이 적으면 「순위에 든다」는 것이 값지고, 많으면 더 많은 항목이 눈에 띕니다.'),
    '순위바탕': dict(key='trend_theme', vals=['기기따라', '밝게', '어둡게'], ref='기기따라', unit='', why='깃허브는 보는 사람 기기의 밝게/어둡게 설정을 따라갑니다(그래서 같은 쪽이 사람마다 다르게 보입니다). 한쪽으로 못 박으면 누구에게나 같은 모습입니다.'),
})
NEED = {'읽는시간': 10, '저장': 10, '듣기': 10, '목록열': 4}   # 이 손잡이가 보이려면 먼저 얹어야 하는 다듬기 걸음


def get(S, name):
    d = DEFS[name]; v = (S.get('knobs') or {}).get(d['key'])
    return v


def css(S):
    K = S.get('knobs') or {}; out = ''
    if S.get('accent'):   # 독자가 정한 색은 어느 틀·어느 다듬기 층에서도 보이게(강조색·머리 색·링크 색)
        a = str(S['accent']).replace(';', '').replace('}', '')
        out += f":root{{--ac:{a};--pri:{a};--link:{a}}}\nbody a.btn,body .btn-pri,body .mast .sub-btn{{background:{a};border-color:{a}}}\n"
    if K.get('body_width'):
        out += f"body .art,body .page{{box-sizing:content-box;max-width:{int(K['body_width'])}px}}\n"
    if K.get('body_px') or K.get('line_height'):
        px = K.get('body_px'); lh = K.get('line_height')
        rule = (f"font-size:calc({px}px*var(--fz,1));" if px else '') + (f"line-height:{lh};" if lh else '')
        out += f"body .art p.sum,body .art li,body .art .src-card p,body .page p,body .page li{{{rule}}}\n"
    if K.get('cols'):
        out += f"@media(min-width:1001px){{body .pg{{grid-template-columns:repeat({int(K['cols'])},minmax(0,1fr))}}}}\n"
    return out


def parse(name, raw):
    d = DEFS[name]
    for v in d['vals']:
        if str(v) == str(raw):
            return v
    if all(isinstance(x, str) for x in d['vals']):
        return None
    try:
        f = float(raw)
        lo, hi = min(x for x in d['vals'] if not isinstance(x, str)), max(x for x in d['vals'] if not isinstance(x, str))
        if lo * 0.7 <= f <= hi * 1.3:
            return int(f) if f == int(f) and d['key'] != 'line_height' else f
    except Exception:
        pass
    return None
