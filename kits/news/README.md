# 뉴스 수집·묶기 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 이 저장소로 뉴스 정보 사이트를 만들어 줘. feeds.json 의 RSS 를 모으고(collect.py) 여러 매체가 함께 다룬 소식으로 묶고(group.py) 빌드해서 첫 화면에 나오는지 확인해 줘.

- **넣는 것 → 나오는 것**: RSS 목록 → 함께 다룬 소식 묶음 + 확인 노트 화면
- **2분 안에 보는 결과**: 첫 화면에 「오늘 여러 매체가 함께 다룬 소식」이 뜹니다
- **파일 위치·붙는 곳**: collect.py · group.py · build.py · check.py · notes/ (이 키트는 저장소 맨 위의 파일을 가리킵니다 — 파일을 옮기지 않았습니다)
- **켜기**: `python mix.py news` 후 `python build.py`
