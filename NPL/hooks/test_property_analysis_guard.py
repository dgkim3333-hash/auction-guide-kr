# -*- coding: utf-8 -*-
# property_analysis_guard 변이 시험 — 막아야 할 때 막고, 통과시킬 때 통과시키는지
import json, os, subprocess, sys, tempfile

G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "property_analysis_guard.py")


def run(mode, payload):
    r = subprocess.run([sys.executable, G, mode], input=json.dumps(payload, ensure_ascii=False).encode("utf-8"), capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def tr(events):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    f.close()
    return f.name


U = lambda t: {"type": "user", "message": {"role": "user", "content": t}}
SK = lambda s: {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Skill", "input": {"skill": s}}]}}
BUILD = {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "PowerShell", "input": {"command": "node _card.js model.json 03_산출물\\물건카드_2025타경1.pptx"}}]}}
RES = lambda t: {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": t}]}}

cases = []
# 1차: 요청 감지
rc, out, _ = run("prompt", {"prompt": "2025타경12345 이 물건 분석해줘"}); cases.append(("prompt 감지 → 체크리스트 주입", rc == 0 and "필수 절차" in out))
rc, out, _ = run("prompt", {"prompt": "오늘 날씨 어때"}); cases.append(("prompt 무관 → 주입 없음", rc == 0 and out.strip() == ""))
# 2차: 종료 검사
base = [U("2025타경12345 분석해줘"), SK("anthropic-skills:npl-analysis"), SK("anthropic-skills:auction-property-card"), BUILD]
rc, _, err = run("stop", {"transcript_path": tr(base)}); cases.append(("산출물 생성 + 검증 없음 → 차단", rc == 2 and "검증 미통과" in err))
rc, _, _ = run("stop", {"transcript_path": tr(base + [RES("...\nVERIFY_PROPERTY PASS")])}); cases.append(("검증 PASS → 통과", rc == 0))
rc, _, _ = run("stop", {"transcript_path": tr(base + [RES("VERIFY_PROPERTY FAIL")])}); cases.append(("검증 FAIL → 차단", rc == 2))
noskill = [U("2025타경12345 분석해줘"), SK("anthropic-skills:npl-analysis"), BUILD, RES("VERIFY_PROPERTY PASS")]
rc, _, err = run("stop", {"transcript_path": tr(noskill)}); cases.append(("auction-property-card 미호출 → 차단", rc == 2 and "auction-property-card" in err))
rc, out, _ = run("stop", {"transcript_path": tr(base), "stop_hook_active": True}); cases.append(("두 번째 종료 → 화면 경고 후 통과", rc == 0 and "systemMessage" in out))
rc, _, _ = run("stop", {"transcript_path": tr([U("종부세 개편안 설명해줘")])}); cases.append(("분석 아닌 차례 → 통과", rc == 0))

ok = all(c[1] for c in cases)
for n, r in cases:
    print(("PASS " if r else "FAIL ") + n)
print("ALL PASS" if ok else "SOME FAIL")
sys.exit(0 if ok else 1)
