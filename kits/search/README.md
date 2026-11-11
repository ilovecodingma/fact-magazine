# 사이트 안 검색 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 이 저장소에 사이트 안 검색을 켜 줘. site.json 의 parts 에서 search 를 켜고 빌드해서 /search/ 에서 글자를 치면 쪽이 나오는지 확인해 줘.

- **넣는 것 → 나오는 것**: 켜기만 하면 → 찍을 때 만든 색인 파일(search.json)을 브라우저가 읽어 /search/ 에서 쪽을 찾음(서버 없음)
- **2분 안에 보는 결과**: /search/ 에 「연금」을 치면 관련 쪽이 바로 나옵니다
- **사이트 어디에 붙나**: 메뉴 「검색」, /search/, search.json
- **서버**: 불필요 · **따라 하는 시간**: 약 2분
- **켜기**: `python mix.py search`(또는 `site.json` 의 `parts` 에서 `search` 켜기) 후 `python build.py`
- **자료 위치**: `kits/search/data/`
