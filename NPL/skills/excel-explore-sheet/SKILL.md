---
name: "excel-explore-sheet"
description: "슬라이서로 조건을 겹쳐 좁히면 결과가 화면 위쪽에 즉시 펼쳐지는 '탐색 시트' 엑셀 제작(원본 표 아래, SUBTOTAL 보조열 + A15 FILTER 스필). 금액 열이 있으면 「금액 규모대」 파생열·슬라이서 필수. ★3단계 XML 패치(슬라이서 144×170pt absoluteAnchor)는 필수 — 건너뛰면 다중선택 버튼이 사라진다. 빌드 후 verify_explore.py 게이트 통과 전 납품 금지. 무인 실행 시 잠기면 _v2 저장. 트리거: 탐색 시트, 슬라이서 엑셀, 드릴다운 엑셀, 다중선택, 조건 좁히면 목록이 줄어드는, FILTER 스필, 금액 규모대, 감정가 규모대, 가격대별로."
---

> **수강생판 안내 (2026-10-02)** — 강사가 실제로 쓰는 스킬을 경로·회사 식별정보만 바꿔 옮긴 것입니다.
> - 작업 루트 `C:\AI\NPL\` · 실거래 창고 `C:\AI\경매창고.duckdb`(03단원) · 회사명·법인번호·연락처는 `[내 회사명]`·`[법인등록번호]`·`[연락처]` 로 비워 두었습니다.
> - `ggi-*`(지지옥션) · `suhyup-*`·`shinhyup-*` · `lender-auction-radar` · `coefficient-*` · `bid-win-curve` · `pipeline-health-check` 와 예약작업은 **유료 사이트 로그인·강사 사내 DB·수집 스크립트가 전제**입니다. 저장소에 함께 올렸지만 그 환경이 없으면 그대로는 돌지 않습니다.
> - `00_시장데이터\` 아래 낙찰 DB·계수이력·수집 스크립트(`calc_coeff.py`·`load_ggi_csv.py` 등)는 강사 사내 자산이라 저장소에 없습니다. 없으면 본문의 **고정 계수표 [추정]** 를 씁니다.

# 탐색 시트 엑셀 (다중선택 드릴다운)

슬라이서를 겹쳐 누르면 **결과가 화면 위쪽 15행부터 즉시 펼쳐지고** 상단 요약 숫자가 함께 움직이는
엑셀을 만든다. 데이터 종류와 무관하게 목록형 산출물이면 이 양식을 쓴다.

## 발상

일반적인 표+슬라이서는 필터링해도 행이 원래 자리에서 숨겨질 뿐이라, 결과를 보려면 스크롤해야 하고
건수가 많으면 어디까지가 결과인지 알기 어렵다.

이 양식은 뒤집는다.

```
원본 표      →  결과 영역 아래로 내린다 (슬라이서의 필터 대상, 사용자는 볼 일 없음)
보조열 Z     →  =SUBTOTAL(103,H501)  행이 살아있으면 1, 숨겨졌으면 0
결과 표      →  A15의 FILTER 수식이 Z=1인 행만 15행부터 스필
요약 숫자    →  SUBTOTAL(103/109/101/104)  숨겨진 행을 빼고 계산 → 슬라이서에 즉시 반응
```

**SUM·COUNTIF를 쓰면 절대 안 바뀐다. 반드시 SUBTOTAL이어야 한다.**

## 지켜야 할 4가지

1. 슬라이서를 누르면 **14행 헤더 바로 아래(15행부터) 선택 결과 전체**가 보인다. 스크롤 불필요, 건수 제한 없음.
2. 같은 데이터가 화면에 **두 번 보이지 않는다**.
3. 상단 패널·슬라이서·결과 표가 **겹치지 않는다**.
4. **금액 열이 있으면 「금액 규모대」 슬라이서가 반드시 있다.** (아래 전용 절 참조)

## ★ 무인 실행 원칙 (2026-09-08 신설)

이 스킬은 무인 예약작업(`onbid-weekly-mon11` · `ggi-newlist-wed` · `ggi-running-wed1130` ·
`lender-auction-radar-weekly`)에서 호출된다. 그 회차에는 사람이 없다.

- **승인 팝업을 띄우는 도구를 호출하지 않는다.**
  `mcp__cowork__allow_cowork_file_delete` · `mcp__cowork__request_cowork_directory` · `AskUserQuestion`.
  무인 회차에 부르면 `AbortError: Tool permission stream closed` 로 회차가 통째로 끊긴다
  (2026-09-08 `suhyup-npl-daily-scan` 실사고).
- **사용자에게 파일을 닫아달라고 요청하고 기다리지 않는다.** 아래 「파일이 잠겼을 때」를 따른다.
- 대화형으로 사람이 함께 있을 때는 요청해도 된다. **무인 회차에서만 금지**다.

## 전제 확인

`FILTER`·`LET`은 Excel 365 전용이다. 처음 쓰는 환경이면 작은 시트에 아래를 넣어 확인한다.

```
=LET(a,FILTER($A$1:$B$4,$C$1:$C$4=1,""),IF(a="","",a))
```

값이 스필되면 진행, `#NAME?`이면 이 양식을 쓸 수 없으니 사용자에게 알린다.

---

## ★ 금액 규모대 슬라이서 — 필수 (2026-09-04 확정)

**금액 열이 하나라도 있으면 「○○ 규모대」 파생열을 만들고 그 열로 슬라이서를 건다. 예외 없다.**

### 왜 필수인가

슬라이서는 **값이 같은 것끼리 묶어** 항목을 만든다. 금액은 전부 다른 값이라
금액 열에 직접 슬라이서를 걸면 항목이 행 수만큼 생겨 못 쓴다.
그래서 금액은 **구간으로 접어야만** 슬라이서가 성립한다.

「전체 3,000,000,000원 이상만 보겠다」, 「500,000,000원 이하 소액만 보겠다」는
목록형 산출물에서 가장 자주 쓰는 조건인데, 규모대 열이 없으면 그 조건을 아예 걸 수 없다.
지역·용도만 있고 금액 구간이 없는 탐색 시트는 **미완성으로 취급한다.**

### 표준 구간 (기본값 — 부동산 금액에 맞춘 8구간)

```
① 100,000,000원 미만
② 100,000,000~300,000,000원
③ 300,000,000~500,000,000원
④ 500,000,000~1,000,000,000원
⑤ 1,000,000,000~3,000,000,000원
⑥ 3,000,000,000~5,000,000,000원
⑦ 5,000,000,000원 이상
⑧ 미상
```

- 라벨 맨 앞의 `①②③…` 원문자는 **정렬용**이다. 빼면 슬라이서가 가나다순으로 뒤섞인다.
- **구간 라벨의 금액도 원 단위 풀 콤마다.** `1억`·`3억`·`5,000만` 같은 축약은 금지.
  (사용자 표기 규칙은 구간 라벨에도 예외 없이 적용된다.)
- 값이 없거나 0이면 `⑧ 미상`. 빈칸으로 두지 마라 — 슬라이서에서 그 행을 고를 수 없게 된다.

### 구간을 갈아야 할 때

데이터 분포가 표준 구간에 안 맞으면(예: 한 구간에 80% 이상이 몰림) 구간을 다시 잡는다.
그때도 **7~8구간을 넘기지 않는다.** 구간이 많으면 슬라이서가 스크롤돼 한눈에 안 들어온다.

- 금액 단위가 다른 데이터(월 임대료·수수료 등)는 자릿수를 낮춰 같은 8구간 골격을 쓴다.
- 금액 열이 2개 이상이면 **대표 금액 하나만** 규모대로 만든다(감정가/원금 등 기준액).
  둘 다 만들면 슬라이서 줄이 길어지고 사용자가 어느 쪽인지 헷갈린다.

### 비율 열이 있으면 「비율 구간」도 같이

`최저가율(%)`·`수익률(%)`·`시세비(%)` 같은 연속 비율 열도 같은 이유로 직접 슬라이서를 걸 수 없다.
금액 규모대와 **한 쌍으로** 구간 열을 만든다.

```
① 40% 이하  ② 40~50%  ③ 50~70%  ④ 70~85%  ⑤ 85~95%  ⑥ 95% 초과  ⑦ 미상
```

### 코드

```python
def band_amount(v):
    if not v: return '⑧ 미상'
    if v <   100_000_000: return '① 100,000,000원 미만'
    if v <   300_000_000: return '② 100,000,000~300,000,000원'
    if v <   500_000_000: return '③ 300,000,000~500,000,000원'
    if v < 1_000_000_000: return '④ 500,000,000~1,000,000,000원'
    if v < 3_000_000_000: return '⑤ 1,000,000,000~3,000,000,000원'
    if v < 5_000_000_000: return '⑥ 3,000,000,000~5,000,000,000원'
    return '⑦ 5,000,000,000원 이상'

def band_ratio(v):
    if v is None: return '⑦ 미상'
    for th, lab in [(40,'① 40% 이하'), (50,'② 40~50%'), (70,'③ 50~70%'),
                    (85,'④ 70~85%'), (95,'⑤ 85~95%')]:
        if v <= th: return lab
    return '⑥ 95% 초과'
```

파생 열은 **원본 표 오른쪽 끝**에 붙인다(결과 표에도 같은 자리에 나온다).
열 폭은 `⑤ 1,000,000,000~3,000,000,000원`이 안 잘리게 **26 이상**으로 잡는다.

### 납품 전 확인

`slicer(list-table-slicers)`로 규모대 슬라이서가 존재하고 `availableItems`가 2개 이상인지 읽는다.
슬라이서가 없거나 항목이 1개뿐이면 구간이 잘못 잡힌 것이니 다시 잡는다.

---

## 레이아웃

| 위치 | 내용 |
|---|---|
| B1 | 제목 14pt 굵게 |
| B2 | 사용법 1줄 (예시 조건 + 해제 방법) |
| B4:B9 | 요약 라벨 — 남색 `1F4E79` 배경·흰 글씨 |
| C4:C9 | 요약 값 — 연분홍 `FCE4E4` 배경·빨강 `C00000` 굵게 |
| 슬라이서 | `top=48`, `width=144`, `height=170` 한 줄 |
| B13 | `▼ 여기가 선택 결과입니다 (선택 조건에 맞는 전체 건수가 표시됩니다)` 빨강 굵게 |
| A14 | 결과 표 헤더 — 원본과 같은 열 이름·서식·열 폭 |
| A15 | 스필 수식 **1개** |
| A15:{끝열}{RAWHDR-5} | 결과 행 서식 미리 깔기 |
| B{RAWHDR-1} | `▼ 아래는 원본 표(슬라이서 필터 대상) — 보지 않으셔도 됩니다. 지우거나 숨기지 마십시오.` 회색 굵게 |
| A{RAWHDR} | 원본 표 헤더, 다음 행부터 데이터. 표 이름 `TBL_xxx` |
| Z{RAWHDR} | `표시여부(보조)` |
| Z{RAWHDR+1}~ | `=SUBTOTAL(103,H501)` 행마다 상대참조 |

`H`는 **빈 값이 없는 열**(키 열)을 쓴다. 빈 셀이 있는 열을 쓰면 그 행이 0으로 판정돼 결과에서 빠진다.

### ★ 원본 표 위치(RAWHDR) — 500 고정이 아니다

결과 영역을 넘는 데이터에 500을 쓰면 전체 해제 시 `#SPILL!`이 난다.

```
N ≤ 420  →  RAWHDR = 500
N > 420  →  RAWHDR = ((N + 80) // 100 + 1) * 100
```

실증: 72건→500 / 248건→500 / 841건→1000 / 2,270건→2400 / 2,205건→2300.

### 수식

```
C4 =SUBTOTAL(103,TBL_xxx[키열])
C5 =SUBTOTAL(109,TBL_xxx[금액열])
C6 =IFERROR(ROUND(SUBTOTAL(101,TBL_xxx[금액열]),0),0)
C7 =IFERROR(SUBTOTAL(104,TBL_xxx[금액열]),0)
C8 =SUBTOTAL(109,TBL_xxx[금액열2])
C9 =IFERROR(ROUND(SUBTOTAL(103,TBL_xxx[키열])/COUNTA(TBL_xxx[키열])*100,1),0)

A15 =LET(a,FILTER($A$501:$X$681,$Z$501:$Z$681=1,""),IF(a="","",a))
```

501·681·X는 실제 데이터 첫 행·끝 행·마지막 열로 맞춘다.
**TAKE 등 건수 제한을 걸지 않는다.**

### ★ 요약 KPI 열 폭 — B·C는 결과 표의 2·3번째 열이기도 하다

결과 표 기준으로만 좁게 잡으면 요약 금액이 `####`로 깨진다(실측 2회 발생).

- **B ≥ 18** (라벨용)
- **C ≥ 26** 을 기본값으로 시작한다. 전 지역 합계는 쉽게 조 단위(13자리 이상)가 되고,
  값 글꼴이 13pt 굵게라 열 폭 단위가 표시하는 것보다 실제로 더 넓게 필요하다.

### 틀고정 · 행 높이

- 틀고정은 `1:14`까지. **열 고정(xSplit)은 넣지 않는다** — 넣으면 화면이 좁아져 목록이 거의 안 보인다.
- **행 높이를 키우지 않으면 슬라이서가 13·14행을 덮는다.**
  슬라이서 아래 끝 = `48+170 = 218pt`. 기본 행 높이로는 1~12행 합이 약 180pt뿐이다.
  실측 통과값: **1행 22 / 4~9행 각 24 / 10~12행 각 20 ≈ 221pt**

---

## 빌드 순서 — 틀리면 수식이 깨진다

**1 → 2 → 3 → 4 전부 필수다. 3·4단계를 「선택」으로 취급하지 마라.**

### 1단계 openpyxl — 정적인 것 전부

데이터·헤더·라벨·안내문·행 높이·열 폭·결과영역 서식·보조열 수식·틀고정.

**구조적 참조(`TBL_xxx[...]`)를 openpyxl로 쓰지 않는다.** 표가 아직 없어 로드 시 오류값이 된다.
(실측: `-2146826265`로 굳음)

```python
# -*- coding: utf-8 -*-
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT   = r"<최종 저장 경로>.xlsx"
FONT  = "Noto Sans CJK SC"
TOPHDR = 14

# HEAD: (열이름, 폭) / KEY: recs 딕셔너리 키 — 순서가 일치해야 한다
# ★금액 열이 있으면 '금액 규모대'를 반드시 마지막에 붙인다 (폭 26 이상)
HEAD = [('연번',6), ('구분',13), ('명칭',20), ('금액(원)',17), ('일자',12), ('금액 규모대',26)]
KEY  = ['연번','구분','명칭','금액','일자','금액 규모대']
recs = [...]                      # 딕셔너리 리스트 (미리 정렬해 둔다)

N        = len(recs)
NC       = len(HEAD)
RAWHDR   = 500 if N <= 420 else ((N + 80) // 100 + 1) * 100
RAWDATA  = RAWHDR + 1
RESEND   = RAWHDR - 5
LASTCOL  = get_column_letter(NC)
LASTROW  = RAWDATA + N - 1
C        = {h: i+1 for i, (h, _) in enumerate(HEAD)}
MONEY    = [C['금액(원)']]
DATES    = [C['일자']]

wb = Workbook(); ws = wb.active; ws.title = '탐색'
hf    = Font(name=FONT, bold=True, color='FFFFFF', size=10)
hfill = PatternFill('solid', fgColor='1F4E79')
base  = Font(name=FONT, size=10)

ws['B1'] = '<제목>'
ws['B1'].font = Font(name=FONT, bold=True, size=14, color='1F4E79')
ws['B2'] = '▼ 위 슬라이서를 눌러 조건을 좁히십시오. 선택 결과는 아래 15행부터 전부 표시됩니다. (해제: 슬라이서 우측 상단 지우개 아이콘)'
ws['B2'].font = Font(name=FONT, size=9, color='595959')

LIVE = [('선택 건수','#,##0'), ('금액 합계(원)','#,##0'), ('금액 평균(원)','#,##0'),
        ('금액 최대(원)','#,##0'), ('금액2 합계(원)','#,##0'), ('전체 대비 비율(%)','0.0"%"')]
for i, (lab, fmt) in enumerate(LIVE):          # 값(C4:C9)은 2단계에서 채운다
    r = 4 + i
    c = ws.cell(r, 2, lab)
    c.font = Font(name=FONT, bold=True, size=10, color='FFFFFF'); c.fill = hfill
    c.alignment = Alignment(horizontal='left', vertical='center')
    v = ws.cell(r, 3)
    v.font = Font(name=FONT, bold=True, size=13, color='C00000')
    v.fill = PatternFill('solid', fgColor='FCE4E4')
    v.number_format = fmt
    v.alignment = Alignment(horizontal='right', vertical='center')

ws['B13'] = '▼ 여기가 선택 결과입니다 (선택 조건에 맞는 전체 건수가 표시됩니다)'
ws['B13'].font = Font(name=FONT, bold=True, size=10, color='C00000')

for j, (h, w) in enumerate(HEAD, start=1):     # 결과 헤더 14행
    c = ws.cell(TOPHDR, j, h); c.font = hf; c.fill = hfill
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.column_dimensions[get_column_letter(j)].width = w
# ★요약 KPI가 잘리지 않게 B·C를 다시 넓힌다
ws.column_dimensions['B'].width = max(ws.column_dimensions['B'].width or 0, 18)
ws.column_dimensions['C'].width = max(ws.column_dimensions['C'].width or 0, 26)

for r in range(15, RESEND + 1):                 # 결과 영역 서식 미리 깔기
    for j in range(1, NC+1):
        cell = ws.cell(r, j); cell.font = base
        if   j in MONEY: cell.number_format = '#,##0'
        elif j in DATES: cell.number_format = 'yyyy-mm-dd'
        elif j == C['연번']: cell.number_format = '0'

ws.cell(RAWHDR-1, 2, '▼ 아래는 원본 표(슬라이서 필터 대상) — 보지 않으셔도 됩니다. 지우거나 숨기지 마십시오.')
ws.cell(RAWHDR-1, 2).font = Font(name=FONT, bold=True, size=10, color='808080')

for j, (h, _) in enumerate(HEAD, start=1):     # 원본 헤더
    c = ws.cell(RAWHDR, j, h); c.font = hf; c.fill = hfill
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

for n, rec in enumerate(recs):                  # 원본 데이터
    rr = RAWDATA + n; rec['연번'] = n + 1
    for j, k in enumerate(KEY, start=1):
        cell = ws.cell(rr, j, rec[k]); cell.font = base
        if   j in MONEY: cell.number_format = '#,##0'
        elif j in DATES: cell.number_format = 'yyyy-mm-dd'
        elif j == C['연번']: cell.number_format = '0'

ws.cell(RAWHDR, 26, '표시여부(보조)').font = Font(name=FONT, bold=True, size=9, color='808080')
for n in range(N):                              # 보조열 Z — 키 열을 참조
    rr = RAWDATA + n
    ws.cell(rr, 26, '=SUBTOTAL(103,H%d)' % rr).font = Font(name=FONT, size=9)
ws.column_dimensions['Z'].width = 13

ws.row_dimensions[1].height = 22                # 슬라이서가 13·14행을 덮지 않게
for r in range(4, 10):  ws.row_dimensions[r].height = 24
for r in range(10, 13): ws.row_dimensions[r].height = 20

ws.freeze_panes = 'A15'
ws.sheet_view.showGridLines = False
wb.create_sheet('피벗집계'); wb.create_sheet('대시보드')
wb.save(OUT)
print('rows', N, '| 원본 %d~%d' % (RAWDATA, LASTROW), '| 마지막열', LASTCOL)
print('A15 =LET(a,FILTER($A$%d:$%s$%d,$Z$%d:$Z$%d=1,""),IF(a="","",a))'
      % (RAWDATA, LASTCOL, LASTROW, RAWDATA, LASTROW))
```

### 2단계 Excel MCP — 표부터, 그 다음 수식

```
file(open)
table(create, sheet:"탐색", range:"A{RAWHDR}:{끝열}{끝행}", table_name:"TBL_xxx", table_style:"TableStyleMedium2")
range(set-formulas, "탐색!C4:C9", 요약 수식 6개)      ← 표 생성 이후여야 한다
range(set-formulas, "탐색!A15",   스필 수식 1개)
slicer(create-table-slicer) × 필요 개수   ← ★금액 규모대를 반드시 포함
pivottable / chart …
file(close, save:true)
```

**슬라이서 `position`은 범위가 아니라 단일 셀**이어야 한다. 범위를 주면 `COMException 0x800A01A8`.
같은 이름으로 재생성해도 같은 오류 — 이름을 바꾸거나 먼저 삭제한다.
셀 앵커로 대충 놓고, pt 정밀 배치는 3단계에서 **반드시** 잡는다.

**★세션을 열어 둔 채 대화가 끊기면 그 세션의 작업은 통째로 날아간다.**
표·수식·슬라이서를 만들었으면 **바로 `file(close, save:true)`** 한다. 다음 파일은 그다음에 연다.
(실측: 세션 유실로 seoul_full·gg_full의 표와 슬라이서가 전부 사라졌다.)

### ★ 파일이 잠겼을 때 (2026-09-08 개정)

사용자가 파일을 Excel에서 열어 두면 `~$파일명.xlsx` 잠금 파일이 생기고 쓰기가 막힌다.

| 상황 | 처리 |
|---|---|
| **대화형** (사람이 함께 있음) | 닫아달라고 요청한 뒤 같은 이름으로 재시도한다 |
| **무인 예약 회차** | **요청하고 기다리지 않는다.** `_v2` 파일명으로 저장하고 보고에 「원본 잠김 — 다음 회차 재시도」를 적는다 |

종전 문구는 무인 회차에서도 「닫아달라고 요청한 뒤 재시도」였다. 응답할 사람이 없어
회차가 그 자리에서 멈춘다. **`allow_cowork_file_delete` 로 우회하지도 않는다** —
그 도구는 승인 팝업을 띄워 `AbortError: Tool permission stream closed` 로 회차를 끊는다.

삭제·이동이 `Operation not permitted` 로 막혀도 그냥 넘어가고 보고에 적는다.

### 3단계 XML 패치 ★필수★ — 세션을 닫고 한다

**「선택」이 아니다. 건너뛰면 다중선택 버튼이 사라진다.**
2단계가 만든 슬라이서는 `twoCellAnchor`(셀 앵커)라 **크기가 셀 폭에 종속**된다.
폭이 144pt에 못 미치면 Excel 이 슬라이서 머리글 오른쪽 버튼부터 잘라내는데,
**가장 먼저 사라지는 것이 「다중 선택」 버튼**이다. 미관 문제가 아니라 기능 요건이다.
[확정 2026-09-21 실사고] 이 단계를 「선택·미관」으로 판단해 생략한 회차에서
산출물 4종 전부 다중선택 불가 상태로 납품됐다. 직전 회차(absoluteAnchor 144×170pt)와의
유일한 구조적 차이가 이것이었다.

```python
import zipfile, re
EMU = 12700
TOP, W, H = 48, 144, 170
# ★첫 슬라이서 left=620pt, 간격 160pt 를 기본값으로 쓴다.
# 폭을 계산식(width*7+5)으로 잡으면 기본 글꼴 렌더링 폭보다 작게 나와 KPI 값이 가려진다(실측 사고).
POS = {n: 620 + 160*i for i, n in enumerate(['SL_A','SL_B','SL_C','SL_D','SL_E','SL_F','SL_G'])}

zin = zipfile.ZipFile(SRC); zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)

    # 슬라이서 pt 정밀 배치: twoCellAnchor → absoluteAnchor
    if re.match(r'xl/drawings/drawing\d+\.xml$', it.filename):
        x = d.decode('utf-8')
        def repl(m):
            blk = m.group(0)
            nm = re.search(r'name="(SL_[^"]+)"', blk)
            if not nm or nm.group(1) not in POS: return blk
            head = ('<xdr:absoluteAnchor><xdr:pos x="%d" y="%d"/><xdr:ext cx="%d" cy="%d"/>'
                    % (POS[nm.group(1)]*EMU, TOP*EMU, W*EMU, H*EMU))
            inner = re.sub(r'^<xdr:twoCellAnchor[^>]*>', '', blk)
            inner = re.sub(r'<xdr:from>.*?</xdr:from>', '', inner, flags=re.S)
            inner = re.sub(r'<xdr:to>.*?</xdr:to>',     '', inner, flags=re.S)
            inner = re.sub(r'</xdr:twoCellAnchor>$', '', inner)
            return head + inner + '</xdr:absoluteAnchor>'
        d = re.sub(r'<xdr:twoCellAnchor.*?</xdr:twoCellAnchor>', repl, x, flags=re.S).encode('utf-8')

    zout.writestr(it, d)
zout.close(); zin.close()
```

패치 후 **부품 수가 같고**, 달라진 부품이 의도한 것뿐이며,
`xl/slicers/`·`xl/slicerCaches/`가 남아 있는지, `Requires="sle15"` 가 슬라이서 수만큼
보존됐는지 확인한다. 검증에 실패하면 원본을 유지한다.
★**ElementTree 로 하지 않는다** — 접두사가 바뀌어 `Requires` 참조가 끊긴다. 위처럼 정규식으로 한다.

**틀고정을 XML로 넣어야 한다면** `<sheetViews>`(복수)가 아니라 **`<sheetView ...>`(단수) 여는 태그 바로 뒤**에
넣는다. 복수 태그 뒤에 넣으면 Excel이 조용히 버린다. 애초에 1단계에서 `freeze_panes`로 거는 편이 안전하다.

### 4단계 검증 게이트 ★필수★ — 납품 차단 장치

빌드가 끝나면 **반드시** 아래를 실행한다. 종료코드가 0이 아니면 **납품하지 않는다.**

```
python "C:\AI\NPL\온비드\_검증도구\verify_explore.py" ^
   <만든 xlsx 전부> --prev "<지난 회차 폴더>" --json "<저장폴더>\verify_<YYYYMMDD>.json"
```

- 읽기 전용이다. openpyxl 을 쓰지 않으므로 슬라이서를 파괴하지 않는다.
- `--prev` 를 주면 **전 회차 대비 회귀**(슬라이서 개수·크기)를 본다.
  「지난주엔 있었는데 이번주엔 없다」류 결함은 이 비교로만 잡힌다.
- 검사 항목: S1~S7(슬라이서 존재·**기하 144×170pt**·규모대/구간 필수)
  · F1~F5(스필 수식·범위 정합·보조열 수식 수·**KPI가 SUBTOTAL인지**·캐시 오류)
  · L1~L5(틀고정·행높이 218pt·B/C 폭·눈금선·숨김행) · P1~P2(회귀).
- **게이트 출력 원문과 종료코드를 보고에 그대로 붙인다.** 손으로 「통과」라고 쓰지 않는다.
- 게이트가 통과해도 ⑪(육안)·⑭(다중선택 실측)는 별도로 한다. 게이트는 파일 구조만 본다.

★게이트가 오탐을 내면 게이트를 끄지 말고 게이트를 고친다.
  (실측 2건: `customHeight="1"` 의 뒤쪽 `ht="1"` 오매칭 / Excel 의 공유수식 `t="shared"` 압축)

★게이트 스크립트가 없는 환경이면 **같은 검사를 손으로라도 한다.**
  최소한 `xl/drawings/drawing1.xml` 에서 `twoCellAnchor` 잔여 0 과 `cx=1828800 cy=2159000` 을 확인한다.

---

## 하지 말 것

- **`recalc.py`(LibreOffice)를 이 양식에 돌리지 않는다.** `FILTER`·`LET`을 평가하지 못해
  `#NAME?`이 파일에 박히고 스필 메타데이터가 사라진다. 검증은 Excel MCP로 값을 읽어서 한다.
- **원본 표 행을 숨기거나 그룹으로 접지 않는다.** 숨기면 보조열이 0이 되어 결과가 전부 빈다.
- **openpyxl로 파일을 다시 저장하지 않는다.** 슬라이서가 삭제되고 피벗차트가 일반 차트로 강등된다.
  (열 폭 수정도 Excel MCP `range_format(set-column-width)`로 한다)
- **대시보드 시트에 슬라이서를 두지 않는다.** 피벗마다 캐시가 달라 하나로 전체를 거르지 못한다.
  드릴다운은 탐색 시트 전용이다.
- **연속값 열(금액·비율·날짜)에 슬라이서를 직접 걸지 않는다.** 항목이 행 수만큼 생겨 못 쓴다.
  반드시 구간 파생열을 거친다. 값이 거의 전부 고유한 열(사건번호·소재지·비고 등)도 마찬가지다.
- **컬럼을 추가·삽입했으면 오른쪽 열들의 너비를 다시 잡는다.** 너비는 열 문자에 붙어 있어
  컬럼이 밀리면 날짜·금액 열이 `#######`으로 깨진다.
- **무인 회차에서 승인 팝업 도구를 부르지 않는다.** (위 「무인 실행 원칙」)
- **3·4단계를 「선택 사항」으로 판단해 생략하지 않는다.** (2026-09-21 사고)

---

## 납품 전 점검

저장하고 **다시 열어서 읽은 값**으로 확인한다. 호출 성공은 증거가 아니다.

| # | 항목 | 확인 방법 | 기대값 |
|---|---|---|---|
| ① | 슬라이서 → 15행부터 즉시 표시 | 한 항목 선택 후 `A15:E34` 읽기 | 행이 채워짐 |
| ② | 선택 건수 = 결과 행 수 | `C4` vs 스필 행 수 | 일치 |
| ③ | 전체 해제 시 전량 표시 | `C4`, 마지막 스필 행 | C4 = 전체 건수 |
| ④ | 중복 표시 없음 | 원본 표가 결과 영역 아래인가 | 예 |
| ⑤ | 13·14행 안 가려짐 | 1~12행 높이 합 ≥ 218pt | 예 |
| ⑥ | 금액 원 단위 콤마 | `range(get-number-formats)` | `#,##0` |
| ⑦ | 오류 없음 | `#REF! #VALUE! #SPILL! #NAME?` 스캔 | 0건 |
| ⑧ | 원본 행 숨김 없음 | `row_dimensions[r].hidden` | 0건 |
| ⑨ | 슬라이서 전체 선택 상태 | `slicer(list-table-slicers)` | selected 개수 = available 개수 |
| ⑩ | 틀고정 유지 | `sheet1.xml`의 `<pane/>` | `ySplit="14" topLeftCell="A15"` |
| ⑪ | 화면 육안 확인 | `screenshot(capture)` A1:H18 | `####`·라벨 잘림·슬라이서 겹침 없음 |
| ⑫ | **금액 규모대 슬라이서 존재** | `slicer(list-table-slicers)` | 존재 + availableItems ≥ 2 |
| ⑬ | **다중선택 기하** | `verify_explore.py` S4 | absoluteAnchor · 144×170pt · twoCell 잔여 0 |
| ⑭ | **다중선택 실측** | 한 슬라이서에 2개 동시 선택 → `C4` | 각 항목 건수의 합과 일치 |

**★⑪·⑬·⑭는 만든 탐색 시트 파일 전부에서 한다. 대표 1개만 실측하고 나머지를 「구조가 같으니 통과」로
적지 않는다.** [확정 2026-09-21] 그렇게 적은 회차에서 4종 전부 결함이 있었는데 보고서에는
통과로 적혀 있었다. 파일이 4개면 실측도 4번이다.

**⑨는 슬라이서 하나만 되돌리고 끝내면 안 된다 — 전부 확인한다.**
필터가 걸린 채 저장되면 사용자가 파일을 열었을 때 일부만 보이고, 그것을 전체로 착각한다.
실측으로 두 번 발생했다.
★⑭ 를 위해 슬라이서 선택을 바꿨으면 **반드시 전체선택으로 되돌리고 저장**한다.

**⑫·⑬·⑭ 중 하나라도 통과하지 못하면 납품하지 않는다.**
금액 규모대가 빠졌거나 다중선택이 안 되는 탐색 시트는 미완성이다.

사용자 PC에 OneDrive 자동 저장이 켜져 있으면, 사용자가 슬라이서를 눌러 본 뒤 닫을 때
**그 필터 상태가 그대로 저장된다.** 기존 파일을 다시 손댈 때는 ⑨를 먼저 확인하고
전체선택으로 되돌린 뒤 작업한다.

피벗을 함께 만들었다면 값 필드마다 `set-field-format`을 별도 호출하고(생성 시 인자는 조용히 무시됨),
총합계 행은 `range(set-number-format)`으로 따로 건다.

---

## 보고

```
파일: <경로> (신규 / 기존 갱신 — 갱신이면 백업 위치)
전체 N건 · 원본 표 A{RAWHDR}:{끝열}{끝행}
슬라이서: <이름 목록>  ← 금액 규모대 포함 여부 명시
3단계 XML 패치: 적용 여부 + 부품 수 대조 + twoCell 잔여 수
점검 ①~⑭: 통과 / 실패 항목 명시   ← 읽어서 확인한 값을 적는다 (파일별로)
검증 게이트: verify_explore.py 종료코드 + 출력 원문 그대로 첨부  ← 요약 금지
드릴다운 실측: <조건> → N건 (C4와 결과 행 수 일치)
다중선택 실측: <슬라이서> 2개 동시 선택 → C4 = a + b (파일별로)
파일 잠금 여부 (_v2 로 저장했으면 명시)
```

검증하지 않은 항목을 "확인했다"고 쓰지 않는다. 못 한 검증은 그대로 밝힌다.
**"구조가 같으니 통과"는 검증이 아니다.**

---

## 변경 이력

- **2026-09-08 (무인실행 중단 사고 반영)**: 「무인 실행 원칙」 절 신설 —
  승인 팝업 도구 호출 금지. / 2단계의 「사용자가 파일을 열어 두면 … 닫아달라고 요청한 뒤
  같은 이름으로 재시도」를 **대화형/무인 회차로 분기**해, 무인에서는 `_v2` 저장 + 보고로
  바꿨다. 종전 문구는 응답할 사람이 없는 회차를 그 자리에 세웠다.
  / 보고 형식에 파일 잠금 항목 추가.

- **2026-09-21 (다중선택 누락 사고 반영)**: 3단계 XML 패치를 **「선택」→「필수」로 승격**.
  폭이 144pt 미만이면 Excel 이 「다중 선택」 버튼을 잘라낸다는 사실과 실사고 근거를 명시했다.
  / **4단계 검증 게이트**(`verify_explore.py`) 신설 — 종료코드 0이 아니면 납품 차단,
  전 회차 회귀 비교 포함. / 납품 전 점검에 **⑬ 다중선택 기하 · ⑭ 다중선택 실측** 추가하고,
  **전 파일 실측**을 명문화했다(대표 1개 실측 후 나머지를 「구조 동일」로 통과 처리 금지).
  / 보고 형식에 3단계 적용 여부와 게이트 출력 원문 첨부를 의무화했다.
  / 「하지 말 것」에 “3·4단계를 선택 사항으로 판단해 생략하지 않는다” 추가.

