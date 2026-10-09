# -*- coding: utf-8 -*-
"""물건 분석 이중 장치 — 수강생판 (강사 원본 2026-10-05 · 목록 1·3·4·7번 2026-10-07 · 7번 덱 표준 2026-10-08 · 1·2·7번 임차인·당해세 스킬 2026-10-09)

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
# 「산출물을 만들었다」 판정 (2026-10-05 오탐 수정 — 읽기용 스크립트 본문에 경로 문자열만 있어도 막히던 문제)
DELIVERABLE_PATH_RE = re.compile(r"(03_산출물[\\/][^\\/]*\.pptx|물건카드_[^\\/]*\.pptx|_card\.js|_npl_excel\.py|NPL수익률_[^\\/]*\.xlsx)$", re.IGNORECASE)
SHELL_BUILD_RE = re.compile(r"\bnode\b[^\n|;&]*_card\.js|\bpython[^\n|;&]*_npl_excel\.py"
                            r"|\b(Copy-Item|Move-Item|cp|mv|copy|move)\b[^\n|;&]*(물건카드_[^\"'\s]*\.pptx|NPL수익률_[^\"'\s]*\.xlsx)", re.IGNORECASE)
REQUIRED_SKILLS = ["npl-analysis", "auction-property-card"]
VERIFY = os.path.join(os.path.expanduser("~"), ".claude", "hooks", "verify_property.py")

CHECKLIST = f"""[물건 분석 필수 절차 — property_analysis_guard 1차 장치 · C:\\AI\\NPL\\CLAUDE.md ■ 두 관점 필수]
아래를 하나도 빼지 않는다. 결론이 일찍 보여도(예: 대항력 인수로 포기 확실) 생략하지 않는다.
1. 첫 동작 Skill 호출: npl-analysis → auction-property-card(용도별 residential/commercial/land/small-building 병행) → priority-payment-date-rule(임차인 있으면) → property-tax-apportionment(주택·근생 복합) → auction-bid-price → npl-svg-chart → npl-cross-collateral-shortfall(토지 : 건물 비율은 항상 · 교차 담보 잉여 배분 · 배당 부족 시 잔존채권 추심 장 · 세무서 압류나 체납 전언이 있으면 선순위 국세 판정·민감도 장 · 경매개시결정 등기 전 매입이면 전입 차단 계약 조항 장) → npl-tenant-rent-check(주택 임차인이 있으면 — 다가구·다세대 기본 — 임차인 서류 대조 · 전입세대 열람 · 월세·관리비 연체 공제(투자금 회수 계산 0원) · 월세 압류 순서·당사자 · 배당이의 · 양수도계약서 대조) → npl-tax-arrears-closing(항상 — 당해 연도 재산세·종부세 미납분 각각 계산·합산 · 압류 세목 판정 · 채권 매입 건 계약일·채무자 납세증명서·잔금일·법무사 체크리스트 · 자금 계획 부록 D) → auction-failure-guard(결론 전 마지막)
2. 서류: 매각물건명세서·건물/토지 등기(열람일 3개월 넘으면 재열람 요청)·건축물대장·감정평가서·현황조사서·문건접수 전수(채권양수 선점 체크) (채권 매입 건이면 매도 금융기관의 임대차현황 · 임대차계약서 전부 · 월세·관리비 납부 내역 · 양수도계약서 초안 · 채무자 국세·지방세 납세증명서는 매도 금융기관 여신 파일의 대출 실행 당시 사본 — 채무자는 협조하지 않고 납세자 본인만 새로 발급받을 수 있다)
3. 두 관점: 관점 1 = 살 수 있는 채권 표(근저당·질권·LH·임차인 채권, 대부업법 §2) + 제3자 낙찰 배당 + 손익은 무차입 값과 질권대출 이자·설정비를 뺀 값 두 가지 / 관점 2 = 직접 낙찰(채권 혼동·상계) + 총비용
4. 판정: 당해세(원칙 13, 갑구 숫자 천원 단위) · 최우선변제(기준일=최선순위 담보물권) · STEP 4-C 선순위 조세 X · 21개 체크리스트 · Agent 0 저항지수 · 토지 : 건물 비율 + 등기부 을구를 토지 순위표·건물 순위표로 따로 읽어 교차 담보 여부 판정(npl-cross-collateral-shortfall A·B) · 선순위 국세(누구의 세금인지 · 당해세인지 · 법정기일이 필지·건물별 근저당 설정일보다 빠른지 — 압류 등기일로 정하지 않는다, 같은 스킬 D) · 실패위험 점검표(auction-failure-guard 11개 유형 — 관점 1 모드 B · 관점 2 모드 A, 재매각 이력이면 앞 낙찰자 실패 원인 맨 위)
5. 시세·입지: 창고(C:\\AI\\경매창고.duckdb) 실거래 사다리 + 추정 감정가(원칙 24) + 전월세 중앙값(원칙 25) · 서울 정비사업 인접 체크 · 역세권(건설 중 노선 포함, STEP 5-B) · 인근 낙찰 사례(00_시장데이터)
6. 세금 4종 개인·법인: 취득세 §19② 시가표준액 안분 · 재산세 · 종부세 2027/2028 개편안 · 출구세(시점 미지정이면 미산출) · 내 세대 보유주택 공시가격 합산(지침 🔴③) · 대출 판정(법인·규제지역 주택 0원) · ECOS 금리
7. 산출물: PPTX(모양·장 순서·생성기는 npl-deck-standard 스킬 · 결론 두 관점 나란히·세금 3장↑·도표 3종·실명 대신 A씨·201호 + 관점 2 다섯 장 = 입지(수요처·통근) · 고유 리스크(확인 방법 열) · 명도(인도명령 일정·예산) · 종합 점수(100점 배점) · 확인해야 할 것) + 배당 폭포 장 하단 토지 : 건물 비율 + (우리 채권 배당이 청구액에 못 미치면) 잔존채권 추심 장 + (세무서 압류나 체납 전언이 있으면) 국세 판정 장 · 국세 민감도 장 + 질권대출 반영 장(질권대출을 쓸 때) + (채권 매입 건이고 주택이 있으며 경매개시결정 등기 전이면) 최우선변제 민감도 장 바로 뒤 「전입 차단 — 계약 조항」 장 + 주택 임차인이 있으면 「월세 연체 공제」·「월세 — 할 일 순서」·「월세 압류 — 당사자」·「배당이의 — 용어와 순서」·「월세 연체 — 들은 내용 판정」 5장 + 「전입세대주 대조」·「개시 뒤 전입세대열람」 2장 + (채권 매입 건) 「양수도계약서 대조」(npl-tenant-rent-check) · 항상 국세 판정 장 뒤 「당해 연도 당해세 산출」(재산세·종부세 각각 + 합계)·「배당요구 종기와 당해세」 · 채권 매입 건 덱 맨 끝 「계약일 체크리스트」·「채무자 납세증명서는 새로 뗄 수 없다」·「잔금일 체크리스트(누가 열)」·「법무사 요청」 4장 + 「부록 D — 자금 계획」 4장(npl-tax-arrears-closing) + 분석 엑셀(셀 수식) + NPL수익률 엑셀(npl-excel-fill-map, 템플릿 _템플릿\\NPL수익률_교육용.xlsx · 하단 D30:D33 토지 : 건물 비율 · 교차 담보면 C16 연결 수식) + 00_물건카드.md
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
                name = c.get("name")
                if name in ("Write", "Edit") and DELIVERABLE_PATH_RE.search(str(inp.get("file_path", ""))):
                    built = True
                elif name in ("PowerShell", "Bash") and SHELL_BUILD_RE.search(str(inp.get("command", ""))):
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
