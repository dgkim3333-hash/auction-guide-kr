# NPL 트랙 스킬 45개

[08단원](../../08_NPL전문가.md) NPL 프로젝트가 부르는 스킬과 강사가 경매·NPL 업무에 쓰는 운영 스킬 전부입니다. 강사 운영본을 **경로·회사 식별정보만 바꿔** 옮겼습니다(2026-10-02 전체 동기화).
모든 스킬 첫머리에 「수강생판 안내」가 붙어 있습니다 — 무엇이 강사 환경 전용이고 무엇을 대신 쓰는지 적어 두었습니다.

> [!IMPORTANT]
> 04단원 스킬(10개)과 이름이 겹치는 8개는 **이 폴더 것으로 덮어쓰세요.** (`npl-deck-standard` 는 두 곳이 같은 파일) NPL판이 원본 그대로라 내용이 더 많습니다.
> `auction-failure-guard` 는 **NPL판 하나만 설치**합니다(경매판 포함 — 모드 A). 나중에 04단원 경매판으로 덮어쓰면 NPL 매입 분석(모드 B)이 사라집니다.
> `auction-analysis`(경매종합분석)는 NPL판에 없습니다. `npl-analysis` 가 그 자리를 맡습니다.

## $\color{#d97757}{\textsf{목록}}$

| 스킬 (폴더명 = 스킬 이름) | 파일 | 언제 쓰나 | 필요한 것 |
|---|---|---|---|
| **핵심 분석** | | | |
| `npl-analysis` | 9 | **NPL 매입 건의 주 절차.** 21개 체크리스트 · 배당표 · 매입가 · 추정 감정가 · 임대 가정 · 유입 총투입 · 대출 판정 | 창고 · real-estate · korean-law · ecos(선택) · rone(선택) |
| `auction-property-card` | 1 | **직접낙찰 건의 주 절차.** 서류 판독 → 권리 → 세금 → PPTX 물건카드 | 창고 · vworld · datagokr · KakaoMap |
| `auction-property-review` | 4 | 직접낙찰 물건 검토 체크리스트 — 24개 위험항목(임차인 vs 조세 법정기일 포함) · 배당·인수금액 · 입찰 상한 · 별점 종합의견 (2026-10-02 추가) | korean-law · 창고(선택) |
| `auction-bid-price` | 5 | 입찰가 범위 · 【A】【B】 계수 · 포기 판정 | 없음 (계수는 정적 스냅샷 [추정]) |
| `auction-failure-guard` | 4 | **결론 전 마지막 게이트.** 실패사례 118건 → 11개 유형 점검표 · 직접 입찰 3게이트(모드 A) · NPL 회수 경로 5개(모드 B) · 반려 권고 사유 (2026-10-06 추가) | korean-law (법리 재조회) |
| `priority-payment-date-rule` | 1 | 소액임차인 최우선변제 — 기준일 · 시기별 한도 내장표 | korean-law |
| `property-tax-apportionment` | 1 | 주택·근생 복합 공시가격 확보 · 세목별 안분 | vworld · 창고 |
| `real-estate-tax-calculator` | 7 | 취득세·재산세·종부세·양도세 · 세후 IRR | korean-law · vworld |
| **유형별 추가 체크** | | | |
| `residential-auction` | 5 | 다가구·다세대·연립·아파트 | — |
| `commercial-unit-auction` | 5 | 구분상가·오피스 호실 | — |
| `land-auction` | 6 | 토지 | vworld |
| `small-building-auction` | 1 | 꼬마빌딩 | — |
| **NPL 전용** | | | |
| `npl-tenant-rent-check` | 1 | 다가구·다세대 임차인 대조 · 전입세대 · 월세 연체 공제(회수 0원) · 월세 압류 · 배당이의 · 양수도계약서 대조 (2026-10-08 추가) | korean-law |
| `npl-tax-arrears-closing` | 1 | 당해 연도 재산세·종부세 당해세 · 압류 세목 판정 · 계약일·잔금일·법무사 체크리스트 · 자금 계획 부록 D · 근질권대출 서류 (2026-10-08 추가) | korean-law · vworld · NPL수익률 템플릿 |
| `npl-cross-collateral-shortfall` | 1 | **npl-analysis 와 항상 함께.** 토지 : 건물 비율 · 교차 담보 잉여 배분과 엑셀 연결 · 잔존채권 추심 장 · 선순위 국세 판정·민감도 · 전입 차단 계약 조항 장 (2026-10-07 추가) | korean-law · NPL수익률 템플릿 |
| `npl-excel-fill-map` | 1 | NPL수익률.xlsx 입력 칸 정본 매핑 | **Excel MCP** · NPL수익률 템플릿 |
| `npl-purchase-letter` | 4 | 매수의향서 .docx 생성·검증 (A4 1페이지) | **Word MCP** · 의향서 템플릿(동봉) |
| `trust-npl-analysis` | 6 | 담보신탁 NPL 우선수익권 매입 분석 | real-estate · ecos(선택) |
| `trust-npl-routine` | 10 | 신탁 NPL 1주 Stage-Gate 루틴 | 위 스킬들 |
| `corporate-debtor-bankruptcy-check` | 5 | 법인 채무자 회생·파산 리스크 4단계 | nts · nps · fsc · iros · naver-search (선택 — 없으면 수동) |
| `post-auction-loan-simulator` | 5 | 낙찰 후 대출 시뮬레이션 · DSCR · 임계 LTV | Excel MCP · ecos(선택) |
| `post-auction-eviction` | 10 | 낙찰 후 명도 D+7~D+90 · 인도명령서·내용증명 생성 | Word MCP |
| `onbid-api-caller` | 2 | 온비드 API 호출 규칙 | datagokr · real-estate |
| `bid-result-log` | 1 | 입찰 결과·2순위 기록 · 예측 오차 누적 | 없음 (`00_시장데이터\` 에 기록) |
| **서류·파일** | | | |
| `npl-doc-intake` | 2 | 서류 자동 분류 · 표준 파일명 · 새 물건 폴더 | `_템플릿\물건폴더_표준` |
| `npl-file-hygiene` | 2 | 백업 정리 · 두 폴더 대조 · 유실 탐지 | — |
| **산출물** | | | |
| `number-format-guard` | 1 | 원 단위 풀 콤마 · 비율 옆 금액 · 피벗 서식 재검증 · 표 열 단위 정렬 (2026-10-07) | — |
| `npl-svg-chart` | 1 | 권리 사다리 · 문건 타임라인 · 배당 폭포 (당해세 주황 배지) | cairosvg |
| `npl-diagram` | 1 | draw.io 편집 가능 도표 | — |
| `pptx-blue-design-system` | 1 | PPTX 16:9 5존 · 블루 팔레트 · `㎡` 금지 | — |
| `npl-deck-standard` | 7 | **물건카드·NPL 브리핑 PPTX를 만들 때 항상.** 모양·장 순서 표준 + 생성기·도표 견본(가상 데이터 14장 덱). `pptx-blue-design-system`·덱 기준 README보다 우선 (2026-10-08 추가) | pptxgenjs · cairosvg(없으면 Windows Edge) |
| **강사 운영 · 수집 자동화** (유료 로그인·사내 DB·예약작업 전제 — 그대로는 안 돌 수 있음) | | | |
| `ggi-collect` | 1 | 지지옥션 입찰당일 결과(응찰자수·유찰) 수집 → 낙찰 DB 적재 | 지지옥션 유료 로그인 · Chrome · duckdb |
| `ggi-newlist-collect` | 1 | 지지옥션 서울·경기 업무상업 신건 수집 → 탐색 엑셀 | 지지옥션 · `excel-explore-sheet` |
| `ggi-running-collect` | 1 | 진행 중 유찰 1~4회 물건 + 예상승률 → 탐색 엑셀 | 지지옥션 · 승률표 스크립트 |
| `ggi-doc-download` | 1 | 지지옥션 서류 PDF 받아 물건 폴더에 저장 | 지지옥션 · PDF Tools |
| `ggi-interest-npl-scan` | 1 | 관심물건 신규분 NPL 매입 분석 · 수익률 엑셀·의향서·PPTX | 지지옥션 · Excel·Word MCP · 계수이력 |
| `lender-auction-radar` | 1 | 신협·수협·저축은행·새마을금고 채권자 경매신청 레이더 엑셀 | 지지옥션 · Excel MCP |
| `suhyup-npl-daily-scan` | 1 | 수협NPL 채권매각 공고 일일 스캔 · 신규 건 분석 | 수협NPL 사이트 · Excel·Word MCP |
| `suhyup-npl-consolidator` | 1 | 수협 NPL 개별 엑셀 → 전체현황 마스터 통합 | Excel |
| `shinhyup-npl-consolidator` | 3 | 신협 NPL 개별 엑셀 → 전체현황 마스터 통합 | Excel · Python |
| `coefficient-auto-update` | 1 | 낙찰 계수 재추정 · 게이트 통과분만 `auction-bid-price` 반영 | 사내 낙찰 DB · `calc_coeff.py` |
| `coefficient-self-diagnosis` | 1 | 계수 홀드아웃 자가진단 · 편향 가설 등록 | 사내 낙찰 DB |
| `bid-win-curve` | 1 | 경쟁 최고가 분포로 입찰가율별 승률·기대이익 | 지지옥션 낙찰 DB |
| `pipeline-health-check` | 1 | 수집·계수 자동화가 멈췄는지 주간 점검 | 예약작업 · 사내 DB |
| `excel-explore-sheet` | 1 | 슬라이서로 좁히면 목록이 펼쳐지는 탐색 시트 엑셀 | Excel · 검증 스크립트 |

**강사 운영 스킬 14개**(위 표 마지막 묶음)는 지지옥션 유료 로그인·강사 사내 낙찰 DB(`00_시장데이터\`)·수집 스크립트(`calc_coeff.py`·`load_ggi_csv.py`·`win_rate_table.py` 등)·무인 예약작업이 전제입니다. 스크립트와 DB는 저장소에 없습니다. **구조를 보는 참고용**으로 읽고, 내 환경에 맞춰 고쳐 쓰세요. `mutation-test-guard` 는 경매 전용이 아니라 넣지 않았습니다.

---

## $\color{#d97757}{\textsf{설치 — 폴더 45개를 그대로 복사}}$

Claude Code(데스크탑 앱 Code 탭)는 스킬을 **`%USERPROFILE%\.claude\skills\<스킬 이름>\SKILL.md`** 로 읽습니다 `[확정 — 2026-09-30 실측]`.
이 폴더(`NPL/skills/`)는 이미 그 구조입니다 — **폴더 이름 = 스킬 이름**, 안에 `SKILL.md` 와 참조 파일.

| 순서 | 할 일 |
|---|---|
| **1** | 저장소 첫 화면 **`<> Code` → `Download ZIP`** → 압축 해제 ([08단원 「받는 법」](../../08_NPL전문가.md)) |
| **2** | 탐색기 주소창에 `%USERPROFILE%\.claude\skills` 를 입력해 연다 (없으면 만든다) |
| **3** | ZIP 의 `NPL\skills\` 안 **폴더 45개**를 선택해 붙여 넣는다 (`README.md` 는 빼도 된다). 같은 이름이 있으면 **덮어쓰기** |
| **4** | Code 새 세션에서 「설치된 스킬 목록 보여줘」 → 45개 |

> [!IMPORTANT]
> 여러 파일짜리 스킬(`npl-analysis\references\`, `npl-purchase-letter\assets\` 등)은 **폴더 안 파일을 전부** 복사해야 합니다. `SKILL.md` 만 옮기면 본문이 참조하는 표·템플릿을 못 찾습니다.
> **백업은 `skills\` 밖에** 둡니다(`%USERPROFILE%\.claude\skills_backup\<이름>_날짜\`). `skills\` 안에 두면 같은 스킬이 두 번 뜹니다 `[확정 — 2026-09-30 실측]`.

> [!NOTE]
> [skills_skill파일/](../skills_skill파일/) 의 `.skill` 45개는 **Cowork·웹용**입니다(2026-10-09 판 — 이 폴더판과 같은 내용). Code 는 폴더를 그대로 씁니다. 두 방법으로 같은 스킬을 이중 설치하지 마세요.

---

## $\color{#d97757}{\textsf{설치 후 확인}}$

Code 새 세션을 열고:

```
설치된 스킬 목록 보여줘
```

45개가 다 보이면 됩니다. 이름이 겹치는 8개(auction-failure-guard · npl-deck-standard 추가 — NPL판으로 덮어쓰기)는 하나씩만 있어야 합니다.

```
npl-analysis 스킬의 첫 줄 수강생판 안내를 읽어줘
```

「작업 루트 C:\AI\NPL」 이 나오면 강사 원본이 아니라 수강생판이 설치된 것입니다.

---

## $\color{#d97757}{\textsf{알아둘 것}}$

- 스킬 본문의 **계수·실측치는 강사 표본의 스냅샷 [추정]** 입니다. 날짜가 적혀 있습니다. 6개월이 지나면 낡습니다.
- 스킬은 **판단 재료**를 만듭니다. 매입가·입찰가 결정은 본인이 합니다.
- 세율·한도·법령 수치는 답변할 때마다 원문으로 확인해야 `[확정]` 입니다.
- **45개 모두 수강생 환경에서 실행 검증 전(미검증)** 입니다. 안 되는 곳이 있으면 어느 스킬 몇 번째 단계에서 멈추는지 알려 주세요.
- AI 분석은 검토 출발점입니다. 실제 입찰·매입 전 등기부·매각물건명세서 원문과 전문가 확인이 필요합니다.
