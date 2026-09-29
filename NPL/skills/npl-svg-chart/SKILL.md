---
name: "npl-svg-chart"
description: "NPL·경매 분석용 도표를 SVG로 생성해 PNG 확인 후 PPTX에 넣는다. 권리 순위 사다리(인수/소멸/기준 + 당해세·최우선 주황 배지 = 소멸하되 0순위 배당), 문건 타임라인, 배당 폭포 3종. 색상은 NPL분석 PPTX 규격, 금액 원 단위 풀 콤마, 배당 폭포 합계 검산, 사다리 당해세 = 엑셀 C20 = 폭포 3자 일치, font-family 첫 항목은 샌드박스 실재 폰트. 트리거: 권리관계도, 말소기준 도표, 문건 타임라인, 배당 폭포, 배당 흐름도, 권리분석 시각화, 당해세 표시, PPTX에 넣을 그림, 한글이 깨져. 편집 가능 파일은 npl-diagram."
---

> **수강생판 안내 (2026-09-29)** — 강사의 운영 스킬을 경로·식별정보만 바꿔 옮긴 것입니다.
> - 작업 루트 `C:\AI\NPL\` · 실거래 창고 `C:\AI\경매창고.duckdb`(03단원에서 만든 것) · 회사명·법인번호는 `[내 회사명]`·`[법인등록번호]` 로 비워 두었습니다.
> - 본문에 나오는 `ggi-collect` · `ggi-running-collect` · `ggi-interest-npl-scan` · `suhyup-npl-daily-scan` · `coefficient-auto-update` · `coefficient-self-diagnosis` · `bid-win-curve` · 예약작업은 **강사 운영 환경 전용**이라 수강생판에 없습니다. 그 줄은 「강사는 이렇게 자동화한다」로 읽고 넘어가면 됩니다.
> - `00_시장데이터\` 아래 낙찰 DB·계수이력·수집 스크립트는 강사 사내 자산입니다. 없으면 본문의 **고정 계수표 [추정]** 를 씁니다.
> - 실제 사건은 A사건·B사건·A물건처럼 익명화했습니다.

# NPL 도표 SVG 생성

경매·NPL 분석에 쓰는 도표 3종을 **SVG**로 만들고, **PNG로 렌더해 눈으로 확인한 뒤** PPTX에 넣는다.

| 도표 | 언제 쓰나 |
|---|---|
| **권리 순위 사다리** | 등기부 권리를 순서대로 세우고 말소기준 아래·위로 인수/소멸을 가른다 |
| **문건 타임라인** | 법원 문건접수·송달을 시간순으로 늘어놓고 위험도를 색으로 표시한다 |
| **배당 폭포** | 낙찰가에서 순위별로 깎여나가 우리 채권에 얼마가 남는지 보인다 |

---

## ★★ 폰트 — 여기서 두 번 깨졌다

**`font-family` 의 첫 항목은 반드시 샌드박스에 실재하는 폰트여야 한다.**

`Pretendard` 를 맨 앞에 두면 cairosvg 가 **폴백하지 않고 한글을 전부 □ 로 렌더한다.**
에러는 나지 않는다. PNG는 정상 생성되고, **눈으로 봐야만 알 수 있다.**

```
✗ "Pretendard, Noto Sans CJK KR, sans-serif"      ← 한글 전멸
✓ "Noto Sans CJK KR, Pretendard, Malgun Gothic, sans-serif"
```

Windows PowerPoint 에는 `Noto Sans CJK KR` 이 대개 없으므로 자동으로 `Pretendard` 로 떨어진다.
**어느 쪽에서도 깨지지 않는 순서가 위 하나뿐이다.**

### 폰트 가드 — 매번 실행한다

```python
import subprocess
def font_guard(font_family):
    first = font_family.split(",")[0].strip().strip("'\"")
    if not subprocess.run(["fc-list", first], capture_output=True).stdout.strip():
        raise AssertionError(f"첫 폰트 '{first}' 가 시스템에 없다 — cairosvg 가 한글을 □ 로 렌더한다")
    return first
```

**변이 검증 통과 (2026-08-27)** — 결함 순서를 넣으면 `차단`, 고친 순서를 넣으면 `통과`.
가드를 지우거나 우회하지 않는다.

---

## ★ 왜 손으로 SVG를 쓰지 않는가

**2026-08-27 실측 — 손으로 쓴 첫 판에서 레이아웃 결함 2개가 나왔다.**

1. 배당 폭포의 낙찰가 금액이 막대 위에 겹쳐 읽히지 않았다
2. `−0원` 행이 그려져 표가 지저분해졌다

**그리고 첫 실전 테스트에서 폰트 결함이 하나 더 나왔다** (위 항목).
**셋 다 PNG를 눈으로 보기 전에는 몰랐다.** 그래서 아래 생성기를 쓰고 반드시 렌더해 확인한다.
생성기는 이 문서 안에 있다. 외부 스크립트·zip에 의존하지 않는다.

---

## STEP 1 — 준비

```bash
pip install cairosvg --quiet --break-system-packages
```

## STEP 2 — 생성기를 `/tmp/npl_svg.py` 로 쓴다

**이 코드를 그대로 쓴다.** 좌표·폰트 순서는 실측으로 맞춘 값이다. 임의로 바꾸면 깨진다.

```python
# -*- coding: utf-8 -*-
import subprocess

# ★ 순서를 바꾸지 마라. Pretendard 를 앞에 두면 한글이 □ 가 된다
F = "Noto Sans CJK KR, Pretendard, Malgun Gothic, sans-serif"

def font_guard(font_family=F):
    first = font_family.split(",")[0].strip().strip("'\"")
    if not subprocess.run(["fc-list", first], capture_output=True).stdout.strip():
        raise AssertionError(f"첫 폰트 '{first}' 가 시스템에 없다 — 한글이 □ 로 렌더된다")
    return first

C = dict(blue="#1456F0", lblue="#3B82F6", ink="#222222", slate="#45515E",
         gray="#8E8E93", bg="#F4F5F7", card="#FFFFFF", line="#D9DCE1",
         high="#DC2626", med="#D97706", low="#8E8E93", green="#059669")

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def won(n):
    return f"{int(n):,}원"          # 원 단위 풀 콤마. 억·만 축약 금지

def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{F}">'
            f'<rect width="{w}" height="{h}" fill="{C["bg"]}"/>')

def txt(x, y, s, size=13, fill=None, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or C["ink"]}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')

# ── 1. 권리 순위 사다리 ──────────────────────────────
def rights_ladder(items, title, sub=None, w=1000):
    """items: [{date, kind, holder, amount, fate}]
    fate = 인수 / 소멸 / 기준 / 당해세 / 최우선
      당해세  = 소재지 구·면 관할 지자체 압류 → 0순위 배당(경매비용 다음, 근저당 앞). 금액 필수
      최우선  = 소액임차인 최우선변제 → 0순위 배당. 금액 필수(상한 가정이면 kind에 [가정] 표기)
    당해세·최우선을 "소멸"로 그리지 않는다 — 소멸은 맞지만 배당에서 근저당보다 앞선다는 사실이 사라진다"""
    ROW, TOP = 46, 92
    h = TOP + ROW * len(items) + 40
    o = [head(w, h), txt(28, 44, title, 20, C["ink"], "bold"),
         txt(28, 68, sub or "말소기준권리 아래는 소멸 · 위는 인수 · 주황 배지(당해세·최우선)는 소멸하되 0순위 배당", 12, C["gray"])]
    for i, it in enumerate(items):
        y = TOP + i * ROW
        fate = it["fate"]
        col = {"인수": C["high"], "소멸": C["gray"], "기준": C["blue"],
               "당해세": C["med"], "최우선": C["med"]}[fate]
        if fate in ("당해세", "최우선"):
            assert it.get("amount"), f"{fate} 행은 금액이 있어야 한다 — 배당표 0순위와 대조하지 못한다"
        o.append(f'<rect x="28" y="{y}" width="{w-56}" height="{ROW-8}" rx="5" '
                 f'fill="{C["card"]}" stroke="{C["line"]}"/>')
        o.append(f'<rect x="28" y="{y}" width="5" height="{ROW-8}" rx="2.5" fill="{col}"/>')
        o.append(txt(48, y+25, f'{i+1}', 12, C["gray"], "bold"))
        o.append(txt(74, y+25, it["date"], 12, C["slate"]))
        o.append(txt(176, y+25, it["kind"], 13, C["ink"], "bold"))
        o.append(txt(330, y+25, it["holder"], 13, C["slate"]))
        if it.get("amount"):
            o.append(txt(w-150, y+25, won(it["amount"]), 13, C["ink"], "normal", "end"))
        o.append(f'<rect x="{w-138}" y="{y+7}" width="52" height="22" rx="11" fill="{col}"/>')
        o.append(txt(w-112, y+22, fate, 11, "#FFFFFF", "bold", "middle"))
        if fate == "기준":
            o.append(f'<line x1="28" y1="{y+ROW-4}" x2="{w-28}" y2="{y+ROW-4}" '
                     f'stroke="{C["blue"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    o.append("</svg>")
    return "\n".join(o)

# ── 2. 문건 타임라인 ────────────────────────────────
def timeline(events, title, sub=None, w=1000):
    """events: [{date, what, read, level}]  level = 위험 / 주의 / 보통"""
    h = 150 + 74 * len(events)
    AX = 190
    o = [head(w, h), txt(28, 44, title, 20, C["ink"], "bold"),
         txt(28, 68, sub or "법원 문건접수·송달 내역", 12, C["gray"]),
         f'<line x1="{AX}" y1="96" x2="{AX}" y2="{h-40}" stroke="{C["line"]}" stroke-width="2"/>']
    for i, e in enumerate(events):
        y = 122 + i * 74
        col = {"위험": C["high"], "주의": C["med"], "보통": C["blue"]}[e.get("level", "보통")]
        o.append(f'<circle cx="{AX}" cy="{y}" r="7" fill="{col}" stroke="{C["bg"]}" stroke-width="3"/>')
        o.append(txt(AX-22, y+5, e["date"], 12, C["slate"], "normal", "end"))
        o.append(f'<rect x="{AX+22}" y="{y-24}" width="{w-AX-52}" height="56" rx="5" '
                 f'fill="{C["card"]}" stroke="{C["line"]}"/>')
        o.append(txt(AX+38, y-4, e["what"], 13, C["ink"], "bold"))
        o.append(txt(AX+38, y+18, e["read"], 12, C["slate"]))
    o.append("</svg>")
    return "\n".join(o)

# ── 3. 배당 폭포 ───────────────────────────────────
def waterfall(bid, steps, title, sub=None, w=1000):
    """steps: [{name, amount, color?}] — 순위 순서대로. 0원 항목은 자동 제외"""
    live = [x for x in steps if x["amount"] > 0]
    h = 150 + 52 * len(live) + 70
    BARX, BARW = 300, w - 360
    o = [head(w, h), txt(28, 44, title, 20, C["ink"], "bold"),
         txt(28, 68, sub or f'예상 낙찰가 {won(bid)} 기준  [공제 전]', 12, C["gray"])]
    rem, y = bid, 100
    o.append(f'<rect x="{BARX}" y="{y}" width="{BARW}" height="26" rx="4" fill="{C["blue"]}"/>')
    o.append(txt(28, y+18, "낙찰가", 13, C["ink"], "bold"))
    # ★ 막대 안쪽 흰 글씨. 막대 밖에 두면 겹쳐 읽히지 않는다 (2026-08-27 실측 결함)
    o.append(txt(BARX+BARW-12, y+18, won(bid), 13, "#FFFFFF", "bold", "end"))
    y += 44
    for s in live:
        amt = min(s["amount"], rem)
        bw = max(2, BARW * (amt / bid if bid else 0))
        o.append(txt(28, y+18, s["name"], 13, C["slate"]))
        o.append(f'<rect x="{BARX}" y="{y}" width="{BARW}" height="26" rx="4" fill="#E8EAEE"/>')
        o.append(f'<rect x="{BARX}" y="{y}" width="{bw:.1f}" height="26" rx="4" '
                 f'fill="{s.get("color", C["lblue"])}"/>')
        o.append(txt(w-32, y+18, "−" + won(amt), 13, C["ink"], "normal", "end"))
        rem -= amt
        y += 44
    o.append(f'<line x1="28" y1="{y-8}" x2="{w-28}" y2="{y-8}" stroke="{C["line"]}"/>')
    col = C["green"] if rem > 0 else C["high"]
    o.append(txt(28, y+22, "우리 채권 배당", 14, C["ink"], "bold"))
    o.append(txt(w-32, y+22, won(rem), 16, col, "bold", "end"))
    o.append("</svg>")
    return "\n".join(o)
```

## STEP 3 — 데이터를 넣어 만든다

```python
from npl_svg import *
font_guard()          # ★ 반드시 먼저

open("권리순위.svg", "w", encoding="utf-8").write(rights_ladder([
    dict(date="2019-03-14", kind="근저당권", holder="○○수협",
         amount=2400000000, fate="기준"),
    dict(date="2021-07-02", kind="임차권등기", holder="임차인 김OO",
         amount=180000000, fate="소멸"),
    dict(date="2025-12-23", kind="압류 (지방세) 당해세", holder="강동구 · 소재지 관할 구 · 등기 표기 1127",
         amount=1127000, fate="당해세"),
], "권리 순위 · 인수/소멸 판정 — 인천3계 J사건"))
```

**색 배정 규칙**

| 도표 | 색 |
|---|---|
| 권리 사다리 | 인수 `DC2626` / 소멸 `8E8E93` / 기준 `1456F0` (점선 구분자 자동) / **당해세·최우선 `D97706`** (소멸하되 0순위 배당 — 배지 글자가 "당해세"·"최우선"으로 찍힌다) |
| 타임라인 | 위험 `DC2626` / 주의 `D97706` / 보통 `1456F0` |
| 배당 폭포 | 기본 `3B82F6`. **당해세·최우선변제는 `D97706`** 로 따로 칠해 눈에 띄게 한다 |

**채권자변경·승계·파산 문건은 반드시 `level="위험"`** 으로 넣는다. 즉시 반려 사유다.

### ★ 당해세·최우선변제는 사다리에서 "소멸"로만 두지 않는다 (2026-09-28 신설 · 대표 지시)

소재지와 같은 구·면 관할 지자체의 압류(npl-analysis 원칙 13으로 당해세 판정된 것)와 소액임차인 최우선변제는
**경매로 소멸하지만 배당에서는 근저당보다 앞선다.** 회색 「소멸」 배지로 그리면 그 사실이 그림에서 사라지고,
읽는 사람은 "우리 뒤에 있으니 무관"으로 오독한다(2026-09-21 A물건 사다리 — 계산에는 C20으로 들어가 있었으나
그림이 「소멸」이어서 대표가 "반영 안 됐다"고 읽었다).

- 당해세 압류 행: `fate="당해세"`, `amount`=천원 단위 환산액. holder 에 「등기 표기 1127 → 1,127,000원」처럼 근거를 쓴다
- 최우선변제 행: `fate="최우선"`, `amount`=MIN(상한, 보증금) 합계. 서류 미확보로 상한 가정이면 kind 에 `[가정]`. kind 는 12자 안쪽으로 짧게 — 길면 holder 글자와 겹친다(2026-09-28 렌더 확인)
- 세 숫자가 같아야 한다: **사다리 당해세 금액 = 엑셀 분석!C20 = 배당 폭포 「당해세」 행**. 최우선도 같다(C19 · 폭포 「최우선변제」 행)
- 배당 폭포에서는 이미 `D97706` 으로 칠하고 있다. 사다리도 같은 색이어야 두 그림이 한 이야기를 한다
- 금액 없는 당해세·최우선 행은 생성기가 `AssertionError` 로 막는다(변이 검증 통과 2026-09-28). 우회하지 않는다

### 확인 못 한 것은 그림에도 그대로 적는다

데이터가 없는 칸에 그럴듯한 값을 채우지 않는다. `[검증필요]`·`[가정]`·`[추정]` 을 **그림 안에** 쓰고,
부제(`sub` 인자)에 `⚠ 등기부 미확보` 처럼 한 줄로 밝힌다.
**그림은 글보다 확정적으로 읽힌다.** 라벨 없는 도표는 없는 사실을 만들어 낸다.

## STEP 4 — PNG로 렌더해 **눈으로 본다** ★ 건너뛰지 않는다

```python
import cairosvg
cairosvg.svg2png(url="권리순위.svg", write_to="권리순위.png", scale=1.5)
```

렌더한 PNG를 **`Read` 도구로 열어 직접 확인한다.** 아래를 본다.

1. **한글이 □ 로 깨지지 않았는가** ← 폰트 가드를 통과해도 한 번 더 본다
2. 글자가 막대·배지·다른 글자에 **겹치지 않는가**
3. 금액이 **원 단위 풀 콤마**인가 (억·만 축약이 섞이지 않았는가)
4. 항목이 카드 밖으로 넘치지 않는가
5. **당해세·최우선 행이 주황 배지인가** — 회색 「소멸」이면 반영 안 된 것이다

**호출 성공은 증거가 아니다.** 이미지를 보지 않고 「완료」라고 쓰지 않는다.

## STEP 5 — 배당 폭포는 검산한다 ★

```python
남은배당 = bid - sum(s["amount"] for s in steps if s["amount"] > 0)
assert 남은배당 == 그림에_찍힌_값, "검산 실패"
```

그림의 숫자와 배당표의 숫자가 **한 원이라도 다르면** 그림을 고치지 말고 **원 데이터를 다시 본다.**

**`우리 채권 배당` 은 회수액이지 채권액이 아니다.** 청구액보다 크게 나오면 그림이 과대평가한 것이다.
청구액과 나란히 적고 **미회수 잔액**을 함께 낸다.

```python
미회수 = 청구액 - min(남은배당, 청구액)
```

`우리 채권 배당`이 **음수면 빨간색**으로 나온다. 그건 배당이 매입가 아래로 내려간다는 뜻이니
보고 첫머리에 그 사실을 적는다.

## STEP 6 — PPTX에 넣는다

| 방법 | 언제 |
|---|---|
| **PNG 삽입** (`ppt_add_picture`) | **기본.** scale=2 로 렌더. 폰트·레이아웃이 어긋날 여지가 없다 |
| SVG 삽입 (`ppt_add_svg_icon`) | 나중에 PowerPoint에서 크기를 크게 바꿀 때만 |

**PNG를 물건 폴더에 남기지 않는다.** `auction-property-card` 규칙과 같다 — `/tmp` 에서 만들어 PPTX에 넣고 버린다.
**SVG 원본은 남긴다.** 수정할 때 다시 만들지 않아도 된다.

---

## 하지 않는 것

- **폰트 순서를 바꾸기** — 첫 항목이 샌드박스에 없으면 한글이 통째로 □ 가 된다
- **폰트 가드를 지우거나 건너뛰기**
- **렌더한 이미지를 보지 않고 넘어가기** — 결함 3개가 전부 눈으로만 잡혔다
- **좌표를 임의로 바꾸기** — 실측으로 맞춘 값이다. 바꾸려면 다시 렌더해 확인한다
- **금액을 억·만으로 축약하기** — `won()` 만 쓴다
- **배당 폭포 합계를 검산 없이 쓰기**
- **`우리 채권 배당` 을 청구액처럼 읽기** — 회수액이다. 미회수 잔액을 함께 낸다
- **0원 항목을 그리기** — 생성기가 자동 제외한다. 우회하지 않는다
- **당해세·최우선변제를 회색 「소멸」로 그리기** — 주황 배지 + 금액이다
- **확인 못 한 값을 라벨 없이 그리기**
- 외부 스크립트·zip을 받아 쓰기 — 이 문서가 전부다
- 그림으로 결론을 대신하기. **판단은 본문에 글로 쓴다**

## 다른 스킬과의 관계

- `npl-analysis` — 원칙 13(당해세 판정·표기)이 당해세 행의 근거다. 판정은 그쪽, 그리기는 여기
- `auction-property-card` — 물건카드 PPTX에 이 도표를 넣는다. 색 규격은 그쪽이 정본이다
- `ggi-interest-npl-scan` — NPL분석 PPTX 「03 권리분석」·「05 배당 시뮬레이션」에 쓴다
- `number-format-guard` — 금액 표기는 그 스킬 규칙을 따른다
- `mutation-test-guard` — 폰트 가드·당해세 금액 assert 는 그 스킬의 변이 검증을 통과했다

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-09-28 | **사다리 fate 에 `당해세`·`최우선` 추가 (`D97706`).** 당해세를 회색 「소멸」로 그려 배당 우선이 그림에서 사라진 결함(A물건, 대표 지적). 금액 없는 당해세·최우선 행은 assert 로 막고(변이 검증 통과), 사다리=C20=폭포 3자 일치 규칙 명시. A물건 사다리로 렌더 확인 |
| 2026-08-27 | **폰트 결함 수정 + 가드 신설.** 첫 실전 테스트(여주5계 I사건)에서 한글이 전부 □ 로 렌더됐다. 원인은 `font-family` 첫 항목 `Pretendard` 가 샌드박스에 없어 cairosvg 가 폴백하지 않은 것. `Noto Sans CJK KR` 을 앞으로 옮기고 `fc-list` 기반 가드를 넣었다(변이 검증 통과). 아울러 「우리 채권 배당 ≠ 청구액」·「미확인 값 라벨」 규칙을 추가 |
| 2026-08-27 | 신설. 3종 도표를 실제로 만들어 PNG 렌더까지 확인했다. 첫 판에서 발견한 결함 2개(낙찰가 금액 겹침·0원 행)를 생성기에 반영했다. 배당 폭포 검산(1,850,000,000 − 18,000,000 − 32,000,000 − 96,000,000 = 1,704,000,000) 통과 |

