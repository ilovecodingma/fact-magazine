# 타임라인 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 타임라인 쪽을 켜 줘. kits/timeline/data/timeline.json 에 일어난 일을 날짜·제목·내용으로 적고 /timeline/ 에 시간순으로 나오는지 확인해 줘.

- **넣는 것 → 나오는 것**: 일어난 일 목록(JSON) → 시간순 정리 쪽
- **2분 안에 보는 결과**: /timeline/ 에 날짜순으로 일이 나열됩니다
- **예시 자료가 이미 들어 있습니다**: `kits/timeline/data/`(숫자·제도를 지어내지 않은 일반 내용). 켜기만 하면 바로 나오고, 내 것으로 바꾸려면 예시를 지우고 내 내용으로 교체합니다.
- **켜기**: `python mix.py --add timeline`(지금 켜진 것에 더하기) 또는 `python mix.py timeline`(이것만) 후 `python build.py`
- **서버**: 불필요
