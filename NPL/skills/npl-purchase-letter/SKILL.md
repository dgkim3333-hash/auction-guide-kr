---
name: "npl-purchase-letter"
description: "NPL수익률 엑셀 데이터로 매수의향서(.docx)를 정본 규격으로 생성·검증. 10만원 절상, 계약금 10%, 한글 금액, A4 1페이지 피팅, 엑셀-의향서 일치 검증. 무인 실행 시 승인 팝업 도구 금지. 트리거: 매수의향서 작성/생성/검증, 의향서 작성, LOI 작성, 채권매수 의향서, 수익률 파일로 의향서, 의향서가 2장."
---

> **수강생판 안내 (2026-10-02)** — 강사가 실제로 쓰는 스킬을 경로·회사 식별정보만 바꿔 옮긴 것입니다.
> - 작업 루트 `C:\AI\NPL\` · 실거래 창고 `C:\AI\경매창고.duckdb`(03단원) · 회사명·법인번호·연락처는 `[내 회사명]`·`[법인등록번호]`·`[연락처]` 로 비워 두었습니다.
> - `ggi-*`(지지옥션) · `suhyup-*`·`shinhyup-*` · `lender-auction-radar` · `coefficient-*` · `bid-win-curve` · `pipeline-health-check` 와 예약작업은 **유료 사이트 로그인·강사 사내 DB·수집 스크립트가 전제**입니다. 저장소에 함께 올렸지만 그 환경이 없으면 그대로는 돌지 않습니다.
> - `00_시장데이터\` 아래 낙찰 DB·계수이력·수집 스크립트(`calc_coeff.py`·`load_ggi_csv.py` 등)는 강사 사내 자산이라 저장소에 없습니다. 없으면 본문의 **고정 계수표 [추정]** 를 씁니다.

# NPL 매수의향서 자동 생성 및 검증 스킬

NPL수익률 엑셀에서 데이터를 뽑아 **정본 규격 매수의향서(.docx)** 를 만들고 검증한다.
**반드시 A4 1장에 들어가야 하며, 페이지 수는 추측하지 말고 PDF로 변환해 실측한다.**

> **정본 기준:** 2026-06-15자 실제 발송본
> (`매수의향서_2026타경50407 수원지방법원 평택지원_20260615.docx`)
>
> ⚠️ `assets/purchase_letter_template.docx` 와 사용자 폴더의
> `_템플릿\매수의향서_템플릿.docx` 는 **구버전 문구**다. **복제해서 쓰지 않는다.**
> 아래 STEP 4 코드로 **처음부터 새로 생성**한다.

> ⚠️ **이 스킬은 무인 예약 실행에서 호출된다.**
> `suhyup-npl-daily-scan`(매일 16시)과 `ggi-interest-npl-scan`(매주 월 17시)이 불러 쓴다.
> 「파일 잠금 대응」 절의 무인 실행 규칙을 반드시 지킨다.

---

## 핵심 규칙 3가지 (2026-08-13 확정)

1. **금액은 10만원 단위 절상(올림).** 종전 절사 규칙 폐기.
2. **계약금은 매수금액의 정확히 10%.** 절상·절사하지 않는다.
   근거: 실제 발송본 `473,700,000` → `47,370,000`.
3. **템플릿 복제 금지.** 정본 문구·서식으로 새로 생성한다.

### 스크립트 우회 (중요)

`scripts/amount_to_korean.py` 는 절사 기준으로 작성돼 있다.

| 함수·필드 | 사용 |
|---|---|
| `number_to_korean()` | 사용 가능 |
| `truncate_to_man()` | **쓰지 않는다** (절사) |
| `deposit_10pct` / `deposit_formatted` | **쓰지 않는다** (계약금을 다시 절사) |

절상한 금액을 넘기면 내부 절사는 무해하게 통과한다. 계약금은 직접 계산한다.

---

## STEP 0 — 금액 상한 검산 (생성 전 필수)

의향서 금액은 **외부 서류에서 읽은 숫자가 흘러 들어온 결과**다.
판독 오류 한 건이 그대로 법적 문서의 금액이 된다. 생성 전에 확인한다.

| 검산 | 조건 | 위반 시 |
|---|---|---|
| 채권 상한 | `E20 ≤ 채권합계` | **생성 중단** |
| 감정가 상한 | `E20 ≤ C13(감정가)` | **생성 중단** |
| 예상낙찰가 상한 | `E20 ≤ C15(= C13 × C14)` | **생성 중단** |

하나라도 걸리면 만들지 않고 사유를 보고한다.
**채권매입금액이 채권합계를 넘는 일은 정상 업무에서 발생하지 않는다.** 넘었다면 계산이 틀렸다.

## STEP 1 — 엑셀 데이터 추출

'분석' 시트를 `header=None`으로 읽고 셀 위치로 가져온다.

| 필드 | 행(0-based) | 열 | 엑셀 셀 |
|---|---|---|---|
| 주소 | 3 | 2 | C4 |
| 채권은행 | 7 | 2 | C8 |
| 담당자/지점 | 8 | 2 | C9 |
| 채권매입금액 | 19 | 4 | **E20** |
| 채권매입비율 | 16 | 4 | E17 |

```python
import pandas as pd
df = pd.read_excel(path, sheet_name='분석', header=None)
address = str(df.iloc[3, 2]); bank = str(df.iloc[7, 2])
branch  = str(df.iloc[8, 2]); E20  = float(df.iloc[19, 4])
```

> openpyxl로 갓 만든 파일은 수식 계산값이 없다. 그때는 Excel MCP로 한 번 열어 E20을 회수한다.
> Excel MCP 인자는 `session_id` · `sheet_name` · `range_address` 이고
> `file` 액션의 경로 인자는 `path` 다. 회수 후 `save:false` 로 닫는다.

## STEP 2 — 금액 처리

```python
매수금액 = -(-int(E20) // 100000) * 100000   # 10만원 절상
계약금   = int(매수금액 * 0.1)                # 정확히 10%
assert '.' not in f"{매수금액:,}"
```

한글 변환은 절상된 금액으로 한다. 예: `106,700,000` → `일억육백칠십만원`

| 원값 | 절상 | 한글 |
|---|---|---|
| 1,443,387,677.23 | 1,443,400,000 | 십사억사천삼백사십만원 |
| 722,074,235.74 | 722,100,000 | 칠억이천이백십만원 |
| 106,661,141.31 | 106,700,000 | 일억육백칠십만원 |
| 473,700,000 | 473,700,000 | 사억칠천삼백칠십만원 |

## STEP 3 — 수신처 구성

`{채권은행} {지점명} 귀중` 형식.

- 지점 없이 본점·조합 앞으로 보내는 경우가 실제로 있다 → 은행명만 쓴다
- 채권관리팀·TF팀 등 부서가 담당 창구면 그 부서명을 지점 자리에 쓴다
- 채권은행에 이미 지점명이 있으면 중복 추가하지 않는다

---

## STEP 4 — 정본 규격으로 생성 (검증된 코드)

아래 코드는 **A4 1페이지가 실측 확인된 구현**이다. 그대로 쓴다.

```python
import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "맑은 고딕"
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)   # A4
for m in ("top_margin","bottom_margin","left_margin","right_margin"):
    setattr(sec, m, Inches(1))

st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
# ★ 1페이지 피팅의 핵심 — 기본 스타일의 줄간격 1.08 / 문단뒤 8pt 를 제거한다
pf = st.paragraph_format
pf.line_spacing = 1.0; pf.space_before = Pt(0); pf.space_after = Pt(0)

def P(text="", align="left", bold=False, size=12, after=0):
    p = doc.add_paragraph()
    p.alignment = {"left":WD_ALIGN_PARAGRAPH.LEFT,"center":WD_ALIGN_PARAGRAPH.CENTER}[align]
    f = p.paragraph_format
    f.space_before = Pt(0); f.space_after = Pt(after/20); f.line_spacing = 1.0
    if text:
        r = p.add_run(text); r.bold = bold; r.font.size = Pt(size); r.font.name = FONT
        r.font.color.rgb = RGBColor(0,0,0)
        r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    return p

def cellP(cell, text, align="left", first=False):
    p = cell.paragraphs[0] if first else cell.add_paragraph()
    p.alignment = {"left":WD_ALIGN_PARAGRAPH.LEFT,"center":WD_ALIGN_PARAGRAPH.CENTER}[align]
    f = p.paragraph_format
    f.space_before = Pt(0); f.space_after = Pt(0); f.line_spacing = 1.0
    r = p.add_run(text); r.font.size = Pt(12); r.font.name = FONT
    r.font.color.rgb = RGBColor(0,0,0)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if text.startswith(" "): r._element.set(qn('xml:space'), 'preserve')

# ── 본문 상단 (빈 줄 없이 제목부터 — 1페이지 피팅) ──
P("매 수 의 향 서", "center", bold=True, size=16, after=400)
P("1. 귀사의 무궁한 발전을 기원합니다.", after=100)
P("2. 본인은 아래와 같은 금액으로 귀사가 보유하고 계신 부실채권에 대하여", after=100)
P("  확정채권 양수도 계약방식으로 매수하고자 의향서를 제출합니다.", after=200)
P("-아 래 -", "center", after=200)

# ── 표 3행 × 2열 ──
t = doc.add_table(rows=3, cols=2); t.style = 'Table Grid'
tblPr = t._tbl.tblPr
lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'),'fixed'); tblPr.append(lay)
mar = OxmlElement('w:tblCellMar')
for tag, v in (('top',80),('left',120),('bottom',80),('right',120)):
    e = OxmlElement(f'w:{tag}'); e.set(qn('w:w'),str(v)); e.set(qn('w:type'),'dxa'); mar.append(e)
tblPr.append(mar)
for row in t.rows:
    for i, c in enumerate(row.cells):
        c.width = Inches([2400,6626][i]/1440)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

cellP(t.cell(0,0), "(1)대상", "center", first=True)
cellP(t.cell(0,1), "* 물건소재지", first=True)
cellP(t.cell(0,1), f"  - {주소}")
cellP(t.cell(1,0), "(2)채권매수금액", "center", first=True)
cellP(t.cell(1,1), f"금 : {한글금액} (₩{매수금액:,})", first=True)
cellP(t.cell(2,0), "(3)매수조건", "center", first=True)
cellP(t.cell(2,1), f"* 계약시 계약금 10% 지급 (₩{계약금:,})", first=True)
cellP(t.cell(2,1), "* 확인되지 않은 당해세,소액임차인,임금채권등 발생시")
cellP(t.cell(2,1), "  매수가격에서 조정")
cellP(t.cell(2,1), "* 근저당권 이전비용 부담")

# ── 본문 하단 ──
P(after=200)
P("위와 같이 매수하고자 의향서를 제출합니다.", after=200)
P(after=100)
P("붙임 : 대부업등록증,사업자등록증,법인인감증명서,법인등기부등본 각1통", bold=True, after=300)
P(f"{today.year}년 {today.month}월 {today.day}일", "center", after=300)
P("매수희망자 : 주식회사 [내 회사명]", after=60)
P("대부업등록번호 : [대부업등록번호]", after=60)
P("법인등록번호 : [법인등록번호]", after=60)
P("주소 : [회사 주소]", after=60)
P("연락처 : [연락처] ([담당자])", after=300)
P(f"{수신처} 귀중", "center", bold=True, size=16, after=100)
doc.save(OUT)
```

### 문구 주의 (구버전과 다름 — 혼입 차단)

- "보유하고 **계신 부실채권에 대하여**" — ~~"보유하고 있는 근저당부채권을"~~ 아님
- "매수하고자 **의향서를** 제출합니다" — ~~"매수의향서를 제출합니다"~~ 아님
- "붙임 : … 법인인감증명서**,법인등기부등본 각1통**" — ~~"각 1부, 끝."~~ 아님
- **대부업등록번호 줄을 빠뜨리지 않는다** (구버전에는 없다)
- 원화기호는 `₩`(U+20A9). `\`(백슬래시) 금지

### 고정 정보 ([내 회사명])

| 항목 | 값 |
|---|---|
| 매수희망자 | 주식회사 [내 회사명] |
| 대부업등록번호 | [대부업등록번호] |
| 법인등록번호 | [법인등록번호] |
| 주소 | [회사 주소] |
| 연락처 | [연락처] ([담당자]) |

> 구주소 `(예전 주소)` 를 재사용하지 않는다.

---

## STEP 5 — A4 1페이지 실측 (필수, 생략 금지)

**"1페이지일 것이다"라고 추측하지 않는다.** 반드시 변환해서 센다.

```
mcp__word__convert_to_pdf(filename=<docx경로>, output_filename=<임시.pdf>)
pdfinfo <임시.pdf> | grep "^Pages"
```

**2페이지 이상이면 아래 순서로 줄이고 다시 측정한다.** 이 순서를 지키면 시각 손상이 가장 적다.

| 순서 | 조치 | 절감 |
|---|---|---|
| 1 | Normal 스타일 `line_spacing=1.0`, `space_after=0` 확인 (누락 시 최대 원인) | 큼 |
| 2 | 제목 위 빈 줄 제거 (위 코드는 이미 제거됨) | 약 22pt |
| 3 | 제목 아래 빈 줄 제거 | 약 22pt |
| 4 | 표 앞뒤 빈 줄(`P(after=200)`)의 after를 100으로 축소 | 약 5pt |
| 5 | 매수희망자 정보 5줄의 after를 60 → 40 | 약 3pt |

**폰트 크기·여백·표 너비는 건드리지 않는다.** 발송 문서의 인상이 달라진다.

측정이 끝나면 임시 PDF는 지운다. **삭제가 막히면 그냥 둔다.** 승인 도구를 부르지 않는다.

> 실측 사례: 주소가 긴 물건(인천 미추홀구 주안동 229-7, 229-12 성우아파트 제2층 제201호)은
> 표가 3줄로 늘어 2페이지가 됐다. 2페이지에는 "귀중" 한 줄만 있었고,
> Normal 스타일 초기화 + 상단 빈 줄 2개 제거로 1페이지에 들어갔다.

---

## STEP 6 — 검증

| # | 항목 | 방법 |
|---|---|---|
| 1 | 물건소재지 | 엑셀 주소 ↔ 의향서 |
| 2 | 채권매수금액 | E20 **절상**값 ↔ 의향서 숫자 |
| 3 | 한글금액 | 숫자→한글 역변환 교차검증 |
| 4 | 계약금 | 매수금액 × 0.1 (**절사 없음**) |
| 5 | 수신처 | 채권은행+지점 ↔ 의향서 |
| 6 | 날짜 형식 | YYYY년 M월 D일 |
| 7 | 소수점 없음 | 전체 텍스트에 `숫자.숫자` 금액 패턴 없음 |
| 8 | 정본 문구 | "계신 부실채권에 대하여" / "의향서를 제출" / "법인등기부등본 각1통" 존재 |
| 9 | 회사정보 | 대부업등록번호 존재 · 주소 [회사 주소] |
| 10 | **A4 1페이지** | PDF 변환 실측 (STEP 5) |
| 11 | 금지어 잔존 | `근저당부채권` `각 1부, 끝` `김포` `473,700,000` `47,370,000` 없음 |

```python
must = ["보유하고 계신 부실채권에 대하여","매수하고자 의향서를 제출합니다",
        "법인등기부등본 각1통","[대부업등록번호]","[회사 주소]",
        f"₩{매수금액:,}", f"₩{계약금:,}", 한글금액, 주소, 수신처]
bad  = ["근저당부채권","매수의향서를 제출","각 1부, 끝","김포","473,700,000","47,370,000"]
assert not [m for m in must if m not in body], "필수 항목 누락"
assert not [b for b in bad  if b in body],     "금지어 잔존"
assert 계약금 == int(매수금액 * 0.1)
```

불일치가 있으면 ❌와 함께 엑셀 값·의향서 값을 나란히 보여준다.

---

## 파일 잠금 대응

`mcp__word__word_live_list_open` 으로 먼저 확인한다.
열려 있으면 재생성하지 말고 `word_live_replace_text` + `word_live_save` 로 값만 고친다.
샌드박스 bash는 세션 이전 파일을 덮어쓰지 못하므로 `rm` 후 `cp` 한다.

### ★★ 무인 실행에서 승인 도구 호출 금지 (2026-09-08 신설)

**이 스킬은 매일·매주 사람 없이 도는 예약작업에서 호출된다.**

- `rm` 이 `Permission denied` / `Operation not permitted` 로 막혀도
  **`mcp__cowork__allow_cowork_file_delete` 를 부르지 않는다.**
- `mcp__cowork__request_cowork_directory` · `AskUserQuestion` 도 마찬가지다.
- 파일이 열려 있어도 **사용자에게 닫아달라고 요청하고 기다리지 않는다.**

이 도구들은 승인 팝업을 띄우는데, 무인 회차에는 응답할 사람이 없어
`AbortError: Tool permission stream closed before response received` 로 **회차가 통째로 끊긴다.**

2026-09-08 실사고: `suhyup-npl-daily-scan` 회차가 이 경로로 멈추다.
그 시점에 `_처리이력.json` 이 저장 전이어서, 다음 회차에 같은 공고를 신규로
재처리할 뻔했다(산출물 중복 생성 + 마스터 중복 등재).

**막히면 대체 파일명으로 저장하고 넘어간다.**

```
매수의향서_{No}_v2.docx   ← 원본이 잠겨 있을 때
```

호출한 상위 스킬에 `pending_locked` 와 사유를 돌려주고, 상위가 이력에 기록해
다음 회차에 재시도하게 한다. **이 단계의 실패는 회차 실패가 아니다.**

## 산출물 저장 규칙

| 경로 | 파일명 |
|---|---|
| 단건 수동 작성 | `매수의향서_{사건번호} {법원명}_{YYYYMMDD}.docx` |
| `suhyup-npl-daily-scan` 일일 스캔 | `매수의향서_{수협NPL 전체현황 B열 No}.docx` |

- 사용자가 선택한 폴더에 저장한다. 임시 폴더에 두고 끝내지 않는다
- 덮어쓰기 전 `_백업\` 에 보관한다

**생성한 의향서는 파일로만 남긴다. 발송·제출·전송은 이 스킬의 범위가 아니며 하지 않는다.**

## 자동 생성 조건 (일일 스캔 연동)

`suhyup-npl-daily-scan` 호출 시 **자기자본수익률 G14 ≥ 0.4(40%)** 인 물건만 생성한다.
미만이면 만들지 않고 실제 G14 수치를 이력에 기록한다.

---

## 변경 이력

- **2026-09-08**: 「파일 잠금 대응」의 `allow_cowork_file_delete` 호출 지시를 **무인 실행 금지**로
  반전하고 대체 절차(`_v2` 파일명 + `pending_locked` 반환)를 명시했다. 이 스킬은
  `suhyup-npl-daily-scan`·`ggi-interest-npl-scan` 이 불러 쓰는 하위 스킬이라, 상위 스킬만
  고치면 여기로 방어가 뚫렸다. / STEP 0 금액 상한 검산을 스킬 자체에 내장했다(종전에는
  상위 스킬에만 있었다). / STEP 5 임시 PDF 삭제 실패 시 처리 명시. / 발송 금지 조항 명시.

