# 10. NPL 전문가 트랙 — Cowork 프로젝트로 만들기

> [08단원](08_NPL전문가.md)과 **같은 지침·같은 스킬**을 **Cowork 의 「프로젝트」** 로 만드는 단원입니다. 08단원은 Code 탭(폴더 + `CLAUDE.md`) 전용이고, 이 단원은 명령어 창 없이 데스크탑 앱 화면만으로 합니다.
>
> 수강생이 할 일은 **폴더 준비 → 프로젝트 만들기 → 지침 붙여넣기 · 폴더 연결 → 스킬 내려받아 넣기 → 「이 물건 분석해줘」** 입니다.
>
> **누구를 위한 것인가** — 채권 매입가를 산정하고, 매수의향서를 내고, 낙찰 후 유입까지 세금을 비교해야 하는 분. 직접 낙찰만 하실 거면 [04단원](04_분석프로젝트.md)으로 충분합니다.

> [!IMPORTANT]
> **08단원(Code)과 10단원(Cowork) 중 하나만 고르세요.** 같은 `C:\AI\NPL` 폴더에 `CLAUDE.md`(08단원)가 있는 채로 Cowork 프로젝트에 연결하면, Cowork 가 그 파일도 읽어 **지침이 두 벌**이 됩니다 `[확정 — 2026-10-06 강사 실측: 폴더를 연결하자 그 폴더의 CLAUDE.md 본문이 대화에 붙음]`.
> 08단원을 하다가 이쪽으로 옮기면 `C:\AI\NPL\CLAUDE.md` 의 이름을 `CLAUDE.md.bak` 으로 바꾸세요.
> **PC 가 켜져 있고 Claude 앱이 열려 있어야** Cowork 가 내 PC 의 폴더·창고·도구를 씁니다 `[확정 — 2026-10-06 강사 실측]`.

**비유** — 프로젝트는 **전담 직원의 책상**입니다. 책상 위에 **업무 매뉴얼(지침)** · **서류함(폴더)** · **업무 수첩(메모리)** · **정기 업무(예정됨)** 가 놓여 있습니다.

---

## $\color{#d97757}{\textsf{0. 먼저 확인 — 03·05·07 이 끝나 있어야 합니다}}$

| 단원 | 이 트랙에서 쓰는 것 |
|---|---|
| [03. DuckDB 창고](03_DuckDB_데이터창고.md) | `C:\AI\경매창고.duckdb` — 실거래·건축물대장·공시가격·철도역. NPL 스킬 전부가 이 창고를 1순위로 봅니다 |
| [05. 도구 연결](05_연결도구_MCP.md) | korean-law · real-estate · datagokr · vworld-landuse · KakaoMap · PlayMCP · duckdb. 더 붙일 것은 [필요한MCP_NPL.md](NPL/mcp/필요한MCP_NPL.md) |
| [07. 개인 설정](07_개인설정.md) | **설정 → 프로필 칸** — 라벨 4종 · 금액 표기 · 금지 소스. NPL 지침은 이것을 **가리키기만** 합니다 |

> [!IMPORTANT]
> 07을 안 넣으면 NPL 지침에서 금액·라벨 규칙이 통째로 빠집니다. 확인: Cowork 새 대화에서 `내 개인 설정에 뭐라고 적혀 있어?`

---

## $\color{#d97757}{\textsf{1. 폴더 준비 — C:}\backslash\textsf{AI}\backslash\textsf{NPL}}$

템플릿과 검증기는 저장소 ZIP 에 들어 있습니다. 저장소 첫 화면 초록색 **`<> Code`** → **`Download ZIP`** → 압축을 풉니다.

```
https://github.com/dgkim3333-hash/auction-guide-kr
```

| 순서 | 할 일 | 이렇게 되면 성공 |
|---|---|---|
| **1** | 파일 탐색기에서 `C:\AI\NPL` 폴더를 만듭니다 | 빈 폴더 |
| **2** | ZIP 의 `NPL\_템플릿\` 폴더를 통째로 `C:\AI\NPL\_템플릿\` 로 복사 | `물건폴더_표준` · `물건카드_PPTX_기준` · `NPL수익률_교육용.xlsx` |
| **3** | `C:\AI\NPL\_도구` 폴더를 만들고 ZIP 의 `NPL\hooks\verify_property.py` 하나만 복사 | `C:\AI\NPL\_도구\verify_property.py` |
| **4** | `C:\AI\NPL\00_시장데이터` 빈 폴더를 만듭니다 | 내 낙찰 기록이 여기 쌓입니다 |

```
C:\AI\
 ├─ 경매창고.duckdb              ← 03단원 (그대로)
 └─ NPL\                          ← 이 트랙의 작업 폴더 (CLAUDE.md 는 두지 않는다)
     ├─ _템플릿\
     │   ├─ 물건폴더_표준\
     │   ├─ 물건카드_PPTX_기준\    ← 덱 모양 기준(README)
     │   └─ NPL수익률_교육용.xlsx
     ├─ _도구\
     │   └─ verify_property.py      ← 빠짐 검사기 (5절)
     ├─ 00_시장데이터\
     └─ <소재지 전체주소>\         ← 물건 하나에 폴더 하나
         ├─ 00_물건카드.md
         ├─ 01_원본서류\
         ├─ 02_분석\
         ├─ 03_산출물\
         └─ 백업\
```

> [!NOTE]
> 08단원의 `property_analysis_guard.py` · `test_property_analysis_guard.py` 는 **Code 훅 전용**이라 이 단원에서는 쓰지 않습니다.

---

## $\color{#d97757}{\textsf{2. 프로젝트 만들기 — 지침 붙여넣기 · 폴더 연결}}$

| 순서 | 할 일 | 이렇게 되면 성공 |
|---|---|---|
| **1** | 데스크탑 앱 왼쪽 **`프로젝트`** 옆 **`+`** → **`Start from scratch`(처음부터 시작)** | 새 프로젝트 입력 창 |
| **2** | 이름: `NPL 매입·직접낙찰` · 저장 위치: `C:\AI\NPL` → 만들기 | 프로젝트 화면 (오른쪽에 지침 · 메모리 · 컨텍스트 · 폴더 · 예정됨) |
| **3** | [NPL/프로젝트지침_Cowork.md](NPL/프로젝트지침_Cowork.md) 를 열어 🔴 **세 곳**을 고친 본문을 준비합니다 (③은 개인 명의로도 볼 때만) | 고친 본문 |
| **4** | 오른쪽 **`지침`** 의 연필 아이콘 → 그 본문을 붙여넣고 저장 | 지침 칸 첫 줄이 「당신은 ○○(○○)의 경매·공매 물건 분석 담당이다」 |
| **5** | 오른쪽 **`폴더`** 의 `+` → `C:\AI\NPL` 추가 | 폴더 목록에 `NPL` |
| **6** | 프로젝트 입력창(`Cowork` 선택)에 `이 프로젝트 지침 첫 줄과 연결된 폴더, C:\AI\NPL\_도구 에 있는 파일을 알려줘` | 지침 첫 줄 · `C:\AI\NPL` · `verify_property.py` 가 나옴 |

[스크린샷 삽입: NPL 프로젝트 화면 — 오른쪽 지침 · 메모리 · 컨텍스트 · 폴더 · 예정됨 패널]

> [!NOTE]
> **붙여넣는 것은 `프로젝트지침_Cowork.md` 의 회색 상자 안 본문입니다.** 상자의 첫 줄(`markdown` 이라고 적힌 백틱 줄)과 마지막 줄(백틱만 있는 줄)은 빼고 「당신은」부터 마지막 「자주 쓰는 요청 문구」 줄까지 붙입니다. 아래쪽 대조표는 붙이지 않습니다.
> 08단원용 `프로젝트지침.md` 가 아니라 **`_Cowork` 가 붙은 파일**입니다. 분석 규칙은 같고, 훅·검증기 경로·개인 설정·도표 글꼴만 Cowork 에 맞췄습니다.
> 지침을 고친 뒤에는 프로젝트 안에서 **새 대화**를 여세요. 메뉴 이름은 앱 버전에 따라 다를 수 있습니다(영문 `Projects` · `Instructions` · `Context`).
> 프로젝트 만들기 메뉴: support.claude.com/en/articles/14116274 (2026-10-06 조회).

---

## $\color{#d97757}{\textsf{3. 스킬 40개 — 이 표에서 바로 내려받기}}$

링크를 누르면 `.skill` 파일이 바로 내려받아집니다. **압축을 풀지 말고 `.skill` 파일 그대로** 앱에 넣습니다. 내용은 저장소 `NPL/skills/` 폴더판과 같습니다(2026-10-05 저녁판 포함).

**한 번에 받기**
- [⬇ NPL_스킬_수강생용_26개.zip](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/NPL_%EC%8A%A4%ED%82%AC_%EC%88%98%EA%B0%95%EC%83%9D%EC%9A%A9_26%EA%B0%9C.zip) — **처음이면 이것.** 강사 운영 14개를 뺀 26개
- [⬇ NPL_스킬_40개_전체.zip](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/NPL_%EC%8A%A4%ED%82%AC_40%EA%B0%9C_%EC%A0%84%EC%B2%B4.zip) — 강사 운영 스킬까지 40개 (아래 표 「강사 운영」은 유료 로그인·사내 DB 전제라 그대로는 안 돌 수 있음)

zip 은 풀면 `.skill` 파일들이 나옵니다. 그 `.skill` 들은 **다시 풀지 않습니다.**

| 내려받기 | 언제 쓰나 | 구분 |
|---|---|---|
| **핵심 분석** | | |
| [⬇ npl-analysis.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-analysis.skill) | **NPL 매입 건의 주 절차.** 21개 체크리스트 · 배당표 · 매입가 · 추정 감정가 · 임대 가정 · 유입 총투입 … | 수강생용 |
| [⬇ auction-property-card.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/auction-property-card.skill) | **직접낙찰 건의 주 절차.** 서류 판독 → 권리 → 세금 → PPTX 물건카드 | 수강생용 |
| [⬇ auction-property-review.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/auction-property-review.skill) | 직접낙찰 물건 검토 체크리스트 — 24개 위험항목(임차인 vs 조세 법정기일 포함) · 배당·인수금액 · 입찰 상한 · 별… | 수강생용 |
| [⬇ auction-bid-price.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/auction-bid-price.skill) | 입찰가 범위 · 【A】【B】 계수 · 포기 판정 | 수강생용 |
| [⬇ priority-payment-date-rule.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/priority-payment-date-rule.skill) | 소액임차인 최우선변제 — 기준일 · 시기별 한도 내장표 | 수강생용 |
| [⬇ property-tax-apportionment.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/property-tax-apportionment.skill) | 주택·근생 복합 공시가격 확보 · 세목별 안분 | 수강생용 |
| [⬇ real-estate-tax-calculator.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/real-estate-tax-calculator.skill) | 취득세·재산세·종부세·양도세 · 세후 IRR | 수강생용 |
| **유형별 추가 체크** | | |
| [⬇ residential-auction.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/residential-auction.skill) | 다가구·다세대·연립·아파트 | 수강생용 |
| [⬇ commercial-unit-auction.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/commercial-unit-auction.skill) | 구분상가·오피스 호실 | 수강생용 |
| [⬇ land-auction.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/land-auction.skill) | 토지 | 수강생용 |
| [⬇ small-building-auction.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/small-building-auction.skill) | 꼬마빌딩 | 수강생용 |
| **NPL 전용** | | |
| [⬇ npl-excel-fill-map.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-excel-fill-map.skill) | NPL수익률.xlsx 입력 칸 정본 매핑 | 수강생용 |
| [⬇ npl-purchase-letter.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-purchase-letter.skill) | 매수의향서 .docx 생성·검증 (A4 1페이지) | 수강생용 |
| [⬇ trust-npl-analysis.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/trust-npl-analysis.skill) | 담보신탁 NPL 우선수익권 매입 분석 | 수강생용 |
| [⬇ trust-npl-routine.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/trust-npl-routine.skill) | 신탁 NPL 1주 Stage-Gate 루틴 | 수강생용 |
| [⬇ corporate-debtor-bankruptcy-check.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/corporate-debtor-bankruptcy-check.skill) | 법인 채무자 회생·파산 리스크 4단계 | 수강생용 |
| [⬇ post-auction-loan-simulator.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/post-auction-loan-simulator.skill) | 낙찰 후 대출 시뮬레이션 · DSCR · 임계 LTV | 수강생용 |
| [⬇ post-auction-eviction.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/post-auction-eviction.skill) | 낙찰 후 명도 D+7~D+90 · 인도명령서·내용증명 생성 | 수강생용 |
| [⬇ onbid-api-caller.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/onbid-api-caller.skill) | 온비드 API 호출 규칙 | 수강생용 |
| [⬇ bid-result-log.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/bid-result-log.skill) | 입찰 결과·2순위 기록 · 예측 오차 누적 | 수강생용 |
| **서류·파일** | | |
| [⬇ npl-doc-intake.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-doc-intake.skill) | 서류 자동 분류 · 표준 파일명 · 새 물건 폴더 | 수강생용 |
| [⬇ npl-file-hygiene.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-file-hygiene.skill) | 백업 정리 · 두 폴더 대조 · 유실 탐지 | 수강생용 |
| **산출물** | | |
| [⬇ number-format-guard.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/number-format-guard.skill) | 원 단위 풀 콤마 · 비율 옆 금액 · 피벗 서식 재검증 | 수강생용 |
| [⬇ npl-svg-chart.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-svg-chart.skill) | 권리 사다리 · 문건 타임라인 · 배당 폭포 (당해세 주황 배지) | 수강생용 |
| [⬇ npl-diagram.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/npl-diagram.skill) | draw.io 편집 가능 도표 | 수강생용 |
| [⬇ pptx-blue-design-system.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/pptx-blue-design-system.skill) | PPTX 16:9 5존 · 블루 팔레트 · `㎡` 금지 | 수강생용 |
| **강사 운영 · 수집 자동화** | | |
| [⬇ ggi-collect.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/ggi-collect.skill) | 지지옥션 입찰당일 결과(응찰자수·유찰) 수집 → 낙찰 DB 적재 | 강사 운영 |
| [⬇ ggi-newlist-collect.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/ggi-newlist-collect.skill) | 지지옥션 서울·경기 업무상업 신건 수집 → 탐색 엑셀 | 강사 운영 |
| [⬇ ggi-running-collect.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/ggi-running-collect.skill) | 진행 중 유찰 1~4회 물건 + 예상승률 → 탐색 엑셀 | 강사 운영 |
| [⬇ ggi-doc-download.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/ggi-doc-download.skill) | 지지옥션 서류 PDF 받아 물건 폴더에 저장 | 강사 운영 |
| [⬇ ggi-interest-npl-scan.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/ggi-interest-npl-scan.skill) | 관심물건 신규분 NPL 매입 분석 · 수익률 엑셀·의향서·PPTX | 강사 운영 |
| [⬇ lender-auction-radar.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/lender-auction-radar.skill) | 신협·수협·저축은행·새마을금고 채권자 경매신청 레이더 엑셀 | 강사 운영 |
| [⬇ suhyup-npl-daily-scan.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/suhyup-npl-daily-scan.skill) | 수협NPL 채권매각 공고 일일 스캔 · 신규 건 분석 | 강사 운영 |
| [⬇ suhyup-npl-consolidator.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/suhyup-npl-consolidator.skill) | 수협 NPL 개별 엑셀 → 전체현황 마스터 통합 | 강사 운영 |
| [⬇ shinhyup-npl-consolidator.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/shinhyup-npl-consolidator.skill) | 신협 NPL 개별 엑셀 → 전체현황 마스터 통합 | 강사 운영 |
| [⬇ coefficient-auto-update.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/coefficient-auto-update.skill) | 낙찰 계수 재추정 · 게이트 통과분만 `auction-bid-price` 반영 | 강사 운영 |
| [⬇ coefficient-self-diagnosis.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/coefficient-self-diagnosis.skill) | 계수 홀드아웃 자가진단 · 편향 가설 등록 | 강사 운영 |
| [⬇ bid-win-curve.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/bid-win-curve.skill) | 경쟁 최고가 분포로 입찰가율별 승률·기대이익 | 강사 운영 |
| [⬇ pipeline-health-check.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/pipeline-health-check.skill) | 수집·계수 자동화가 멈췄는지 주간 점검 | 강사 운영 |
| [⬇ excel-explore-sheet.skill](https://github.com/dgkim3333-hash/auction-guide-kr/raw/main/NPL/skills_skill%ED%8C%8C%EC%9D%BC/excel-explore-sheet.skill) | 슬라이서로 좁히면 목록이 펼쳐지는 탐색 시트 엑셀 | 강사 운영 |

**Cowork 에 넣는 법** — 둘 중 하나 `[검증필요 — 메뉴 이름은 앱 버전에 따라 다름 · 수강생 PC 실측 전]`

| 방법 | 할 일 | 이렇게 되면 성공 |
|---|---|---|
| **가. 설정에서 올리기** | 데스크탑 앱 왼쪽 아래 내 이름 → **설정** → **기능(Capabilities)** 의 **스킬** → **업로드** → `.skill` 선택 (여러 개면 하나씩) | 스킬 목록에 이름이 생김 |
| **나. 대화에 첨부** | Cowork 새 대화에 `.skill` 파일들을 끌어다 놓고 `이 스킬들을 저장해줘` | 저장 확인 → 승인 |

확인: 새 대화에서 「설치된 스킬 목록 보여줘」 → 넣은 이름이 나오면 성공. **같은 스킬을 두 방법으로 두 번 넣지 마세요.**

> [!IMPORTANT]
> 스킬을 새로 넣거나 바꿨으면 **새 대화**에서 분석합니다. 대화는 시작할 때 받아 둔 스킬로 돕니다 `[추정 — 강사 실측]`.
> 스킬별 필요한 도구는 [NPL/skills/README.md](NPL/skills/README.md) 의 「필요한 것」 열을 봅니다.

---

## $\color{#d97757}{\textsf{4. 도구(MCP) 확인}}$

05단원에서 `claude_desktop_config.json` 에 넣은 도구는 Cowork 대화에도 붙습니다 `[확정 — 2026-10-06 강사 실측: Cowork 대화에서 duckdb MCP 호출]`. PlayMCP 는 claude.ai 커넥터라 자동입니다.

프로젝트 입력창 왼쪽 **`+`** → **`Connectors`** 에서 켜져 있는지 봅니다: **duckdb · korean-law · real-estate · datagokr · vworld-landuse · PlayMCP**. NPL 트랙에서 더 붙일 것(Excel·Word 도구 등)과 없을 때 대안은 [필요한MCP_NPL.md](NPL/mcp/필요한MCP_NPL.md), 설정 파일 완성본은 [claude_desktop_config_NPL.json](NPL/mcp/claude_desktop_config_NPL.json) 입니다.

---

## $\color{#d97757}{\textsf{5. 빠짐 검사 — Cowork 에는 훅이 없습니다}}$

08단원(Code)은 훅 2개가 **체크리스트를 자동으로 넣고, 검사를 통과하기 전에는 끝내지 못하게** 막습니다. Cowork 에는 이 장치가 없습니다.
그래서 Cowork 판 지침은 Claude 에게 **스스로** 하게 합니다 — 답변 첫머리에 필수 절차 8단계를 적고, 산출물을 만든 뒤 `C:\AI\NPL\_도구\verify_property.py` 를 돌려 「VERIFY_PROPERTY PASS」를 확인한 다음에 「완료」라고 쓰도록.

**자동으로 막아 주지는 않습니다.** 끝났다는 보고에 PASS 줄이 없으면 이렇게 요청하세요.

```
끝내기 전에 C:\AI\NPL\_도구\verify_property.py 로 이 물건 폴더를 검사하고 결과 전체를 보여줘. FAIL 이 있으면 그 항목부터 채워줘.
```

정말 해당 없는 항목(예: 집합건물이라 토지 등기부 없음)만 물건 폴더에 `_검증예외.md` 를 만들고 `- 서류_토지등기: 집합건물이라 토지 등기부 없음` 처럼 **검사ID 와 사유**를 적습니다.

> [!CAUTION]
> **검증기 PASS 는 「빠진 항목이 없다」는 뜻이지 「결론이 맞다」는 뜻이 아닙니다.** 표현이 있는지만 봅니다.

---

## $\color{#d97757}{\textsf{6. 써 보기 — 자주 쓰는 요청 문구}}$

왼쪽 `프로젝트` → `NPL 매입·직접낙찰` → 입력창(`Cowork` 선택)에서:

```
C:\AI\NPL\<소재지> 폴더의 서류로 이 물건 분석해줘
```

```
이 NPL 매입할까요. 유입 시나리오 세금까지 넣어줘
```

```
물건카드 만들어줘. 개인·법인 두 경우로 세금 넣어줘
```

```
민감도 슬라이드 넣어줘. 낙찰가율 ±5%p로
```

```
낙찰됐어. 명도 계획 만들어줘
```

```
패찰했어. 낙찰가 000원, 응찰 0명, 2순위 000원
```

**이렇게 되면 성공** — 답변 첫머리에 절차 판별(법원경매 / 압류재산 공매)과 필수 절차 8단계가 나오고, 관점 1(NPL 매입)·관점 2(직접 낙찰)를 둘 다 다루며, `03_산출물` 에 PPTX, `02_분석` 에 NPL수익률 엑셀이 생기고, 마지막에 「VERIFY_PROPERTY PASS」가 보입니다.

---

## $\color{#d97757}{\textsf{안 될 때}}$

| 증상 | 원인 | 해결 |
|---|---|---|
| 지침을 무시하는 것 같다 | 지침을 저장하기 전에 연 대화 | 프로젝트 안에서 **새 대화** |
| 「폴더를 볼 수 없다」 · 서류를 못 찾는다 | 프로젝트에 `C:\AI\NPL` 을 연결하지 않음 | 2절 5번 |
| 지침이 두 번 적용된 것 같다 · 「훅」 이야기를 한다 | `C:\AI\NPL\CLAUDE.md`(08단원)가 남아 있음 | 이름을 `CLAUDE.md.bak` 으로 → 새 대화 |
| 「검증기 미실행」이라고 보고한다 | `_도구\verify_property.py` 가 없음 | 1절 3번 → 5절 요청 문구 |
| 검증기에서 `No module named pptx` | 작업 환경에 패키지가 없음 | 「python-pptx 와 openpyxl 을 설치하고 다시 돌려줘」 |
| 「○○ 스킬 없음」 | 스킬을 안 넣었거나 이름이 다름 | 3절 — 「설치된 스킬 목록 보여줘」 |
| 「창고 미조회」가 계속 나온다 | duckdb 도구가 꺼져 있거나 설정 파일에 없음 | 입력창 `+` → `Connectors` → [03단원](03_DuckDB_데이터창고.md) · [05단원](05_연결도구_MCP.md) |
| PC 의 파일·창고를 전혀 못 읽는다 | PC 가 꺼졌거나 Claude 앱이 닫힘 | 켜 둔 상태에서 다시 요청 |
| 「NPL수익률.xlsx 없음」 | 템플릿을 안 넣음 | 1절 2번 — `_템플릿\NPL수익률_교육용.xlsx` |
| 의향서에 회사명이 `[내 회사명]` 그대로 | 고정 정보 미입력 | npl-purchase-letter 「고정 정보」 표 |
| ggi-*·coefficient-*·bid-win-curve 가 로그인·DB 오류로 멈춘다 | 강사 운영 스킬은 유료 로그인·사내 DB 전제 | 정상. 참고용으로 읽고 그 단계는 건너뜀 |
| 금액이 억·만으로 나온다 · 라벨이 없다 | 개인 설정(설정 → 프로필)을 안 넣음 | [07단원](07_개인설정.md) |
| 도표의 한글이 전부 □ 다 | 도표 글꼴 첫 항목이 작업 환경에 없음 | `_charts.py` 의 font-family 첫 항목을 `Noto Sans CJK KR` 로 |
| 배당표가 당해세 → 최우선변제 순으로 나온다 | 2026-10-05 이전 스킬 | 3절에서 스킬 다시 넣기 → 새 대화 |

---

## $\color{#d97757}{\textsf{조심할 것}}$

- **매입가·의향서는 실제 돈이 걸린 산출물입니다.** 스킬이 낸 숫자는 검토 출발점이지 결정이 아닙니다.
- 계수는 전부 **[추정]** 이고 강사 표본입니다. 내 지역·시기에 맞지 않을 수 있습니다.
- 의향서·엑셀에 **채무자·임차인 실명을 남기지 마세요.** 외부로 나가는 문서입니다.
- 법령·세율은 스킬에 적혀 있어도 **답변할 때마다 원문으로 확인**해야 `[확정]` 입니다.
- 지침은 **그 프로젝트 안의 대화에만** 붙습니다. 프로젝트 밖에서 연 대화에는 개인 설정만 남습니다.
- Cowork 에는 빠짐 검사 **자동 차단이 없습니다.** 끝났다는 보고에 PASS 줄이 있는지 직접 보세요.
- AI 분석은 검토 출발점입니다. 실제 입찰·매입 전 등기부·매각물건명세서 원문과 전문가 확인이 필요합니다.

**Code 탭으로 하실 분 → [08. NPL 전문가 트랙 (Code)](08_NPL전문가.md)**

---

출처

- support.claude.com/en/articles/14116274 — Organize your tasks with projects in Claude Cowork (2026-10-06 조회)
- Cowork 에서 PC 의 MCP(duckdb) 호출 · 연결 폴더의 CLAUDE.md 를 읽음 · Cowork 가 `%USERPROFILE%\.claude` 폴더를 열지 못함 · 작업 환경 글꼴(Noto Sans CJK KR) · python-pptx·openpyxl 사용 가능: 2026-10-06 강사 실측
- 계수·실측치: 강사 실무 운영 기록. 특정 지역·기간 표본이며 [추정]
