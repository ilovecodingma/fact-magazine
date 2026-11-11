# 공지·바뀐 내역·중복 점검 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 공지를 켜 줘. kits/notice/data/notice.md 첫 줄이 첫 화면 위에 나오고 changes.json 이 /changes/ 에 나오는지 확인해 줘. 그리고 python dupcheck.py 로 비슷한 제목을 점검해 줘.

- **넣는 것 → 나오는 것**: 공지 파일 + 바뀐 내역 파일 → 첫 화면 한 줄 + /changes/ 쪽, dupcheck.py 로 비슷한 제목 짝
- **2분 안에 보는 결과**: 첫 화면 위에 노란 공지 한 줄이 뜨고 「바뀐 내역」에서 날짜순 목록이 보입니다
- **예시 자료가 이미 들어 있습니다**: `kits/notice/data/`(숫자·제도를 지어내지 않은 일반 내용). 켜기만 하면 바로 나오고, 내 것으로 바꾸려면 예시를 지우고 내 내용으로 교체합니다.
- **켜기**: `python mix.py --add notice`(지금 켜진 것에 더하기) 또는 `python mix.py notice`(이것만) 후 `python build.py`
- **서버**: 불필요
