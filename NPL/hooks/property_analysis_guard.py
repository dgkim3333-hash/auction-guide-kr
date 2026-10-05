# -*- coding: utf-8 -*-
"""물건 분석 이중 장치 — 수강생판 (강사 원본 2026-10-05)

  python property_analysis_guard.py prompt   ← UserPromptSubmit: 분석 요청이면 필수 체크리스트를 요청 옆에 주입 (1차)
  python property_analysis_guard.py stop     ← Stop: 이번 차례에 산출물을 만들었으면
                                               ① npl-analysis·auction-property-card 호출 ② verify_property.py PASS 를 확인 (2차)
미충족 → 종료 차단(exit 2). 차단 뒤에도 그대로 끝내려 하면(stop_hook_active) 내 화면에 경고(systemMessage)를 띄우고 통과시킨다.
설치: %USERPROFILE%\\.claude\\hooks\\ 에 이 파일과 verify_property.py 를 둔다(08단원 9절).
"""
import json, os, re, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

CASE_RE = re.compile(r"\d{4}\s*타경\s*\d+|\d{4}-\d{5}-\d{3}")
ASK_RE = re.compile(r"분석|물건카드|PPTX|pptx|매입할까|입찰가|검토|정밀")
DELIVERABLE_RE = re.compile(r"03_산출물[\\/][^\"']*\.pptx|_card\.js|_npl_excel\.py|NPL수익률_[^\"']*\.xlsx", re.IGNORECASE)
REQUIRED_SKILLS = ["npl-analysis", "auction-property-card"]
VERIFY = os.path.join(os.path.expanduser("~"), ".claude", "hooks", "verify_property.py")

CHECKLIST = f"""[물건 분석 필수 절차 — property_analysis_guard 1차 장치 · C:\\AI\\NPL\\CLAUDE.md ■ 두 관점 필수]
아래를 하나도 빼지 않는다. 결론이 일찍 보여도(예: 대항력 인수로 포기 확실) 생략하지 않는다.
1. 첫 동작 Skill 호출: npl-analysis → auction-property-card(용도별 residential/commercial/land/small-building 병행) → priority-payment-date-rule(임차인 있으면) → property-tax-apportionment(주택·근생 복합) → auction-bid-price → npl-svg-chart
2. 서류: 매각물건명세서·건물/토지 등기(열람일 3개월 넘으면 재열람 요청)·건축물대장·감정평가서·현황조사서·문건접수 전수(채권양수 선점 체크)
3. 두 관점: 관점 1 = 살 수 있는 채권 표(근저당·질권·LH·임차인 채권, 대부업법 §2) + 제3자 낙찰 배당 / 관점 2 = 직접 낙찰(채권 혼동·상계) + 총비용
4. 판정: 당해세(원칙 13, 갑구 숫자 천원 단위) · 최우선변제(기준일=최선순위 담보물권) · STEP 4-C 선순위 조세 X · 21개 체크리스트 · Agent 0 저항지수
5. 시세·입지: 창고(C:\\AI\\경매창고.duckdb) 실거래 사다리 + 추정 감정가(원칙 24) + 전월세 중앙값(원칙 25) · 서울 정비사업 인접 체크 · 역세권(건설 중 노선 포함, STEP 5-B) · 인근 낙찰 사례(00_시장데이터)
6. 세금 4종 개인·법인: 취득세 §19② 시가표준액 안분 · 재산세 · 종부세 2027/2028 개편안 · 출구세(시점 미지정이면 미산출) · 내 세대 보유주택 공시가격 합산(지침 🔴③) · 대출 판정(법인·규제지역 주택 0원) · ECOS 금리
7. 산출물: PPTX(결론 두 관점 나란히·세금 3장↑·도표 3종·실명 대신 A씨·201호) + 분석 엑셀(셀 수식) + NPL수익률 엑셀(npl-excel-fill-map, 템플릿 _템플릿\\NPL수익률_교육용.xlsx) + 00_물건카드.md
8. 완료 전: python "{VERIFY}" "<물건 폴더>" 실행 → 「VERIFY_PROPERTY PASS」 확인(없으면 Stop 훅이 종료를 막는다). 슬라이드는 렌더해 눈으로 확인한다."""


def lines(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                o = json.loads(ln)
                if isinstance(o, dict):
                    out.append(o)
            except json.JSONDecodeError:
                pass
    return out


def is_real_user(o):
    if o.get("type") != "user" or o.get("isMeta"):
        return False
    c = (o.get("message") or {}).get("content")
    if isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
        return False
    return True


def user_text(o):
    c = (o.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    return ""


def analyze(objs):
    """세션 전체 스킬, 이번 차례의 사용자 글·산출물 생성 여부·검증 PASS 여부"""
    all_skills, turn_skills, turn_prompt = set(), set(), ""
    built, verified = False, False
    for o in objs:
        if is_real_user(o):
            turn_skills, built, verified, turn_prompt = set(), False, False, user_text(o)
            continue
        msg = o.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                inp = c.get("input") or {}
                if c.get("name") == "Skill":
                    s = str(inp.get("skill", "")).split(":")[-1]
                    all_skills.add(s); turn_skills.add(s)
                blob = json.dumps(inp, ensure_ascii=False)
                if DELIVERABLE_RE.search(blob) and c.get("name") in ("Write", "Edit", "PowerShell", "Bash"):
                    built = True
            elif c.get("type") == "tool_result":
                rc = c.get("content")
                txt = rc if isinstance(rc, str) else json.dumps(rc, ensure_ascii=False)
                if "VERIFY_PROPERTY PASS" in txt:
                    verified = True
                elif "VERIFY_PROPERTY FAIL" in txt:
                    verified = False
    return all_skills, turn_skills, turn_prompt, built, verified


def mode_prompt(payload):
    p = payload.get("prompt", "") or ""
    if CASE_RE.search(p) and ASK_RE.search(p):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": CHECKLIST}}, ensure_ascii=False))
    sys.exit(0)


def mode_stop(payload):
    objs = lines(payload.get("transcript_path", ""))
    all_skills, turn_skills, prompt, built, verified = analyze(objs)
    analysis_turn = built or (CASE_RE.search(prompt or "") and ASK_RE.search(prompt or "") and turn_skills & set(REQUIRED_SKILLS))
    if not analysis_turn:
        sys.exit(0)
    problems = []
    miss = [s for s in REQUIRED_SKILLS if s not in all_skills]
    if miss:
        problems.append(f"필수 스킬 미호출: {', '.join(miss)} — Skill 도구로 호출하고 그 절차대로 보완하세요.")
    if built and not verified:
        problems.append(f'산출물 검증 미통과: python "{VERIFY}" "<물건 폴더>" 를 실행해 「VERIFY_PROPERTY PASS」를 받으세요. '
                        "FAIL 항목은 산출물을 보완하고, 정말 해당 없는 항목만 물건 폴더 _검증예외.md 에 「- 검사ID: 사유」로 적으세요.")
    if not problems:
        sys.exit(0)
    head = "🚨 물건 분석 이중 장치(property_analysis_guard) — 빠진 절차가 있습니다"
    if payload.get("stop_hook_active"):
        # 두 번째 종료 시도: 무한 루프를 피하되 내 화면에 반드시 보이게 한다
        print(json.dumps({"systemMessage": head + " (미보완 상태로 종료됨): " + " / ".join(problems)}, ensure_ascii=False))
        sys.exit(0)
    sys.stderr.write(head + "\n" + "\n".join(f"{i}. {p}" for i, p in enumerate(problems, 1)) + "\n")
    sys.exit(2)


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "prompt":
        mode_prompt(payload)
    elif mode == "stop":
        mode_stop(payload)
    sys.exit(0)
