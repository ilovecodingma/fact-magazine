# 링크 모음 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 링크 모음 쪽을 켜 줘. kits/links/data/links.json 에 분류별 링크를 적고 /links/ 에 나오는지, python linkcheck.py 로 깨진 링크가 있는지 점검해 줘.

- **넣는 것 → 나오는 것**: 주소 목록(분류별) → 링크 쪽 + linkcheck.py 로 깨진 링크 점검
- **2분 안에 보는 결과**: /links/ 에 분류별 링크가 나오고 linkcheck.py 가 각 주소의 상태를 알려 줍니다
- **예시 자료가 이미 들어 있습니다**: `kits/links/data/`(숫자·제도를 지어내지 않은 일반 내용). 켜기만 하면 바로 나오고, 내 것으로 바꾸려면 예시를 지우고 내 내용으로 교체합니다.
- **켜기**: `python mix.py --add links`(지금 켜진 것에 더하기) 또는 `python mix.py links`(이것만) 후 `python build.py`
- **서버**: 불필요
