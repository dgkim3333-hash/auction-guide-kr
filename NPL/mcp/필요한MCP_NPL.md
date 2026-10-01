# NPL 트랙에 필요한 MCP

05단원에서 붙인 것 위에 **필수 2개**를 더하고, 나머지는 **선택**입니다.
선택 MCP가 없어도 분석은 멈추지 않습니다 — 해당 값을 「미조회 `[검증필요]`」로 두고 진행하도록 스킬이 짜여 있습니다.

## $\color{#d97757}{\textsf{한눈에}}$

| 구분 | MCP | 어디서 | 쓰는 스킬 | 없으면 |
|---|---|---|---|---|
| **이미 있음 (05단원)** | `korean-law` | 05단원 | npl-analysis · property-card · tax 2종 · priority-rule · trust-routine | 법령을 기억에 의존 — 위험 |
| | `real-estate` | 05단원 | npl-analysis · property-card · trust 2종 · loan-sim · eviction · onbid | 시세 대조 불가 |
| | `datagokr` | 05단원 | property-card · tax · onbid · fill-map | 건축물대장·온비드 조회 불가 |
| | `vworld-landuse` | 05단원 | property-card · property-tax · tax-calculator · land-auction | 공시지가·좌표 불가 |
| | `KakaoMap` (커넥터) | 05단원 | property-card 역세권 실측 | 지하철 접근성 `[정보부족]` |
| | PlayMCP `kakaoRealEstate` | 04단원 | npl-analysis · property-card 시세 2순위 | 3순위 real-estate로 |
| | `duckdb` (창고) | 03단원 | 거의 전부 1순위 | 조회 도구로 폴백 |
| **추가 필수** | **Excel MCP** | claude-guide-kr 안내 | npl-excel-fill-map · loan-simulator · bid-result-log | NPL수익률 엑셀을 못 채운다 |
| | **Word MCP** (`word`) | 아래 | npl-purchase-letter · eviction 문서 | 의향서·명도 서류를 못 만든다 |
| **추가 선택** | `ecos` (한국은행) | 강사 제작 · 배포 준비 중 | npl-analysis 원칙 16 · trust · loan-sim | 한국은행 ECOS 웹에서 수동 조회 → `[검증필요]` |
| | `rone` (부동산원) | 강사 제작 · 배포 준비 중 | npl-analysis 원칙 12 (표본 부족 보조) | R-ONE 웹 수동 조회 |
| | `court-auction` | 강사 제작 · 배포 준비 중 | auction-bid-price 주변 조사 · eviction | 대법원 경매정보 웹 |
| | `nts` · `nps` · `fsc-financial-info` · `iros` | 강사 제작 · 배포 준비 중 | corporate-debtor-bankruptcy-check | 홈택스 · 국민연금 · DART 웹 **수동 조회 후 값 입력** |
| | `naver-search` | 공개 패키지 있음 (아래) | corporate-check 뉴스 정황 · fill-map | 뉴스 정황 생략 |
| | `korea-law-search` | 강사 제작 | eviction · corporate-check 판례 | `korean-law` 의 판례 검색으로 대체 |
| | `powerpoint` | Windows PowerPoint 필요 | property-card 파일 닫기 · svg-chart 삽입 | PPTX 파일을 직접 닫는다 |
| | `hwp` | 05단원 선택 | npl-doc-intake 한글 서류 | 한글 파일은 PDF로 바꿔 넣는다 |

> [!NOTE]
> 「강사 제작 · 배포 준비 중」 MCP는 강사가 자기 환경용으로 만든 것이라 아직 공개 저장소가 없습니다.
> 스킬 본문은 이 MCP가 **있으면 쓰고 없으면 건너뛰도록** 돼 있습니다. 배포되면 이 표를 갱신합니다.

---

## $\color{#d97757}{\textsf{추가 필수 1 — Word MCP (word)}}$

의향서(.docx)와 명도 서류를 만듭니다. 05단원 설정 파일 완성본에 이미 들어 있습니다. 없으면 아래를 `mcpServers` 안에 추가합니다.

```json
"word": {
  "command": "uvx",
  "args": ["--from", "word-mcp-live", "word_mcp_server.exe"],
  "env": { "MCP_AUTHOR": "Claude", "MCP_AUTHOR_INITIALS": "C", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1" }
}
```

## $\color{#d97757}{\textsf{추가 필수 2 — Excel MCP}}$

NPL수익률.xlsx 를 셀 단위로 채우고 서식을 읽어 검증합니다. **확장 프로그램(.mcpb)** 으로 설치합니다.
설치 방법은 [claude-guide-kr 05단원](https://github.com/dgkim3333-hash/claude-guide-kr/blob/main/05_MCP와API.md) 의 Excel MCP 항목을 따르세요.
Windows Excel 이 설치돼 있어야 하고, 작업 중에는 **그 파일을 Excel 에서 닫아 두어야** 합니다.

## $\color{#d97757}{\textsf{추가 선택 — naver-search}}$

법인 채무자 뉴스 정황 보조입니다. 공개 패키지가 있습니다 — 네이버 개발자센터에서 검색 API 키를 발급받습니다.

```json
"naver-search": {
  "command": "npx",
  "args": ["-y", "@isnow890/naver-search-mcp"],
  "env": { "NAVER_CLIENT_ID": "<<발급받은_ID>>", "NAVER_CLIENT_SECRET": "<<발급받은_Secret>>" }
}
```

`[검증필요]` — 패키지명·env 이름은 배포 시점 기준이며 npm 에서 최신 README 로 확인하세요.

---

## $\color{#d97757}{\textsf{설정 파일 완성본}}$

[claude_desktop_config_NPL.json](claude_desktop_config_NPL.json) — 05단원 완성본에 `word`·`duckdb`(창고)를 합친 것입니다.
`<< >>` 자리에 본인 키를 넣습니다. 설정 파일 전체를 남에게 보내지 마세요 — 키가 평문입니다.

설정 파일 위치와 여는 법은 [claude-guide-kr 크롬연결/README](https://github.com/dgkim3333-hash/claude-guide-kr/blob/main/크롬연결/README.md) 아래쪽과 05단원을 따르세요.
고치기 전 백업, 고친 뒤 **Claude 완전 종료 → 재실행 → 새 대화**입니다.

---

## $\color{#d97757}{\textsf{붙었는지 확인}}$

새 작업을 열고 순서대로:

```
DuckDB 창고 연결됐어? 실거래_아파트_매매 건수 세어줘
```

```
korean-law 로 주택임대차보호법 시행령 제10조 조회해줘
```

```
Word MCP 연결됐어? 빈 문서 하나 만들어 봐
```

셋 다 되면 NPL 트랙 필수는 끝입니다.
