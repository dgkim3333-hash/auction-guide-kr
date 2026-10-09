# -*- coding: utf-8 -*-
"""
NPL 폴더 위생 점검·정리

왜 스크립트인가:
  매번 즉석에서 짜면 판정 기준이 흔들린다. 특히 "무엇을 백업으로 볼 것인가"가
  사람마다 달라지면, 어느 날은 마스터를 백업으로 오인해 옮기는 사고가 난다.
  판정 규칙을 한 곳에 고정해두는 것이 이 스크립트의 목적이다.

  scan  : 문제만 찾아서 보고 (파일을 건드리지 않음)
  tidy  : 백업 파일을 백업 폴더로 이동 (--apply 없이는 예행연습)
  dup   : 두 폴더 트리를 대조해 한쪽에만 있는 파일을 찾음
  verify: 복사·이동 후 원본과 크기 대조

사용법:
  python hygiene.py scan   --root <폴더>
  python hygiene.py tidy   --root <폴더> [--apply]
  python hygiene.py dup    --a <폴더A> --b <폴더B>
  python hygiene.py verify --a <원본폴더> --b <복사본폴더>
"""

import argparse
import os
import re
import shutil
import sys
from collections import defaultdict

# 백업으로 판정하는 패턴. 마스터를 잘못 잡지 않도록 "확장자 앞 또는 이름 안에
# 날짜/백업 표식이 있는 경우"만 인정한다.
# 확실한 백업 — 자동 이동 대상.
# 파일명에 명시적으로 백업임을 밝힌 표식이 있는 경우만 인정한다.
BACKUP_PAT = re.compile(
    r"(\.bak(\.|_|$)|_bak(\.|_|$)|backup|백업|복사본|_old(\.|_|$)|_prev(\.|_|$))",
    re.IGNORECASE)

# 의심 중복 — 보고만 하고 자동 이동하지 않는다.
# "파일 (1).pdf" 는 중복 내려받기일 때가 많지만, 실제로 다른 문서인 경우도 있다.
# 사건별 서류는 내용이 달라도 이름이 같기 쉬워서 자동 처리하면 사고가 난다.
# 숫자 2자리로 제한하는 이유: 법령 파일 "...(20251001).rtf" 같은 것이 걸리기 때문.
SUSPECT_DUP_PAT = re.compile(r"\(\d{1,2}\)\.[A-Za-z0-9]{2,5}$")
DATE_PAT = re.compile(r"(20\d{6}|20\d{2}-\d{2}-\d{2})")
JUNK_PAT = re.compile(r"(^~\$|^\.~lock\.|\.tmp$|\.crdownload$|\.partial$|Thumbs\.db$|\.DS_Store$)")
BACKUP_DIRS = ("백업", "_backup", "backup", "_백업", "bak")

# 코드 프로젝트 내부는 손대지 않는다.
# build·dist·node_modules는 도구가 다시 만드는 폴더라 비어 있는 게 정상이고,
# .git 내부를 건드리면 저장소가 깨진다.
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "build", "dist",
             ".next", ".cache", "site-packages", ".pytest_cache", ".mypy_cache"}

# 템플릿 폴더는 비어 있는 것이 정상이다. 새 물건을 시작할 때 통째로 복사해 쓰는
# 뼈대이므로, 빈 하위 폴더를 지우면 템플릿이 망가진다.
TEMPLATE_MARKERS = ("_템플릿", "template", "_양식", "_서식")


def is_backup(name: str) -> bool:
    return bool(BACKUP_PAT.search(name)) or bool(DATE_PAT.search(name) and "전체현황" in name)


def is_junk(name: str) -> bool:
    return bool(JUNK_PAT.search(name))


def walk(root):
    for dp, dns, fs in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fs:
            yield os.path.join(dp, f)


def scan(root: str) -> dict:
    """문제만 찾는다. 파일은 건드리지 않는다."""
    loose_backups = defaultdict(list)   # 디렉터리 -> 확실한 백업 (백업폴더 밖)
    suspects = defaultdict(list)        # 디렉터리 -> 의심 중복 (자동 이동 안 함)
    junk = []
    empty_dirs = []
    naming = defaultdict(set)           # 같은 마스터의 서로 다른 명명 규칙
    long_paths = []

    for dp, dns, fs in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        base = os.path.basename(dp)
        if base in SKIP_DIRS:
            continue
        in_backup_dir = base in BACKUP_DIRS
        if not fs and not dns and not any(m in dp for m in TEMPLATE_MARKERS):
            empty_dirs.append(dp)
        for f in fs:
            p = os.path.join(dp, f)
            if is_junk(f):
                junk.append(p); continue
            if SUSPECT_DUP_PAT.search(f) and not is_backup(f):
                suspects[dp].append(f)
                continue
            if is_backup(f) and not in_backup_dir:
                loose_backups[dp].append(f)
                stem = re.split(r"[._]?(bak|backup|백업|복사본)", f, flags=re.I)[0].strip()
                m = BACKUP_PAT.search(f)
                if m:
                    naming[stem].add(m.group(0).lower())
            if len(p) > 240:
                long_paths.append(p)

    return {"loose_backups": dict(loose_backups), "suspects": dict(suspects), "junk": junk,
            "empty_dirs": empty_dirs, "naming": {k: v for k, v in naming.items() if len(v) > 1},
            "long_paths": long_paths}


def print_scan(root: str) -> None:
    r = scan(root)
    n_lb = sum(len(v) for v in r["loose_backups"].values())
    print(f"점검 대상: {root}\n")
    print(f"■ 마스터와 섞여 있는 백업 파일: {n_lb}개")
    for d, fs in sorted(r["loose_backups"].items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   {os.path.relpath(d, root)}  ({len(fs)}개)")
        for f in sorted(fs)[:5]:
            print(f"      {f}")
        if len(fs) > 5:
            print(f"      ... 외 {len(fs)-5}개")

    n_sp = sum(len(v) for v in r["suspects"].values())
    print(f"\n■ 의심 중복 (자동 이동 안 함): {n_sp}개")
    print("   '파일 (1).pdf' 형태. 중복 내려받기일 수도, 다른 문서일 수도 있어 직접 확인이 필요합니다.")
    for d, fs in sorted(r["suspects"].items(), key=lambda x: -len(x[1]))[:5]:
        print(f"   {os.path.relpath(d, root)}  ({len(fs)}개)")

    if r["naming"]:
        print(f"\n■ 명명 규칙이 뒤섞인 그룹: {len(r['naming'])}개")
        print("   같은 파일의 백업인데 규칙이 여러 개면, 나중에 어느 게 최신인지 판단이 어려워집니다.")
        for stem, kinds in list(r["naming"].items())[:5]:
            print(f"   {stem} → {', '.join(sorted(kinds))}")

    print(f"\n■ 정리 대상 잔여물: {len(r['junk'])}개")
    for p in r["junk"][:8]:
        print(f"   {os.path.relpath(p, root)}")

    print(f"\n■ 빈 폴더: {len(r['empty_dirs'])}개")
    for p in r["empty_dirs"][:8]:
        print(f"   {os.path.relpath(p, root)}")

    if r["long_paths"]:
        print(f"\n■ 경로 240자 초과 (Excel·한글이 못 여는 위험): {len(r['long_paths'])}개")
        for p in r["long_paths"][:5]:
            print(f"   [{len(p)}자] {os.path.relpath(p, root)}")

    total = n_lb + len(r["junk"]) + len(r["empty_dirs"])
    print(f"\n조치 대상 합계 {total}건" if total else "\n문제 없음")


def tidy(root: str, apply: bool = False, remove_empty: bool = False) -> None:
    """백업을 백업 폴더로 모으고 잔여물·빈 폴더를 정리한다.

    같은 이름이 이미 있으면 건너뛴다. 덮어쓰면 되돌릴 수 없기 때문이다.
    """
    r = scan(root)
    moved = skipped = removed = 0
    tag = "" if apply else "[예행] "

    for d, fs in r["loose_backups"].items():
        dest = os.path.join(d, "백업")
        for f in sorted(fs):
            src, dst = os.path.join(d, f), os.path.join(dest, f)
            if os.path.exists(dst):
                print(f"  {tag}건너뜀(중복)  {f}"); skipped += 1; continue
            print(f"  {tag}이동  {os.path.relpath(src, root)} → 백업/")
            if apply:
                os.makedirs(dest, exist_ok=True)
                shutil.move(src, dst)
            moved += 1

    for p in r["junk"]:
        print(f"  {tag}삭제  {os.path.relpath(p, root)}")
        if apply:
            try:
                os.remove(p)
            except OSError as e:
                print(f"        실패: {e}")
                continue
        removed += 1

    if not remove_empty:
        if r["empty_dirs"]:
            print(f"\n  빈 폴더 {len(r['empty_dirs'])}개는 그대로 뒀습니다. "
                  f"지우려면 --remove-empty 를 붙이세요.")
            print("  (의도적으로 비워둔 폴더일 수 있어 기본값은 보존입니다)")
        r["empty_dirs"] = []
    for p in sorted(r["empty_dirs"], key=len, reverse=True):
        print(f"  {tag}빈 폴더 제거  {os.path.relpath(p, root)}")
        if apply:
            try:
                os.rmdir(p)
            except OSError:
                continue
        removed += 1

    print(f"\n{tag}이동 {moved} / 건너뜀 {skipped} / 삭제 {removed}")
    if not apply:
        print("실제로 적용하려면 --apply 를 붙여 다시 실행하세요.")


def _rel_map(root):
    return {os.path.relpath(p, root): os.path.getsize(p) for p in walk(root)}


def dup(a: str, b: str) -> None:
    """두 트리 대조. 경로 기준이 원칙이고, 이름+크기는 보조 판정이다.

    이름만으로 판단하면 '등기.pdf' 처럼 사건마다 내용이 다른 범용 파일명에서
    실제로 다른 문서를 같은 것으로 오인한다. 실측에서 이 실수로 79개가 누락됐다.
    """
    ra, rb = _rel_map(a), _rel_map(b)
    sig_b = {(os.path.basename(k), v) for k, v in rb.items()}
    only_a = [k for k in ra if k not in rb]
    missing = [k for k in only_a if (os.path.basename(k), ra[k]) not in sig_b]
    mismatch = [k for k in ra if k in rb and ra[k] != rb[k]]

    print(f"A: {a}  ({len(ra)}개)")
    print(f"B: {b}  ({len(rb)}개)\n")
    print(f"■ A에만 있는 경로: {len(only_a)}개")
    print(f"   → 같은 내용이 B의 다른 위치에 있음: {len(only_a)-len(missing)}개 (안전)")
    print(f"   → B 어디에도 없음: {len(missing)}개  ← 유실 위험")
    for k in sorted(missing)[:25]:
        print(f"      {k}")
    if len(missing) > 25:
        print(f"      ... 외 {len(missing)-25}개")
    print(f"\n■ 같은 경로인데 크기 다름: {len(mismatch)}개")
    for k in sorted(mismatch)[:15]:
        import datetime
        ta = os.path.getmtime(os.path.join(a, k)); tb = os.path.getmtime(os.path.join(b, k))
        win = "A" if ta > tb else "B"
        d = lambda t: datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d")
        print(f"   [{win}최신] {k}")
        print(f"       A {ra[k]:>10,} / {d(ta)}    B {rb[k]:>10,} / {d(tb)}")


def verify(a: str, b: str) -> None:
    """복사·이동 후 무결성 확인. 클라우드 동기화 중에는 잘린 복사가 실제로 발생한다."""
    ra, rb = _rel_map(a), _rel_map(b)
    bad = [(k, ra[k], rb.get(k)) for k in ra if k in rb and ra[k] != rb[k]]
    miss = [k for k in ra if k not in rb]
    for k, sa, sb in bad:
        print(f"  크기 불일치  {sa:,} → {sb:,}   {k}")
    for k in miss[:20]:
        print(f"  누락  {k}")
    print(f"\n검증: 일치 {len(ra)-len(bad)-len(miss)} / 불일치 {len(bad)} / 누락 {len(miss)}")
    if bad:
        print("불일치 파일은 다시 복사하세요. 클라우드 파일은 첫 복사가 잘리는 경우가 있습니다.")


def main():
    ap = argparse.ArgumentParser()
    s = ap.add_subparsers(dest="cmd", required=True)
    for c in ("scan", "tidy"):
        p = s.add_parser(c); p.add_argument("--root", required=True)
        if c == "tidy":
            p.add_argument("--apply", action="store_true")
            p.add_argument("--remove-empty", action="store_true")
    for c in ("dup", "verify"):
        p = s.add_parser(c); p.add_argument("--a", required=True); p.add_argument("--b", required=True)
    a = ap.parse_args()
    if a.cmd == "scan":   print_scan(a.root)
    elif a.cmd == "tidy": tidy(a.root, a.apply, a.remove_empty)
    elif a.cmd == "dup":  dup(a.a, a.b)
    elif a.cmd == "verify": verify(a.a, a.b)


if __name__ == "__main__":
    main()
