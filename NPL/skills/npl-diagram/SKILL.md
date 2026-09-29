---
name: "npl-diagram"
description: "NPL·경매 분석 도표를 draw.io(.drawio) 편집 가능 파일로 생성. 배당 순위 흐름·권리 타임라인·명도 D+N 절차 3종, XML 무결성 검사, 줄바꿈은 br 태그(\\n 무시됨), 금액 원 단위 풀 콤마, 배당 합계 검산. 트리거: drawio, 다이어그램 만들어, 편집 가능한 도표, 흐름도, 배당 흐름도, 권리 타임라인, 명도 절차도, 수정할 수 있는 그림. 고정 이미지는 npl-svg-chart."
---

> **수강생판 안내 (2026-09-29)** — 강사의 운영 스킬을 경로·식별정보만 바꿔 옮긴 것입니다.
> - 작업 루트 `C:\AI\NPL\` · 실거래 창고 `C:\AI\경매창고.duckdb`(03단원에서 만든 것) · 회사명·법인번호는 `[내 회사명]`·`[법인등록번호]` 로 비워 두었습니다.
> - 본문에 나오는 `ggi-collect` · `ggi-running-collect` · `ggi-interest-npl-scan` · `suhyup-npl-daily-scan` · `coefficient-auto-update` · `coefficient-self-diagnosis` · `bid-win-curve` · 예약작업은 **강사 운영 환경 전용**이라 수강생판에 없습니다. 그 줄은 「강사는 이렇게 자동화한다」로 읽고 넘어가면 됩니다.
> - `00_시장데이터\` 아래 낙찰 DB·계수이력·수집 스크립트는 강사 사내 자산입니다. 없으면 본문의 **고정 계수표 [추정]** 를 씁니다.
> - 실제 사건은 A사건·B사건·A물건처럼 익명화했습니다.

# NPL 도표 — draw.io 파일 생성

NPL·경매 분석 도표를 **`.drawio` 파일**로 만든다. 사용자가 draw.io에서 열어 **직접 수정**할 수 있다.

| 도표 | 언제 쓰나 |
|---|---|
| **배당 순위 흐름** | 낙찰가에서 순위별로 흘러 우리 채권에 얼마가 남는지 |
| **권리 타임라인** | 등기 권리를 시간축에 배치하고 말소기준을 표시 |
| **명도 D+N 절차** | 낙찰일 기준 D+0 ~ D+90 마일스톤 |

## `npl-svg-chart` 와 어느 것을 쓰나

| | 이 스킬 (.drawio) | `npl-svg-chart` (.svg/.png) |
|---|---|---|
| 목적 | **나중에 직접 고칠** 도표 | **그대로 넣을** 완성 도표 |
| 편집 | draw.io에서 자유롭게 | 코드를 고쳐 다시 생성 |
| PPTX 삽입 | draw.io에서 PNG 내보내기 필요 | 바로 삽입 |

**PPTX 물건카드에 넣을 것은 `npl-svg-chart`.** 이 스킬은 절차·구조를 설명하고 손볼 여지를 남길 때 쓴다.

---

## ★★ 줄바꿈은 `&lt;br&gt;` 다 — `\n` 은 무시된다

스타일에 `html=1` 이 들어가므로 **draw.io 는 `\n` 을 줄바꿈으로 렌더하지 않는다.**
에러 없이 한 줄로 붙어 나온다. **draw.io 로 열어 보기 전에는 모른다.**

```
✗ value="낙찰가\n1,740,749,525원"          → "낙찰가 1,740,749,525원" (한 줄)
✓ value="낙찰가&lt;br&gt;1,740,749,525원"   → 두 줄
```

**2026-08-27 실측** — 첫 판에서 6개 라벨이 전부 한 줄로 붙었다. `&lt;br&gt;` 로 바꿔 재확인했다.
아래 생성기의 `_box()` 가 이 변환을 자동으로 한다. **직접 XML을 쓰지 말고 생성기를 쓴다.**

---

## STEP 1 — 생성기를 `/tmp/npl_drawio.py` 로 쓴다

```python
# -*- coding: utf-8 -*-
from xml.sax.saxutils import escape

C = dict(blue="#1456F0", lblue="#3B82F6", ink="#222222", slate="#45515E",
         gray="#8E8E93", line="#D9DCE1", high="#DC2626", med="#D97706",
         green="#059669", card="#FFFFFF", bg="#F4F5F7")

def won(n): return f"{int(n):,}원"        # 원 단위 풀 콤마. 억·만 축약 금지

def _box(i, x, y, w, h, label, fill, stroke, fontcolor="#FFFFFF", size=13, bold=1, rounded=1):
    st = (f"rounded={rounded};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
          f"fontColor={fontcolor};fontSize={size};fontStyle={bold};align=center;verticalAlign=middle;"
          f"arcSize=12;shadow=0;")
    # ★ html=1 이므로 줄바꿈은 \n 이 아니라 &lt;br&gt; 여야 한다
    v = escape(label).replace("\n", "&lt;br&gt;")
    return (f'<mxCell id="n{i}" value="{v}" style="{st}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

def _edge(i, src, dst, label="", dashed=0, color=None):
    st = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={color or C['slate']};"
          f"strokeWidth=2;dashed={dashed};endArrow=block;endFill=1;fontSize=11;fontColor={C['slate']};")
    return (f'<mxCell id="e{i}" value="{escape(label)}" style="{st}" edge="1" parent="1" '
            f'source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry"/></mxCell>')

def _wrap(cells, name, w=1100, h=900):
    return ('<mxfile host="app.diagrams.net" type="device">'
            f'<diagram name="{escape(name)}" id="d1">'
            f'<mxGraphModel dx="{w}" dy="{h}" grid="1" gridSize="10" guides="1" tooltips="1" '
            f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="826" '
            f'math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            + "".join(cells) +
            '</root></mxGraphModel></diagram></mxfile>')

# ── 1. 배당 순위 흐름 ────────────────────────────────
def dist_flow(bid, steps, title, ours):
    """steps: [{name, amount, color?}] 순위 순 · ours: {'name':..,'claim':..}"""
    cells, i, y = [], 0, 100
    cells.append(_box("T", 40, 30, 1000, 44, title, C["ink"], C["ink"], size=16))
    cells.append(_box(i, 400, y, 280, 56, f"낙찰가\n{won(bid)}", C["blue"], C["blue"], size=14))
    prev, rem, i = f"n{i}", bid, i + 1
    for s in steps:
        y += 100
        amt = min(s["amount"], rem)
        rem -= amt
        cells.append(_box(i, 130, y, 240, 52, f"{s['name']}\n−{won(amt)}",
                          s.get("color", C["med"]), s.get("color", C["med"]), size=12))
        cells.append(_box(i+1, 400, y, 280, 56, f"잔액\n{won(rem)}", C["card"], C["line"],
                          fontcolor=C["ink"], size=13))
        cells.append(_edge(i, prev, f"n{i+1}"))
        cells.append(_edge(i+1, f"n{i+1}", f"n{i}", "", 1, s.get("color", C["med"])))
        prev, i = f"n{i+1}", i + 2
    y += 100
    받는금액 = min(rem, ours["claim"])
    col = C["green"] if 받는금액 >= ours["claim"] else C["high"]
    cells.append(_box(i, 400, y, 280, 64, f"{ours['name']}\n배당 {won(받는금액)}", col, col, size=14))
    cells.append(_edge(i, prev, f"n{i}"))
    i += 1
    미회수 = ours["claim"] - 받는금액
    note = (f"채권액 {won(ours['claim'])} · 전액 회수" if 미회수 == 0
            else f"채권액 {won(ours['claim'])} · 미회수 {won(미회수)}")
    cells.append(_box(i, 400, y + 80, 280, 40, note, C["bg"], C["line"],
                      fontcolor=C["ink"], size=11, bold=0))
    return _wrap(cells, "배당 순위 흐름")

# ── 2. 권리 타임라인 ────────────────────────────────
def rights_timeline(items, title):
    """items: [{date, kind, holder, amount, fate}] fate = 인수/소멸/기준"""
    cells, i, x, STEP = [], 0, 60, 175
    cells.append(_box("T", 40, 30, 1000, 44, title, C["ink"], C["ink"], size=16))
    cells.append(f'<mxCell id="axis" value="" style="endArrow=block;html=1;strokeColor={C["line"]};'
                 f'strokeWidth=3;" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="40" y="260" as="sourcePoint"/>'
                 f'<mxPoint x="{60+STEP*len(items)}" y="260" as="targetPoint"/></mxGeometry></mxCell>')
    for it in items:
        fate = it["fate"]
        col = {"인수": C["high"], "소멸": C["gray"], "기준": C["blue"]}[fate]
        amt = f"\n{won(it['amount'])}" if it.get("amount") else ""
        up = (i % 2 == 0)
        by = 130 if up else 300
        cells.append(_box(i, x, by, 155, 88, f"{it['kind']}\n{it['holder']}{amt}",
                          C["card"], col, fontcolor=C["ink"], size=11, bold=0))
        cells.append(_box(f"{i}d", x + 30, 240, 95, 26, it["date"], col, col, size=10))
        cells.append(f'<mxCell id="c{i}" value="" style="endArrow=none;html=1;strokeColor={col};'
                     f'strokeWidth=2;dashed=1;" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                     f'<mxPoint x="{x+77}" y="{by+88 if up else by}" as="sourcePoint"/>'
                     f'<mxPoint x="{x+77}" y="{240 if up else 266}" as="targetPoint"/></mxGeometry></mxCell>')
        if fate == "기준":
            cells.append(_box(f"{i}m", x + 5, 375, 145, 30, "★ 말소기준권리", C["blue"], C["blue"], size=11))
        x += STEP
        i += 1
    cells.append(_box("L", 60, 430, 620, 34, "파랑 = 말소기준 · 빨강 = 인수 · 회색 = 소멸",
                      C["bg"], C["line"], fontcolor=C["slate"], size=11, bold=0))
    return _wrap(cells, "권리 타임라인")

# ── 3. 명도 D+N 절차 ────────────────────────────────
def eviction_flow(낙찰일, title, 점유자="채무자"):
    from datetime import date, timedelta
    d0 = date.fromisoformat(낙찰일)
    def dd(n): return (d0 + timedelta(days=n)).isoformat()
    steps = [
        (0,  "낙찰",                  "매각허가결정 대기", C["blue"]),
        (7,  "매각허가결정",           "확정까지 7일 항고기간", C["blue"]),
        (14, "대금지급기한 통지",       "통상 낙찰 후 1개월 내", C["med"]),
        (30, "잔금 납부 · 소유권 취득", "이때부터 인도명령 신청 가능", C["green"]),
        (31, "인도명령 신청",          "점유자 수만큼 각각 신청", C["med"]),
        (45, "인도명령 결정",          "송달 후 확정", C["med"]),
        (60, "강제집행 신청",          "집행관 계고", C["high"]),
        (90, "명도 완료",              "합의 또는 강제집행", C["green"]),
    ]
    cells, i, y, prev = [], 0, 100, None
    cells.append(_box("T", 40, 30, 1000, 44, title, C["ink"], C["ink"], size=16))
    for n, name, note, col in steps:
        cells.append(_box(i, 120, y, 200, 30, f"D+{n}  ({dd(n)})", col, col, size=11))
        cells.append(_box(i+1, 360, y - 8, 380, 46, f"{name}\n{note}", C["card"], col,
                          fontcolor=C["ink"], size=12, bold=0))
        if prev: cells.append(_edge(i, prev, f"n{i}"))
        prev, i, y = f"n{i}", i + 2, y + 78
    cells.append(_box(i, 790, 340, 240, 100, "협상 분기\n합의 이사비가\n강제집행보다 싸다",
                      C["bg"], C["med"], fontcolor=C["ink"], size=11, bold=0))
    cells.append(_box(i+1, 120, y + 20, 900, 40,
                      f"점유자: {점유자} · 점유자 수만큼 인도명령이 필요하다 · 명도 공백기 이자를 총투입에 넣는다",
                      C["bg"], C["line"], fontcolor=C["slate"], size=11, bold=0))
    return _wrap(cells, "명도 D+N 절차")
```

**D+N 일수는 통상값이다** — 사건마다 다르다. 서류로 확인된 기일이 있으면 그 값으로 바꾸고 `[확정]` 을 붙인다.

## STEP 2 — 데이터를 넣어 만든다

```python
from npl_drawio import *

open("배당흐름.drawio", "w", encoding="utf-8").write(dist_flow(
    1_740_749_525,
    [dict(name="당해세 (중랑구 재산세 토지)", amount=1_700_000, color=C["med"]),
     dict(name="최우선변제 (소액임차인)",      amount=240_000_000, color=C["med"])],
    "배당 순위 흐름 — 북부4계 C사건",
    dict(name="1순위 근저당 · △△수협", claim=1_331_348_418)))
```

**색 규칙** — 인수 `DC2626` / 소멸 `8E8E93` / 기준 `1456F0` / 당해세·최우선변제 `D97706` / 전액회수 `059669`

**확인 못 한 값은 `[검증필요]`·`[가정]` 을 라벨 안에 쓴다.** 그림은 글보다 확정적으로 읽힌다.

## STEP 3 — 무결성 검사 ★ 저장 전에 반드시

```python
import xml.etree.ElementTree as ET
r = ET.parse(f).getroot()
assert r.tag == "mxfile", "루트가 mxfile 이 아니다"
root = r.find(".//root")
ids = {c.get("id") for c in root.findall("mxCell")}
assert "0" in ids and "1" in ids, "필수 셀 0/1 누락 — draw.io 가 열지 못한다"
for c in root.findall("mxCell"):
    for k in ("parent", "source", "target"):
        v = c.get(k)
        assert v is None or v in ids, f"존재하지 않는 {k}: {v}"
```

**셀 `0` 과 `1` 이 없으면 draw.io 가 빈 문서로 연다.** 에러는 나지 않는다.
`source`/`target` 이 없는 id를 가리키면 그 선만 조용히 사라진다.

## STEP 4 — draw.io 로 열어 **눈으로 본다** ★

파일을 만든 것으로 끝내지 않는다. 아래 URL로 브라우저에서 연다.

```python
from urllib.parse import quote
xml = open("배당흐름.drawio", encoding="utf-8").read()
url = "https://app.diagrams.net/?splash=0&ui=min#R" + quote(xml, safe="")
```

확인할 것

1. **줄바꿈이 됐는가** — 한 줄로 붙어 있으면 `&lt;br&gt;` 문제다
2. 한글이 깨지지 않았는가
3. 상자가 겹치거나 화살표가 엉키지 않았는가
4. 금액이 **원 단위 풀 콤마**인가

**7KB 정도까지는 URL 로 열린다.** 더 크면 파일을 직접 열게 안내한다.

## STEP 5 — 배당 흐름은 검산한다 ★

```python
남은배당 = bid - sum(s["amount"] for s in steps)
assert 남은배당 == 배당표의_값, "검산 실패 — 그림이 아니라 원 데이터를 다시 본다"
```

**`배당` 은 회수액이지 채권액이 아니다.** 생성기가 `min(잔액, 채권액)` 으로 자르고
미회수 잔액을 아래 상자에 함께 적는다. 그 상자를 지우지 않는다.

---

## 사용자에게 안내할 것

`.drawio` 파일은 **draw.io 에서 열어 직접 수정**할 수 있다. 설치 불필요.

```
app.diagrams.net → 열기 → 기존 다이어그램 열기 → 파일 선택
```

PPTX 에 넣으려면 draw.io 에서 `파일 → 내보내기 → PNG` 를 쓴다.
**처음부터 PPTX 용이면 이 스킬 대신 `npl-svg-chart` 를 쓰는 편이 빠르다.**

## 하지 않는 것

- **`\n` 으로 줄바꿈하기** — html=1 에서는 무시된다. `_box()` 를 우회하지 않는다
- **XML 을 손으로 쓰기** — 생성기를 쓴다. 셀 0/1 누락·참조 깨짐이 조용히 난다
- **압축(base64+deflate) 저장** — 평문이어야 나중에 텍스트로 고칠 수 있다
- **무결성 검사·육안 확인 건너뛰기** — 둘 다 조용한 실패를 잡는 유일한 장치다
- **금액을 억·만으로 축약하기** — `won()` 만 쓴다
- **배당 흐름을 검산 없이 내기**
- **확인 못 한 값을 라벨 없이 그리기**
- **D+N 통상값을 확정 기일처럼 쓰기**
- 그림으로 결론을 대신하기. **판단은 본문에 글로 쓴다**

## 다른 스킬과의 관계

- `npl-svg-chart` — 고정 이미지가 필요할 때. 색 규격을 공유한다
- `auction-property-card` — 물건카드 PPTX. 도표는 PNG 로 넣는다
- `post-auction-eviction` — 명도 D+N 의 실제 절차·서식은 그쪽이 정본이다
- `number-format-guard` — 금액 표기 규칙

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-08-27 | 신설. 3종을 실제로 만들어 draw.io(app.diagrams.net)에서 열어 확인했다. 첫 판에서 **줄바꿈 6개가 전부 한 줄로 붙는 결함**을 발견해 `\n` → `&lt;br&gt;` 변환을 `_box()` 에 넣고 재검증했다. XML·parent/source/target 참조 무결성 검사를 STEP 3 으로 못박았다 |


