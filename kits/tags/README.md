# 태그 쪽 키트

**이렇게 입력하세요** (Claude Code 에 그대로 붙여 넣기)

> 태그 쪽을 켜 줘. 확인 노트의 tags 와 kits/tags/data/post_tags.json 의 글 태그로 /tags/ 에 태그별 목록이 생기는지 확인해 줘.

- **넣는 것 → 나오는 것**: 글·노트의 태그 → /tags/ 태그 목록 + 태그별 목록 쪽
- **2분 안에 보는 결과**: /tags/ 에서 태그를 누르면 그 태그가 붙은 글·노트가 나옵니다
- **예시 자료**: `kits/tags/data/`(있는 키트만, 일반 내용)
- **켜기**: `python mix.py --add tags` 후 `python build.py`
- **서버**: 불필요
