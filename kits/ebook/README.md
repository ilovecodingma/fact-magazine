# 전자책 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 이 저장소의 글과 연재 소설을 PDF 전자책 한 권으로 묶어 줘. python ebook.py 를 돌리고 /ebook/ 에서 내려받을 수 있는지 확인해 줘.

- **넣는 것 → 나오는 것**: python ebook.py → 글(posts)과 연재(novels)를 표지·차례가 있는 PDF 한 권으로 → /ebook/ 에 내려받기
- **2분 안에 보는 결과**: /ebook/ 에서 PDF 를 내려받아 열면 표지와 차례가 있습니다
- **사이트 어디에 붙나**: 푸터 「전자책」, /ebook/
- **서버**: 불필요(브라우저 인쇄 기능) · **따라 하는 시간**: 약 5분
- **켜기**: `python mix.py ebook`(또는 `site.json` 의 `parts` 에서 `ebook` 켜기) 후 `python build.py`
- **자료 위치**: `kits/ebook/data/`
