# ruri-ctrl — 로컬 크롬 제어 확장 (실습 자료)

내 PC에서 돌아가는 작은 서버(127.0.0.1:8765)가 명령을 내리면, 크롬 확장이 `chrome.debugger` 로 탭을 열고 누르고 입력하고 화면을 찍어 돌려주는 구조입니다. 로그인해 둔 내 크롬 프로필 안에서 동작하므로, 자기 계정으로 하는 반복 작업을 자동화하는 연습에 씁니다.

```
x.py ──명령──▶ server.py(127.0.0.1:8765) ◀──20초 단위 요청──  background.js(확장)
                                                          └─ chrome.debugger ─▶ 탭
```

## 파일
| 파일 | 역할 |
|---|---|
| manifest.json, background.js | 확장(MV3). 서버에서 명령을 받아 탭에서 실행 |
| server.py | 명령 중계 서버. 127.0.0.1 에만 열림, 모든 요청에 토큰 헤더 필요 |
| x.py | 서버에 명령 한 건을 보내는 클라이언트 |
| xe.py | JS 파일을 탭에서 실행하는 보조 |
| make_token.py | 접근 토큰 생성 |

## 설치
1. 토큰 만들기: `python make_token.py` → `token.txt`, `token.js` 가 생깁니다. 이 두 파일은 `.gitignore` 로 제외되어 있으니 **절대 올리지 마세요.** 토큰이 새면 다시 실행해 새로 만들고 확장을 새로고침합니다.
2. 서버 켜기: `python server.py`
3. 크롬 주소창에 `chrome://extensions` → 오른쪽 위 **개발자 모드** 켜기 → **압축해제된 확장 프로그램을 로드합니다** → 이 폴더 선택.
4. 확장이 서버에 연결되면 명령이 통합니다.

## 쓰기
```
python x.py "{\"op\":\"tabs\"}"
python x.py "{\"op\":\"open\",\"url\":\"https://example.com\"}"
python x.py "{\"op\":\"shot\",\"tab\":123}"      # shot.png 로 저장
```
명령: tabs, open, newtab, nav, activate, close, eval, click, type, key, scroll, shot, upload

## 주의
- 디버거로 탭을 완전히 제어하는 도구입니다. 토큰을 아는 쪽이 로그인된 탭을 마음대로 움직일 수 있으므로 토큰 파일을 지키세요.
- 새 탭을 만들어 곧바로 유튜브를 열면 탭이 사라지는 일이 있었습니다. 빈 페이지로 연 뒤 이동하면 정상이었습니다.
- 내 계정, 내가 허용된 사이트에서만 쓰세요. 사이트 약관의 자동화 제한을 확인하세요.
