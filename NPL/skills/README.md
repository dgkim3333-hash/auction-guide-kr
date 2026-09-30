# NPL 트랙 스킬 25개

[08단원](../../08_NPL전문가.md) NPL 프로젝트가 부르는 스킬 전부입니다. 강사 운영본을 **경로·식별정보만 바꿔** 옮겼습니다.
모든 스킬 첫머리에 「수강생판 안내」가 붙어 있습니다 — 무엇이 강사 환경 전용이고 무엇을 대신 쓰는지 적어 두었습니다.

> [!IMPORTANT]
> 04단원 스킬(9개)과 이름이 겹치는 6개는 **이 폴더 것으로 덮어쓰세요.** NPL판이 원본 그대로라 내용이 더 많습니다.
> `auction-analysis`(경매종합분석)는 NPL판에 없습니다. `npl-analysis` 가 그 자리를 맡습니다.

## 목록

| 스킬 (폴더명 = 스킬 이름) | 파일 | 언제 쓰나 | 필요한 것 |
|---|---|---|---|
| **핵심 분석** | | | |
| `npl-analysis` | 9 | **NPL 매입 건의 주 절차.** 21개 체크리스트 · 배당표 · 매입가 · 추정 감정가 · 임대 가정 · 유입 총투입 · 대출 판정 | 창고 · real-estate · korean-law · ecos(선택) · rone(선택) |
| `auction-property-card` | 1 | **직접낙찰 건의 주 절차.** 서류 판독 → 권리 → 세금 → PPTX 물건카드 | 창고 · vworld · datagokr · KakaoMap |
| `auction-bid-price` | 5 | 입찰가 범위 · 【A】【B】 계수 · 포기 판정 | 없음 (계수는 정적 스냅샷 [추정]) |
| `priority-payment-date-rule` | 1 | 소액임차인 최우선변제 — 기준일 · 시기별 한도 내장표 | korean-law |
| `property-tax-apportionment` | 1 | 주택·근생 복합 공시가격 확보 · 세목별 안분 | vworld · 창고 |
| `real-estate-tax-calculator` | 7 | 취득세·재산세·종부세·양도세 · 세후 IRR | korean-law · vworld |
| **유형별 추가 체크** | | | |
| `residential-auction` | 1 | 다가구·다세대·연립·아파트 | — |
| `commercial-unit-auction` | 1 | 구분상가·오피스 호실 | — |
| `land-auction` | 1 | 토지 | vworld |
| `small-building-auction` | 1 | 꼬마빌딩 | — |
| **NPL 전용** | | | |
| `npl-excel-fill-map` | 1 | NPL수익률.xlsx 입력 칸 정본 매핑 | **Excel MCP** · NPL수익률 템플릿 |
| `npl-purchase-letter` | 5 | 매수의향서 .docx 생성·검증 (A4 1페이지) | **Word MCP** · 의향서 템플릿(동봉) |
| `trust-npl-analysis` | 3 | 담보신탁 NPL 우선수익권 매입 분석 | real-estate · ecos(선택) |
| `trust-npl-routine` | 1 | 신탁 NPL 1주 Stage-Gate 루틴 | 위 스킬들 |
| `corporate-debtor-bankruptcy-check` | 3 | 법인 채무자 회생·파산 리스크 4단계 | nts · nps · fsc · iros · naver-search (선택 — 없으면 수동) |
| `post-auction-loan-simulator` | 5 | 낙찰 후 대출 시뮬레이션 · DSCR · 임계 LTV | Excel MCP · ecos(선택) |
| `post-auction-eviction` | 10 | 낙찰 후 명도 D+7~D+90 · 인도명령서·내용증명 생성 | Word MCP |
| `onbid-api-caller` | 2 | 온비드 API 호출 규칙 | datagokr · real-estate |
| `bid-result-log` | 1 | 입찰 결과·2순위 기록 · 예측 오차 누적 | 없음 (`00_시장데이터\` 에 기록) |
| **서류·파일** | | | |
| `npl-doc-intake` | 2 | 서류 자동 분류 · 표준 파일명 · 새 물건 폴더 | `_템플릿\물건폴더_표준` |
| `npl-file-hygiene` | 2 | 백업 정리 · 두 폴더 대조 · 유실 탐지 | — |
| **산출물** | | | |
| `number-format-guard` | 1 | 원 단위 풀 콤마 · 비율 옆 금액 · 피벗 서식 재검증 | — |
| `npl-svg-chart` | 1 | 권리 사다리 · 문건 타임라인 · 배당 폭포 (당해세 주황 배지) | cairosvg |
| `npl-diagram` | 1 | draw.io 편집 가능 도표 | — |
| `pptx-blue-design-system` | 1 | PPTX 16:9 5존 · 블루 팔레트 · `㎡` 금지 | — |

**언급되지만 포함되지 않은 스킬** — `ggi-collect` · `ggi-running-collect` · `ggi-doc-download` · `ggi-interest-npl-scan` · `suhyup-npl-daily-scan` · `coefficient-auto-update` · `coefficient-self-diagnosis` · `bid-win-curve` · `mutation-test-guard`.
지지옥션 유료 로그인·사내 낙찰 DB·무인 예약작업이 전제라 수강생 환경에서는 돌지 않습니다. 본문에서 이 이름을 만나면 「강사는 이렇게 자동화한다」로 읽고 넘어가면 됩니다.

---

## 설치 — 폴더 25개를 그대로 복사

Claude Code(데스크탑 앱 Code 탭)는 스킬을 **`%USERPROFILE%\.claude\skills\<스킬 이름>\SKILL.md`** 로 읽습니다 `[확정 — 2026-09-30 실측]`.
이 폴더(`NPL/skills/`)는 이미 그 구조입니다 — **폴더 이름 = 스킬 이름**, 안에 `SKILL.md` 와 참조 파일.

| 순서 | 할 일 |
|---|---|
| **1** | 저장소 첫 화면 **`<> Code` → `Download ZIP`** → 압축 해제 ([08단원 「받는 법」](../../08_NPL전문가.md)) |
| **2** | 탐색기 주소창에 `%USERPROFILE%\.claude\skills` 를 입력해 연다 (없으면 만든다) |
| **3** | ZIP 의 `NPL\skills\` 안 **폴더 25개**를 선택해 붙여 넣는다 (`README.md` 는 빼도 된다). 같은 이름이 있으면 **덮어쓰기** |
| **4** | Code 새 세션에서 「설치된 스킬 목록 보여줘」 → 25개 |

> [!IMPORTANT]
> 여러 파일짜리 스킬(`npl-analysis\references\`, `npl-purchase-letter\assets\` 등)은 **폴더 안 파일을 전부** 복사해야 합니다. `SKILL.md` 만 옮기면 본문이 참조하는 표·템플릿을 못 찾습니다.
> **백업은 `skills\` 밖에** 둡니다(`%USERPROFILE%\.claude\skills_backup\<이름>_날짜\`). `skills\` 안에 두면 같은 스킬이 두 번 뜹니다 `[확정 — 2026-09-30 실측]`.

> [!NOTE]
> [skills_skill파일/](../skills_skill파일/) 의 `.skill` 25개는 **Cowork·웹용**입니다. Code 는 폴더를 그대로 씁니다. 두 방법으로 같은 스킬을 이중 설치하지 마세요.

---

## 설치 후 확인

Code 새 세션을 열고:

```
설치된 스킬 목록 보여줘
```

25개가 다 보이면 됩니다. 이름이 겹치는 6개는 하나씩만 있어야 합니다.

```
npl-analysis 스킬의 첫 줄 수강생판 안내를 읽어줘
```

「작업 루트 C:\AI\NPL」 이 나오면 강사 원본이 아니라 수강생판이 설치된 것입니다.

---

## 알아둘 것

- 스킬 본문의 **계수·실측치는 강사 표본의 스냅샷 [추정]** 입니다. 날짜가 적혀 있습니다. 6개월이 지나면 낡습니다.
- 스킬은 **판단 재료**를 만듭니다. 매입가·입찰가 결정은 본인이 합니다.
- 세율·한도·법령 수치는 답변할 때마다 원문으로 확인해야 `[확정]` 입니다.
- **25개 모두 수강생 환경에서 실행 검증 전(미검증)** 입니다. 안 되는 곳이 있으면 어느 스킬 몇 번째 단계에서 멈추는지 알려 주세요.
- AI 분석은 검토 출발점입니다. 실제 입찰·매입 전 등기부·매각물건명세서 원문과 전문가 확인이 필요합니다.
