# -*- coding: utf-8 -*-
"""
물건 폴더 서류 분류·표준 파일명 제안

표준 구조(_템플릿/물건폴더_표준)에 맞춰 파일을 분류한다.
  00_물건카드.md
  01_원본서류/   등기·대장·감정평가서·명세서 등 원본 PDF
  02_분석/       수익률 엑셀, 시세 조사, 분석 노트
  03_산출물/     브리핑 PPTX, 의향서, 신청서 등 대외 산출물

기본은 예행연습이다. --apply 를 붙여야 실제로 옮긴다.
확신이 서지 않는 파일은 옮기지 않고 '미분류'로 보고한다.
잘못 옮기는 것보다 그대로 두는 편이 낫기 때문이다.

사용법:
  python intake.py plan  --folder <물건폴더>
  python intake.py plan  --folder <물건폴더> --apply
  python intake.py init  --folder <새폴더> --template <템플릿경로>
"""

import argparse
import os
import re
import shutil
import sys

# (표준번호, 표준명, 매칭 정규식)  — 위에서부터 먼저 매칭된다.
# 오타 변형(건출물대장·사곤내역·물건송달)은 실제 폴더에서 관찰된 것들이다.
RULES_ORIGINAL = [
    ("01", "등기부_건물",      r"건물\s*등기|등기\s*건물|건물등기부"),
    ("02", "등기부_토지",      r"토지\s*등기|등기\s*토지|토지등기부"),
    ("03", "등기부_집합",      r"집합\s*건물\s*등기|구분\s*등기"),
    ("19", "법인등기",         r"법인\s*등기|법인등기부"),
    ("04", "등기부",           r"등기사항|등기부|교합등기부|등기"),
    ("05", "건축물대장",       r"건축물\s*대장|건출물\s*대장|건축물관리대장"),
    ("06", "감정평가서",       r"감정\s*평가서|감정서"),
    ("07", "매각물건명세서",   r"매각물건명세서|물건\s*명세서|공매재산\s*명세서|명세서"),
    ("08", "현황조사서",       r"현황\s*조사서|현황\s*조사보고서|현황\s*보고서"),
    ("09", "문건접수내역",     r"문건\s*접수|문건\s*송달|물건\s*접수|물건\s*송달"),
    ("10", "당사자내역",       r"당사자\s*내역"),
    ("11", "사건내역",         r"사건\s*내역|사곤\s*내역|대법원\s*사건검색"),
    ("12", "전입세대열람",     r"전입\s*세대"),
    ("13", "토지이용계획",     r"토지\s*이용\s*계획|토지이음"),
    ("14", "경매정보",         r"경매\s*정보|경매지|공매\s*정보|공매공고|입찰\s*공고"),
    ("15", "채권매각공고",     r"채권\s*매각\s*공고|채권매각\s*명세|매각\s*제안서"),
    ("16", "공시가격",         r"공시\s*가격|공시지가|기준시가"),
    ("17", "임대차현황",       r"임대차\s*현황|임차\s*현황|임대\s*사항|임차\s*관리"),
    ("18", "배당요구",         r"배당\s*요구|교부\s*청구"),
]

RULES_ANALYSIS = [
    (None, None, r"NPL\s*수익률|수익률\s*분석|수익률분석"),
    (None, None, r"실거래가|시세\s*검증|시세\s*조사|온비드\s*조회"),
    (None, None, r"취득세|양도세|세금\s*계산|배당\s*표|배당표"),
    (None, None, r"분석\s*노트|검토\s*메모"),
]

RULES_OUTPUT = [
    (None, None, r"의향서|매수의향서|매각참가"),
    (None, None, r"신청서|소장|내용증명|합의서|위임장"),
    (None, None, r"보고서|리포트|브리핑|투자분석|경매분석|분석\s*보고"),
    (None, None, r"입찰\s*분석|공매\s*분석|매입\s*분석|인쇄용"),
]

ORIGINAL_EXT = {".pdf", ".hwp", ".hwpx", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}
ANALYSIS_EXT = {".xlsx", ".xls", ".csv", ".md", ".html", ".htm"}
OUTPUT_EXT = {".pptx", ".ppt", ".docx", ".doc"}

DIRS = {"원본": "01_원본서류", "분석": "02_분석", "산출물": "03_산출물"}
SKIP_NAMES = {"00_물건카드.md", "README_사용법.md"}
UNIT_PAT = re.compile(r"(\d{3,4})\s*호")


def classify(name: str):
    """(대분류, 표준파일명 또는 None, 판정근거) 반환. 확신 없으면 (None, None, 사유)."""
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if name in SKIP_NAMES or name.startswith("~$") or name.startswith(".~lock"):
        return None, None, "건너뜀"

    # 원본서류 규칙은 PDF·HWP·이미지에만 적용한다.
    # "공시지가 기준시가 임차보증금 임차권등기.xlsx" 같은 분석 파일이
    # 이름에 '등기'가 들어갔다는 이유로 원본서류로 가는 사고를 막는다.
    for num, std, pat in (RULES_ORIGINAL if ext in ORIGINAL_EXT else []):
        if re.search(pat, stem, re.IGNORECASE):
            unit = UNIT_PAT.search(stem)
            suffix = f"_{unit.group(1)}호" if unit else ""
            return "원본", f"{num}_{std}{suffix}{ext}", f"서류명 '{std}' 매칭"

    for _, _, pat in RULES_ANALYSIS:
        if re.search(pat, stem, re.IGNORECASE):
            return "분석", None, "분석 자료 패턴"

    for _, _, pat in RULES_OUTPUT:
        if re.search(pat, stem, re.IGNORECASE):
            return "산출물", None, "산출물 패턴"

    # 이름으로 못 잡으면 확장자로 추정하되, 표준 파일명은 붙이지 않는다.
    if ext in ANALYSIS_EXT:
        return "분석", None, "확장자 추정"
    if ext in OUTPUT_EXT:
        return "산출물", None, "확장자 추정"
    if ext in ORIGINAL_EXT:
        return None, None, "원본 서류로 보이나 종류 불명"
    return None, None, "분류 불가"


def plan(folder: str, apply: bool = False) -> None:
    if not os.path.isdir(folder):
        sys.exit(f"[오류] 폴더 없음: {folder}")
    items = []
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        if os.path.isdir(p):
            continue
        cat, std, why = classify(f)
        items.append((f, cat, std, why))

    moves = [x for x in items if x[1]]
    unknown = [x for x in items if not x[1] and x[3] != "건너뜀"]
    tag = "" if apply else "[예행] "

    print(f"대상 폴더: {folder}")
    print(f"파일 {len(items)}개  |  분류 {len(moves)}개  |  미분류 {len(unknown)}개\n")

    if moves:
        print(f"■ 이동 계획")
        for f, cat, std, why in moves:
            dest = DIRS[cat]
            new = std or f
            arrow = f"{dest}/{new}"
            mark = "  (이름변경)" if std and std != f else ""
            print(f"  {tag}{f}")
            print(f"       → {arrow}{mark}    [{why}]")

    if unknown:
        print(f"\n■ 미분류 — 옮기지 않음")
        print("   종류를 특정하지 못했습니다. 잘못 옮기는 것보다 두는 편이 안전합니다.")
        for f, _, _, why in unknown:
            print(f"   {f}    [{why}]")

    if not apply:
        print(f"\n실제로 적용하려면 --apply 를 붙여 다시 실행하세요.")
        return

    done = skipped = 0
    for f, cat, std, why in moves:
        dest_dir = os.path.join(folder, DIRS[cat])
        os.makedirs(dest_dir, exist_ok=True)
        target = os.path.join(dest_dir, std or f)
        if os.path.exists(target):
            base, ext = os.path.splitext(target)
            n = 2
            while os.path.exists(f"{base}_{n}{ext}"):
                n += 1
            target = f"{base}_{n}{ext}"
            print(f"  이름충돌 → {os.path.basename(target)}")
        shutil.move(os.path.join(folder, f), target)
        done += 1
    print(f"\n이동 {done}개 / 미분류 {len(unknown)}개 보존")


def init(folder: str, template: str) -> None:
    if os.path.exists(folder):
        sys.exit(f"[오류] 이미 존재: {folder}")
    shutil.copytree(template, folder)
    for sub in DIRS.values():
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    rd = os.path.join(folder, "README_사용법.md")
    if os.path.exists(rd):
        os.remove(rd)
    print(f"[생성] {folder}")
    print("  00_물건카드.md 부터 채우세요.")


def main():
    ap = argparse.ArgumentParser()
    s = ap.add_subparsers(dest="cmd", required=True)
    p1 = s.add_parser("plan"); p1.add_argument("--folder", required=True)
    p1.add_argument("--apply", action="store_true")
    p2 = s.add_parser("init"); p2.add_argument("--folder", required=True)
    p2.add_argument("--template", required=True)
    a = ap.parse_args()
    if a.cmd == "plan": plan(a.folder, a.apply)
    else: init(a.folder, a.template)


if __name__ == "__main__":
    main()
