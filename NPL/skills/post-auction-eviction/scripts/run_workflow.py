#!/usr/bin/env python3
"""
명도 절차 통합 워크플로우 — MD 체크리스트 + XLSX 일정관리 + DOCX 문서패키지 일괄 생성

사용법:
    python run_workflow.py --params params.json --output-dir /mnt/user-data/outputs/

params.json은 사건 정보 + 당사자 + 시나리오 + 물건정보를 모두 포함한다.
샘플은 assets/sample_params.json 참조.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="명도 절차 통합 워크플로우")
    parser.add_argument("--params", required=True, help="사건 정보 JSON 파일")
    parser.add_argument("--output-dir", required=True, help="산출물 출력 디렉토리")
    args = parser.parse_args()

    with open(args.params, "r", encoding="utf-8") as f:
        params = json.load(f)

    # 필수 필드 검증
    required = ["case_no", "auction_date", "scenario", "court_name",
                "applicant_name", "occupant_name"]
    missing = [k for k in required if k not in params]
    if missing:
        print(f"❌ 필수 필드 누락: {missing}", file=sys.stderr)
        sys.exit(1)

    case_no = params["case_no"]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    script_dir = Path(__file__).parent

    # 1. 체크리스트 MD
    md_path = output_dir / f"{case_no}_명도체크리스트.md"
    subprocess.run([
        sys.executable, str(script_dir / "build_checklist_md.py"),
        "--case-no", case_no,
        "--auction-date", params["auction_date"],
        "--scenario", params["scenario"],
        "--court", params["court_name"],
        "--property-addr", params.get("property_short_addr", params.get("property_description", "")),
        "--occupant-name", params["occupant_name"],
        "--output", str(md_path),
    ], check=True)

    # 2. XLSX 일정관리
    xlsx_path = output_dir / f"{case_no}_명도일정관리.xlsx"
    subprocess.run([
        sys.executable, str(script_dir / "build_schedule_xlsx.py"),
        "--case-no", case_no,
        "--auction-date", params["auction_date"],
        "--scenario", params["scenario"],
        "--output", str(xlsx_path),
    ], check=True)

    # 3. DOCX 문서패키지
    docs_dir = output_dir / f"{case_no}_명도문서패키지"
    subprocess.run([
        sys.executable, str(script_dir / "generate_documents.py"),
        "--scenario", params["scenario"],
        "--params", args.params,
        "--output-dir", str(docs_dir),
    ], check=True)

    print(f"\n{'='*60}")
    print("✅ 모든 산출물 생성 완료")
    print(f"{'='*60}")
    print(f"  📋 체크리스트: {md_path}")
    print(f"  📊 일정관리: {xlsx_path}")
    print(f"  📁 문서패키지: {docs_dir}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
