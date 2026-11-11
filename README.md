# 에이전트와 만드는 정보 사이트 + 웹 게임 하네스

**여섯 걸음** — 책의 차례(1부 기능 만들기 / 2부 조립·홍보·운영)와 같은 순서입니다.

1. **키트 하나 해 보기(5분)** — `python doctor.py` 로 점검하고 `python serve.py --open` 으로 내 PC 에서 열어, 키트 하나(예: 계산기)를 해 봅니다. `python know.py 계산기` 로 꼭 알아야 할 것을 읽습니다.
2. **섞기** — `python mix.py 키트1 키트2 …` 로 고른 키트만 켠 사이트를 찍습니다(`kits/README.md`).
3. **조립 예시 열 개에서 고르기** — `python serve.py` 후 `http://127.0.0.1:8000/demo/` 에서 열 개 가운데 하나를 내 이름·내 자료로 바꿉니다.
4. **올리기(선택)** — 내 PC 에서 열어 본 뒤 공개 서비스에 올립니다(`CLAUDE.md` 5번). 로그인·공개는 사람이 합니다.
5. **알리기** — `python promo.py`(블로그용 글·알림 문구), `python card.py`(공유용 그림), `python shorts.py`(쇼츠)로 올릴 준비를 하고, 올리기는 승인 뒤에 합니다.
6. **하루 한 바퀴** — `python run_daily.py` 로 수집부터 점검까지 한 번에(`런북.md` 12·18절).

> **Claude Code 에서 한 줄로 시작**: `이 저장소 주소는 <주소> 야. 시작.md 를 읽고 그대로 해 줘.` (총괄 세션이 받기·점검·내 PC 열기까지 해 줍니다)

---

에이전트에게 주소 하나만 주면 **뉴스 정보 사이트와 브라우저 웹 게임 몇 개를 가진 내 사이트**가 만들어지는 실습 저장소입니다. 정보 쪽은 뉴스 RSS 제목을 모으고, 여러 매체가 함께 다룬 소식을 묶고, 그중 제도·숫자·날짜를 공식 자료와 대조해 「확인 노트」로 싣는 작은 정적 사이트입니다. 게임은 `games/` 폴더에 게임마다 폴더 하나(`meta.json` + `game.js`)로 들어 있습니다(예: `games/rumor/`). 비용 0원(GitHub Pages + GitHub Actions), 파이썬 기본 기능만 씁니다.

> **Claude Code 에 이 주소를 주고 이렇게 입력하세요**
>
> `이 저장소 주소는 <이 저장소의 주소> 야. CLAUDE.md 를 읽고, 내 이름으로 복사해서 내 사이트로 만들어 줘. 주제는 <내가 다루고 싶은 주제>. 로그인이나 공개 게시처럼 내가 해야 하는 건 그때 멈추고 물어봐.`

더 많은 입력 예시는 `프롬프트/` 폴더에 있습니다.

## 무엇이 들어 있나
- 틀: `feeds.json` `collect.py` `group.py` `build.py` `check.py`
- 웹 게임: `games/<이름>/meta.json` + `game.js` (캔버스, 바깥 라이브러리·이미지·소리 없음). `build.py` 가 `docs/games/` 로 복사하고 `/games/` 목록 쪽을 만듭니다
- 규칙: `CLAUDE.md`(에이전트가 가장 먼저 읽음) `런북.md`(하루 한 바퀴와 멈추는 자리)
- 역할 안내: `역할/` (기획·개발·마케터·홍보, 세션 하나로 돌리는 방법)
- 자동 갱신: `.github/workflows/daily.yml` (수집·묶기·빌드만)

## 직접 해 보려면
```
python collect.py          # RSS 수집
python group.py            # 함께 다룬 소식 묶기
python build.py --example  # 예시 노트로 화면 확인 → docs/index.html 열기
python build.py            # 공개 빌드
```
`site.json` 의 이름을 내 것으로 바꾼 뒤, **Cloudflare Pages**(무료, `프로젝트이름.pages.dev`)에 `docs/` 폴더를 올리면 사이트가 열립니다(`npx wrangler pages deploy docs --project-name 이름`, 로그인은 사람이 합니다). 주소가 정해지면 `site.json` 의 `url` 에 넣고 다시 빌드하세요. 다음 단계로 내 도메인을 붙일 수 있고, Vercel·GitHub Pages 에 올리는 다른 방법은 `CLAUDE.md` 5번에 있습니다.

## 지키는 것
기사 본문은 옮기지 않고 제목·매체·시각·링크만 씁니다. 공식 자료에서 못 찾은 것은 지어서 채우지 않고 「아직 확인 안 됨」으로 둡니다. 연예인·정치인·사건 당사자 이야기는 다루지 않습니다.

## 부품 → 만들 수 있는 것 (조합표)

부품은 `site.json` 의 `parts` 에서 켜고 끕니다. `python preset.py 이름` 으로 묶음째 바꾸고, 묶음에 없는 조합은 `python preset.py info,games,issue` 처럼 **부품 이름을 나열**하거나 `site.json` 의 `parts` 를 직접 고칩니다. 에이전트에게 「이 부품들로 ○○ 서비스 만들어 줘」라고 하면 `presets.json` 을 보고 무엇을 켜고 끌지 정합니다.

| 부품 | 파일 | 하는 일 | `parts` 이름 |
|---|---|---|---|
| 수집 + 묶기 + 화면 | `collect.py` `group.py` `build.py` | 뉴스 제목 모아 함께 다룬 소식 묶고 사이트로 찍기 | `info` |
| 확인 노트 + 대조 | `notes/` `check.py` | 공식 자료와 숫자·날짜 대조, 통과한 것만 | `info` |
| 웹 게임 | `games/` | 브라우저 게임(캔버스) 여러 개, 판 번호·바뀐 것 표시 | `games` |
| 잡지(호 발행) | `issue.py` | 그날 노트를 「호」로 묶은 쪽 + 인쇄용 PDF | `issue` |
| 쇼츠 영상 | `shorts.py` | 노트 → 세로 영상(글자·도형, 품질 문턱) | `shorts` |
| 소식지 메일 | `mail.py` | 오늘 노트 요약을 메일 한 통으로(SMTP) | `mail` |
| 메일 대응 | `inbox.py` | 문의 메일만 골라 답장 초안(보내지는 않음) | `inbox` |
| 하루 한 바퀴 | `run_daily.py` | 위를 순서대로 한 번에(스케줄러에 걸 수 있음) | — |

| 만들 서비스 | 켤 부품(묶음 이름) |
|---|---|
| 정보 매거진 | `info` + `issue` (`정보 매거진`) |
| 게임 모음 | `games` (`게임 모음`) |
| 영상 채널 | `info` + `shorts` (`영상 채널`) |
| 소식지 | `info` + `issue` + `mail` + `inbox` (`소식지`) |
| 전부 | 모두 (`전부`) |
