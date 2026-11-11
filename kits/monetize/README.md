# 돈이 나올 자리 키트

켜면 모든 쪽 아래에 광고 칸·제휴 링크·후원/문의·소식 받기 자리가 붙고, 푸터에 「광고·제휴 고지」와 `/disclosure/` 쪽이 생깁니다. 값은 `site.local.json` 의 `monetize` 에 넣습니다:

```json
"monetize": {"ad": {"html": "<광고 코드>"}, "affiliates": [{"name": "상품 이름", "url": "https://…", "note": "한 줄"}], "support": {"label": "후원하기", "url": "https://…"}, "newsletter": {"label": "소식 받기", "url": "https://…"}}
```

값이 없으면 틀(자리)만 보입니다. **광고·제휴·후원 서비스 가입과 심사는 사람이 합니다.**
