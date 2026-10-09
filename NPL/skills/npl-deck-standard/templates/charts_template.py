# -*- coding: utf-8 -*-
"""물건카드 도표 4종 생성기 (견본) — 권리 사다리 · 문건 타임라인 · 배당 폭포 · 회차 시나리오.

숫자와 문구는 모두 _model.json 에서 읽는다. 이 파일에 숫자·이름을 직접 쓰지 않는다.
출력: 환경변수 CARD_CHARTS (없으면 이 파일 옆 charts/) 에 PNG 와 sizes.json.
렌더: cairosvg → 없으면 Windows Edge 헤드리스. 둘 다 없으면 SVG 만 남기고 멈춘다.

실행:  python charts_template.py [모델 경로]
"""
import json, os, sys, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_model.json")
if not os.path.exists(MODEL):
    MODEL = os.path.join(HERE, "sample_model.json")
M = json.load(open(MODEL, encoding="utf-8"))
OUTD = os.environ.get("CARD_CHARTS") or os.path.join(HERE, "charts")
os.makedirs(OUTD, exist_ok=True)

# ★ 첫 글꼴은 그 PC 에 실제로 있는 한글 글꼴이어야 한다. 없으면 한글이 □ 로 깨지고 에러는 나지 않는다.
F = "Malgun Gothic, Noto Sans CJK KR, Apple SD Gothic Neo, sans-serif"


def font_guard():
    """그 PC 에 실제로 있는 한글 글꼴을 font-family 첫 항목으로 올린다(cairosvg 는 다음 글꼴로 넘어가지 않는다)."""
    global F
    found = None
    if os.path.exists(r"C:\Windows\Fonts\malgun.ttf"):
        found = "Malgun Gothic"
    elif shutil.which("fc-list"):
        out = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
        for name in ("Malgun Gothic", "Noto Sans CJK KR", "Apple SD Gothic Neo", "NanumGothic"):
            if name in out:
                found = name
                break
    elif os.path.exists("/System/Library/Fonts/AppleSDGothicNeo.ttc"):
        found = "Apple SD Gothic Neo"
    if found:
        F = found + ", " + F
        return found
    raise SystemExit("한글 글꼴을 찾지 못했다 — 도표 한글이 □ 로 깨진다. 맑은 고딕 또는 Noto Sans CJK KR 설치 필요")


C = dict(blue="#1456F0", lblue="#3B82F6", ink="#222222", slate="#45515E", gray="#8E8E93", bg="#F4F5F7",
         card="#FFFFFF", line="#D9DCE1", high="#DC2626", med="#D97706", green="#059669")
FATE = {"인수": C["high"], "소멸": C["gray"], "기준": C["blue"], "당해세": C["med"], "최우선": C["med"], "안전": C["green"]}


def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def won(n): return f"{int(round(n)):,}원"


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{F}">'
            f'<rect width="{w}" height="{h}" fill="{C["bg"]}"/>')


def txt(x, y, s, size=13, fill=None, weight="normal", anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or C["ink"]}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'


def rights_ladder(items, title, sub=None, w=1000):
    """fate: 인수(빨강) · 소멸(회색) · 기준(파랑, 말소기준) · 당해세/최우선(주황 + 금액 필수)."""
    ROW, TOP = 46, 92
    h = TOP + ROW * len(items) + 40
    o = [head(w, h), txt(28, 44, title, 20, C["ink"], "bold"),
         txt(28, 68, sub or "말소기준 아래는 소멸 · 위는 인수 · 주황(당해세·최우선)은 소멸하되 먼저 배당", 12, C["gray"])]
    for i, it in enumerate(items):
        y = TOP + i * ROW
        fate = it["fate"]
        col = FATE[fate]
        if fate in ("당해세", "최우선"):
            assert it.get("amount"), f"{fate} 행은 금액이 있어야 한다 — 회색 「소멸」로 그리지 않는다"
        o.append(f'<rect x="28" y="{y}" width="{w-56}" height="{ROW-8}" rx="5" fill="{C["card"]}" stroke="{C["line"]}"/>')
        o.append(f'<rect x="28" y="{y}" width="5" height="{ROW-8}" rx="2.5" fill="{col}"/>')
        o.append(txt(48, y + 25, f'{i+1}', 12, C["gray"], "bold"))
        o.append(txt(74, y + 25, it["date"], 12, C["slate"]))
        o.append(txt(176, y + 25, it["kind"], 13, C["ink"], "bold"))
        o.append(txt(330, y + 25, it["holder"], 13, C["slate"]))
        if it.get("amount"):
            o.append(txt(w - 150, y + 25, won(it["amount"]), 13, C["ink"], "normal", "end"))
        o.append(f'<rect x="{w-138}" y="{y+7}" width="52" height="22" rx="11" fill="{col}"/>')
        o.append(txt(w - 112, y + 22, fate, 11, "#FFFFFF", "bold", "middle"))
        if fate == "기준":
            o.append(f'<line x1="28" y1="{y+ROW-4}" x2="{w-28}" y2="{y+ROW-4}" stroke="{C["blue"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    o.append("</svg>")
    return "\n".join(o), h


def timeline(events, title, sub=None, w=1000):
    h = 150 + 74 * len(events)
    AX = 190
    o = [head(w, h), txt(28, 44, title, 20, C["ink"], "bold"), txt(28, 68, sub or "법원 문건접수·송달 내역", 12, C["gray"]),
         f'<line x1="{AX}" y1="96" x2="{AX}" y2="{h-40}" stroke="{C["line"]}" stroke-width="2"/>']
    for i, e in enumerate(events):
        y = 122 + i * 74
        col = {"위험": C["high"], "주의": C["med"], "보통": C["blue"]}[e.get("level", "보통")]
        o.append(f'<circle cx="{AX}" cy="{y}" r="7" fill="{col}" stroke="{C["bg"]}" stroke-width="3"/>')
        o.append(txt(AX - 22, y + 5, e["date"], 12, C["slate"], "normal", "end"))
        o.append(f'<rect x="{AX+22}" y="{y-24}" width="{w-AX-52}" height="56" rx="5" fill="{C["card"]}" stroke="{C["line"]}"/>')
        o.append(txt(AX + 38, y - 4, e["what"], 13, C["ink"], "bold"))
        o.append(txt(AX + 38, y + 18, e["read"], 12, C["slate"]))
    o.append("</svg>")
    return "\n".join(o), h


def waterfall(bid, steps, title, sub=None, result_label="우리 채권 배당", w=1000):
    live = [x for x in steps if x["amount"] > 0]
    h = 150 + 52 * len(live) + 70
    BARX, BARW = 300, w - 360
    o = [head(w, h), txt(28, 44, title, 20, C["ink"], "bold"), txt(28, 68, sub or f'예상 낙찰가 {won(bid)} 기준', 12, C["gray"])]
    rem, y = bid, 100
    o.append(f'<rect x="{BARX}" y="{y}" width="{BARW}" height="26" rx="4" fill="{C["blue"]}"/>')
    o.append(txt(28, y + 18, "낙찰가", 13, C["ink"], "bold"))
    o.append(txt(BARX + BARW - 12, y + 18, won(bid), 13, "#FFFFFF", "bold", "end"))
    y += 44
    for s in live:
        amt = min(s["amount"], rem)
        bw = max(2, BARW * (amt / bid if bid else 0))
        o.append(txt(28, y + 18, s["name"], 13, C["slate"]))
        o.append(f'<rect x="{BARX}" y="{y}" width="{BARW}" height="26" rx="4" fill="#E8EAEE"/>')
        o.append(f'<rect x="{BARX}" y="{y}" width="{bw:.1f}" height="26" rx="4" fill="{s.get("color", C["lblue"])}"/>')
        # 금액 라벨은 막대 밖 오른쪽 끝 — 막대와 겹치지 않게
        o.append(txt(w - 32, y + 18, "−" + won(amt), 13, C["ink"], "normal", "end"))
        rem -= amt
        y += 44
    o.append(f'<line x1="28" y1="{y-8}" x2="{w-28}" y2="{y-8}" stroke="{C["line"]}"/>')
    o.append(txt(28, y + 22, result_label, 14, C["ink"], "bold"))
    o.append(txt(w - 32, y + 22, won(rem), 16, C["green"] if rem > 0 else C["high"], "bold", "end"))
    o.append("</svg>")
    return "\n".join(o), h, rem


def scen_chart(scen, appraisal, cap, w=1000):
    """회차별 예상 낙찰가 막대 + 매입 상한 점선."""
    h = 430
    X0, BW, GAP = 140, 160, 120
    vals = [appraisal * s["rate"] for s in scen]
    mx = max(vals + [cap]) * 1.15
    sy = lambda v: 360 - 260 * v / mx
    o = [head(w, h), txt(28, 44, "회차별 예상 낙찰가 — 기준은 누적 매각 확률 50%를 처음 넘는 회차", 20, C["ink"], "bold"),
         txt(28, 68, f"점선 = 매입 상한 {won(cap)}", 12, C["gray"])]
    for i, (s, a) in enumerate(zip(scen, vals)):
        x = X0 + i * (BW + GAP)
        o.append(f'<rect x="{x}" y="{sy(a):.1f}" width="{BW}" height="{360-sy(a):.1f}" fill="{C["blue"]}" rx="3"/>')
        o.append(txt(x + BW / 2, sy(a) - 8, won(a), 12, C["ink"], "bold", "middle"))
        o.append(txt(x + BW / 2, 384, f'{s["name"]} ({int(round(s["rate"]*100))}%) · 확률 {int(round(s["prob"]*100))}%', 13, C["ink"], "bold", "middle"))
    o.append(f'<line x1="100" y1="{sy(cap):.1f}" x2="{w-40}" y2="{sy(cap):.1f}" stroke="{C["high"]}" stroke-width="2" stroke-dasharray="7 5"/>')
    o.append(f'<line x1="100" y1="360" x2="{w-40}" y2="360" stroke="{C["line"]}"/>')
    o.append("</svg>")
    return "\n".join(o), h


def render(name, svg, h):
    sp = os.path.join(OUTD, name + ".svg")
    png = os.path.join(OUTD, name + ".png")
    open(sp, "w", encoding="utf-8").write(svg)
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=png, output_width=2000)
        return
    except ImportError:
        pass
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge):
        html = os.path.join(OUTD, name + ".html")
        open(html, "w", encoding="utf-8").write(f'<html><body style="margin:0">{svg}</body></html>')
        subprocess.run([edge, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size=1000,{h}", f"--screenshot={png}", html], capture_output=True, timeout=90)
        return
    raise SystemExit("PNG 렌더 도구 없음 — pip install cairosvg 를 하거나 Windows Edge 가 있는 PC 에서 실행")


if __name__ == "__main__":
    print("글꼴:", font_guard())
    meta = M["meta"]
    tax = M["tax_property"] + M["tax_comprehensive"]
    outs = []
    outs.append(("ladder",) + rights_ladder(M["ladder"], f"권리 순위 · 인수/소멸 — {meta['case']}"))
    outs.append(("timeline",) + timeline(M["timeline"], f"문건 타임라인 — {meta['case']}", "위험 = 빨강 · 주의 = 주황"))
    steps = [dict(name="1. 집행비용", amount=M["exec_cost"]),
             dict(name="2. 최우선변제(소액임차인)", amount=M["priority"], color=C["med"]),
             dict(name="3. 당해세(재산세+종부세)", amount=tax, color=C["med"])]
    svg, h, rem = waterfall(M["bid"], steps, "배당 폭포 — 기준 회차", f"예상 낙찰가 {won(M['bid'])} 기준")
    # ★ 검산: 폭포 끝 금액 = 모델의 우리 채권 배당. 안 맞으면 도표가 아니라 원 데이터를 다시 본다.
    assert abs(rem - M["our_dividend"]) <= 1, f"폭포 검산 실패 {rem} vs {M['our_dividend']}"
    outs.append(("waterfall", svg, h))
    outs.append(("scen",) + scen_chart(M["scenarios"], M["appraisal"], M["buy_cap"]))
    for name, svg, h in outs:
        render(name, svg, h)
        print(name, h)
    json.dump({n: h for n, _, h in outs}, open(os.path.join(OUTD, "sizes.json"), "w"))
    print("폭포 검산 통과:", won(rem), "→", OUTD)
