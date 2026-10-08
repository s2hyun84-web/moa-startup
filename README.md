# 모아 · 개인용 창업지원 데스크

월간·주간·목록 캘린더, 검색·카테고리·지원 자격 필터, 관심 공고, 지원 단계와 메모, 수동 등록·수정·삭제, 로컬 저장, JSON 백업·병합 복원을 제공하는 정적 웹사이트입니다.

## 현재 상태

- 앱 구현 및 데이터 처리 자동 검사 9개 완료.
- 공식 API 인증키는 포함되어 있지 않습니다. 실제 공고 데이터는 빈 상태이며 샘플은 별도 선택해야 표시됩니다.
- 기업마당 공식 API 수집 코드를 포함합니다. 발급된 인증키를 이용한 실제 수집 검증은 아직 하지 않았습니다.
- K-Startup 자동 연동은 미구현입니다. 해당 공고는 수동으로 등록할 수 있습니다.
- 브라우저의 실제 화면·모바일·전체 저장 흐름 검증은 별도로 필요합니다.

## 무료 GitHub Pages 배포

1. GitHub 계정 `s2hyun84-web`에서 공개 저장소 `moa-startup`을 만듭니다.
2. **이 README가 있는 폴더의 내용**을 저장소 최상위에 업로드합니다. `site`, `scripts`, `tests`, `.github`, `.gitignore`, `package.json`, `README.md`가 최상위에 있어야 합니다. ZIP 자체를 올리는 것이 아닙니다. `.github` 같은 숨김 폴더도 반드시 포함합니다.
3. 기본 브랜치를 `main`으로 사용합니다.
4. 저장소 Settings → Pages → Build and deployment → Source에서 **GitHub Actions**를 선택합니다.
5. 키 없이 먼저 배포하려면 Actions → Collect public notices and deploy Pages → Run workflow에서 `collect`를 **해제(false)**하고 실행합니다. 초기 push도 키가 없으면 빈 공고 상태의 앱을 배포합니다.
6. 배포가 성공하면 `https://s2hyun84-web.github.io/moa-startup/`에 접속합니다. 성공 전에는 404가 표시될 수 있습니다.

GitHub Free의 공개 저장소에서 Pages를 이용할 수 있고, 표준 GitHub-hosted runner의 공개 저장소 Actions는 무료 제공 대상입니다. 사용자 지정 도메인은 불필요합니다. 요금과 사용 제한은 GitHub의 최신 정책을 확인하세요.

## 공식 API 키 설정과 매일 갱신

1. [기업마당 API 신청 페이지](https://www.bizinfo.go.kr/apiDetail.do?id=bizinfoApi)에서 사용 신청 후 인증키를 발급받습니다.
2. GitHub 저장소 Settings → Secrets and variables → Actions → New repository secret을 선택합니다.
3. 이름을 `BIZINFO_API_KEY`, 값은 발급받은 키로 저장합니다. 키를 소스·README·공개 공고 파일·채팅에 붙여 넣지 마세요.
4. Actions에서 워크플로를 수동 실행할 때 `collect`를 켭니다.
5. 이후 매일 한국 시간 오전 7시 17분에 예약 실행합니다. GitHub 실행 대기 상황에 따라 지연되거나 누락될 수 있습니다. 공개 저장소가 60일간 비활성 상태이면 예약 실행이 중지될 수 있으므로 Actions에서 확인하고 재활성화하세요.

API 수집은 GitHub Actions에서 수행하며 공개 공고만 배포 산출물에 넣습니다. 저장소에 데이터 갱신 커밋을 만들지 않습니다. 실패한 수집은 배포를 중단하여 기존 배포를 유지합니다. **키를 제거한 상태의 push 또는 collect=false 수동 배포는 소스에 포함된 빈 공고 파일을 배포하므로 기존 공개 공고 목록이 비게 됩니다.** 관심 공고로 저장한 정보는 브라우저에 남습니다.

화면의 ‘배포된 공고 다시 읽기’는 이미 배포된 파일을 다시 읽는 기능입니다. API 수집 자체를 실행하지 않습니다. ‘마지막 수집’ 시간을 확인하세요. API 응답 구조가 바뀌거나 전체 건수가 맞지 않으면 수집이 실패하도록 되어 있습니다. 인증키·서비스 상태·응답 형식을 확인해야 합니다.

마감일이 모호하거나 예산 소진 시까지인 공고는 임의 날짜를 지정하지 않고 ‘일정 확인 필요’에 표시합니다. 지원 자격 분류는 검색 보조이며 실제 지원 가능 여부는 공식 원문으로 확인하세요.

## 개인 기록과 백업

관심 공고, 지원 단계, 메모, 직접 등록한 공고는 **사이트 주소별 현재 브라우저의 localStorage**에만 저장합니다. 서버나 GitHub로 전송하지 않습니다. 다른 기기·브라우저·사이트 주소로 자동 동기화되지 않습니다.

‘데이터와 백업’에서 백업 파일을 내려받고 다른 기기에서 복원할 수 있습니다. 복원은 합치기 방식이며 같은 항목은 백업 내용으로 갱신됩니다. 복원 전에 현재 기록을 백업하세요. 브라우저 데이터 삭제, 비공개 모드 종료, 기기 분실에 대비해 정기 백업하세요. 로컬 저장은 암호화된 보관함이 아니므로 공용 기기에 민감한 기록을 남기지 마세요.

**공개 저장소에 올리지 않을 것:** 내려받은 `moa-backup-*.json`, 개인 자료, API 인증키, `.env` 파일. `.gitignore`가 해당 파일들을 제외하지만 브라우저 업로드 시에는 직접 파일 선택을 확인해야 합니다. 배포는 `scripts/stage.py`의 허용 목록만 사용합니다. 저장소 소스 자체에 개인정보를 넣으면 배포 제외 여부와 관계없이 공개되므로 넣지 마세요.

## 내 컴퓨터에서 실행

Python 3가 설치되어 있다면 이 폴더에서:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

브라우저에서 `http://127.0.0.1:4173`에 접속합니다. 종료는 터미널에서 Ctrl+C입니다. HTML 파일을 직접 더블 클릭하는 방식은 모듈과 데이터 읽기가 제한되어 지원하지 않습니다.

개발 검사는 Node.js 22 및 Python 3.12 환경에서 `npm test`로 실행합니다. 별도 라이브러리 설치는 필요 없습니다.

## 공식 참고 자료

- [기업마당 API 명세 및 신청](https://www.bizinfo.go.kr/apiDetail.do?id=bizinfoApi)
- [GitHub Pages 시작하기](https://docs.github.com/en/pages/getting-started-with-github-pages)
- [GitHub Actions 안내](https://github.com/features/actions)
- [GitHub 예약 실행 제한](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
