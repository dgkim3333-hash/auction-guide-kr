#!/usr/bin/env python3
"""
경매 낙찰 후 명도 절차 D+N 마일스톤 자동 계산기

사용법:
    python calculate_milestones.py --auction-date 2026-01-15
    python calculate_milestones.py --auction-date 2026-01-15 --output milestones.json

낙찰일(매각결정기일)을 D+0으로 정의하고 명도 절차의 키 마일스톤을 계산한다.
주말/공휴일 보정은 하지 않는다(법정 기한은 자연일 기준이 다수).
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta


# 마일스톤 정의: (이름, D+N일수, 근거, 카테고리)
# 일수 None은 동적 계산
MILESTONES = [
    # 잔금납부 단계
    ("매각허가결정 항고기간 종료", 14, "민사집행법 §129 (1주 항고기간 + 송달기간)", "잔금"),
    ("매각대금 납부 기한 (추정)", 44, "매각허가확정 후 약 30일 내 (민사집행법 §142)", "잔금"),
    ("소유권 취득 시점", 44, "대금납부 시 (민사집행법 §135)", "잔금"),

    # 명도 1차 단계
    ("1차 내용증명 발송", 14, "협상 개시용 (실무 관행)", "명도"),
    ("부동산 인도명령 신청 (권장)", 14, "잔금납부 후 6개월 이내 (민사집행법 §136①)", "명도"),
    ("점유자 협상 시한 (분기점)", 30, "합의 가능성 판단 (실무 관행)", "명도"),

    # 명도 2차 단계
    ("인도명령 결정 송달 추정", 35, "보통 신청 후 2~4주", "명도"),
    ("인도명령 항고기간 종료", 49, "결정 송달 후 1주 + 송달기간 (민사집행법 §136⑤)", "명도"),
    ("강제집행 신청", 50, "인도명령 확정 후 즉시 가능", "명도"),
    ("1차 계고 (집행관)", 60, "강제집행 신청 후 약 2주", "명도"),
    ("강제집행 실시 (목표)", 80, "2차 계고 후 약 2주", "명도"),
    ("명도 완료 목표", 90, "실무 표준", "명도"),

    # 인도명령 신청 절대 한도
    ("인도명령 신청 절대 한도 (6개월)", 224, "잔금납부 후 6개월 (민사집행법 §136①)", "한도"),
]


def calculate(auction_date: date) -> list[dict]:
    """낙찰일 기준 마일스톤 일자 계산."""
    results = []
    payment_date = None  # 잔금납부일 추정 (D+44)

    for name, offset, basis, category in MILESTONES:
        target = auction_date + timedelta(days=offset)
        if "소유권 취득" in name:
            payment_date = target
        # 인도명령 6개월 한도는 잔금납부일 기준이지만 D+44 기준이므로 D+44+180 = D+224
        results.append({
            "milestone": name,
            "days_from_d0": offset,
            "date": target.strftime("%Y-%m-%d"),
            "weekday": ["월", "화", "수", "목", "금", "토", "일"][target.weekday()],
            "basis": basis,
            "category": category,
        })

    return results


def render_table(rows: list[dict]) -> str:
    """마크다운 테이블 형태로 출력."""
    lines = [
        "| D+N | 일자 | 요일 | 마일스톤 | 카테고리 | 근거 |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| D+{r['days_from_d0']} | {r['date']} | {r['weekday']} | "
            f"{r['milestone']} | {r['category']} | {r['basis']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="명도 절차 D+N 마일스톤 계산기")
    parser.add_argument(
        "--auction-date",
        required=True,
        help="낙찰일 (YYYY-MM-DD). 매각결정기일 또는 매각허가결정일을 D+0으로 사용.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="JSON 출력 경로. 미지정시 stdout으로 마크다운 출력.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="출력 형식 (기본: markdown)",
    )
    args = parser.parse_args()

    try:
        d0 = datetime.strptime(args.auction_date, "%Y-%m-%d").date()
    except ValueError:
        print(f"❌ 날짜 형식 오류: {args.auction_date} (YYYY-MM-DD 필요)", file=sys.stderr)
        sys.exit(1)

    rows = calculate(d0)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "auction_date": d0.strftime("%Y-%m-%d"),
                    "milestones": rows,
                    "note": "법정 기한은 자연일 기준 계산. 공휴일 만료 시 익일 적용 등은 별도 검토.",
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"✅ {args.output}에 저장됨 ({len(rows)}건)")
    elif args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(f"# 명도 절차 마일스톤 (낙찰일 D+0 = {d0})\n")
        print(render_table(rows))
        print("\n> ⚠️ 법정 기한은 자연일 기준입니다. 공휴일 만료, 송달 지연, 항고 발생 시 변동됩니다.")
        print("> ⚠️ 인지액·송달료는 매년 변동되므로 대법원 전자소송에서 최신 기준 확인 필요.")


if __name__ == "__main__":
    main()
