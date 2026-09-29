#!/usr/bin/env python3
"""
명도 절차 체크리스트(Markdown) 생성기

낙찰일·사건번호·시나리오·물건정보를 받아 단계별 체크리스트 MD 파일을 생성한다.
사용자가 진행 상황을 기록하고 다음 액션을 추적하는 용도.

사용법:
    python build_checklist_md.py \
      --case-no 2024타경12345 \
      --auction-date 2026-01-15 \
      --scenario A \
      --court "서울중앙지방법원" \
      --output 체크리스트.md
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from calculate_milestones import calculate as calc_milestones  # noqa: E402

SCENARIO_INFO = {
    "A": {
        "name": "일반 채무자/소유자 점유",
        "summary": "매각물건명세서에 임차인 없음. 채무자 본인 점유. 인도명령 → 강제집행으로 진행.",
        "docs": ["부동산인도명령신청서", "내용증명(1차 명도 요청)", "강제집행신청서"],
        "warning": "표준 절차. 점유자가 즉시항고 시 항고심 대응 필요.",
    },
    "B": {
        "name": "명도합의 우선",
        "summary": "점유자가 협조적. 이사비·이사기한 협의로 자진 이주 유도. 강제집행보다 비용·시간 유리.",
        "docs": ["명도합의서", "이사비 영수증", "(보험) 인도명령신청서"],
        "warning": "합의 결렬 대비 인도명령 미리 신청 권장. 합의서는 공증으로 집행권원 효력 부여.",
    },
    "C": {
        "name": "대항력 있는 임차인",
        "summary": "전입+점유가 최선순위 근저당보다 빠름. 보증금 인수 부담. 인도명령 불가, 명도소송으로만 가능.",
        "docs": ["임대차 검토 메모", "건물명도소송 소장", "부당이득반환청구 소장"],
        "warning": "⚠️ 보증금 인수가 입찰가에 미반영 시 수익률 음전환 위험. 변호사 검토 필수. 명도소송 6개월~1년 소요.",
    },
    "D": {
        "name": "배당받은 임차인",
        "summary": "임차인이 배당요구 후 보증금 전액 또는 일부 배당받음. 배당과 동시에 인도 의무 발생.",
        "docs": ["부동산인도명령신청서(배당 명시)", "내용증명", "강제집행신청서"],
        "warning": "배당표 사본 첨부 필수. 미배당 잔여 보증금 있으면 시나리오 C 일부 적용.",
    },
    "E": {
        "name": "유치권 주장",
        "summary": "매각물건명세서에 유치권 신고. 진위 판정 → 부존재확인소송 또는 협상.",
        "docs": ["유치권 진위 조사 메모", "유치권 부존재확인 소장", "(승소 후) 인도명령신청서"],
        "warning": "⚠️ 유치권은 인수주의. 패소 시 채권액 추가 부담. 변호사 선임 필수. 부존재확인 소송 8~18개월.",
    },
}


def build(case_no: str, auction_date: str, scenario: str, court: str,
          property_addr: str = "", occupant_name: str = "") -> str:
    d0 = datetime.strptime(auction_date, "%Y-%m-%d").date()
    info = SCENARIO_INFO[scenario]
    milestones = calc_milestones(d0)

    lines = [
        f"# 명도 절차 체크리스트 — {case_no}",
        "",
        "## 사건 정보",
        "",
        f"- **사건번호**: {case_no}",
        f"- **관할법원**: {court}",
        f"- **낙찰일 (D+0)**: {auction_date}",
        f"- **물건 소재지**: {property_addr or '_____'}",
        f"- **점유자**: {occupant_name or '_____'}",
        f"- **점유자 시나리오**: **{scenario} - {info['name']}**",
        "",
        "## 시나리오 요약",
        "",
        f"> {info['summary']}",
        "",
        f"⚠️ **주의사항**: {info['warning']}",
        "",
        "---",
        "",
        "## 핵심 마일스톤",
        "",
        "| D+N | 일자 | 마일스톤 | 상태 | 메모 |",
        "|---|---|---|---|---|",
    ]
    for m in milestones:
        lines.append(
            f"| D+{m['days_from_d0']} | {m['date']} ({m['weekday']}) | "
            f"{m['milestone']} | ☐ 대기 | |"
        )

    lines.extend([
        "",
        "> 상태 칸은 ☐(대기) → ▶(진행 중) → ✅(완료) 순으로 갱신",
        "",
        "---",
        "",
        "## Stage 1 — 사건정보 수집 (D+0 ~ D+7)",
        "",
        "- [ ] 매각허가결정 정본 수령",
        "- [ ] 매각대금완납증명 발급 (잔금납부 후)",
        "- [ ] 부동산등기부등본 신규 발급",
        "- [ ] 매각물건명세서 사본 확보",
        "- [ ] 현황조사보고서 사본 확보",
        "- [ ] 감정평가서 사본 확보 (월세 상당액 산정용)",
        "- [ ] 점유자 정보 확정 (실거주 주소 포함)",
        "- [ ] 임대차 정보 확인 (해당 시)",
        "",
        "## Stage 2 — 점유자 시나리오 판정",
        "",
        f"☑ 판정 결과: **{scenario} - {info['name']}**",
        "",
        "판정 근거 (사용자 메모):",
        "```",
        "_____",
        "```",
        "",
        "## Stage 3 — 잔금납부 (D+14 ~ D+44)",
        "",
        "- [ ] `post-auction-loan-simulator` 스킬로 잔금조달 시나리오 확정",
        "- [ ] 매각대금 완납",
        "- [ ] `real-estate-tax-calculator` 스킬로 취득세 계산",
        "- [ ] 취득세 신고·납부 (60일 이내)",
        "- [ ] 소유권이전등기 촉탁 신청",
        "",
        "## Stage 4 — 1차 문서 생성·발송 (D+7 ~ D+14)",
        "",
    ])

    for doc in info["docs"]:
        lines.append(f"- [ ] **{doc}** 작성 완료")
        lines.append(f"  - 작성일: _____")
        lines.append(f"  - 발송/제출일: _____")
        lines.append(f"  - 송달증명/접수증: _____")

    # 시나리오별 추가 액션
    if scenario == "A":
        lines.extend([
            "",
            "### 시나리오 A 추가 액션",
            "- [ ] 점유자 직접 방문 또는 통화 시도 (협상 가능성 타진)",
            "- [ ] 인도명령 결정 송달 확인 (D+30 전후)",
            "- [ ] 즉시항고 여부 확인 (송달 후 1주)",
        ])
    elif scenario == "B":
        lines.extend([
            "",
            "### 시나리오 B 추가 액션",
            "- [ ] 1차 협상 미팅 일정 확정",
            "- [ ] 이사비 범위 사전 결정 (예: 50만 ~ 500만원)",
            "- [ ] 합의서 공증사무소 예약",
            "- [ ] 이사비 선지급 (합의 시)",
            "- [ ] 이주 완료 확인 + 잔액 지급 + 열쇠 인수",
            "- [ ] 합의 결렬 대비 인도명령 병행 신청",
        ])
    elif scenario == "C":
        lines.extend([
            "",
            "### 시나리오 C 추가 액션",
            "- [ ] **변호사·법무사 사전 검토 (필수)**",
            "- [ ] 보증금 인수액 최종 확정",
            "- [ ] 임대차 승계 vs 명도소송 의사결정",
            "- [ ] (소송 시) 소가 산정 → 인지액·송달료 납부",
            "- [ ] 1차 변론기일 출석 준비",
            "- [ ] 합의 가능성 지속 검토",
        ])
    elif scenario == "D":
        lines.extend([
            "",
            "### 시나리오 D 추가 액션",
            "- [ ] 배당기일 종료 확인",
            "- [ ] 배당표 사본 확보 (인도명령 첨부용)",
            "- [ ] 임차인의 배당금 수령 사실 확인",
            "- [ ] 미배당 잔여 보증금 확인 (있으면 시나리오 C 일부 적용)",
        ])
    elif scenario == "E":
        lines.extend([
            "",
            "### 시나리오 E 추가 액션",
            "- [ ] **변호사 선임 (필수)**",
            "- [ ] 점유 시작 시점 입증자료 수집 (CCTV, 전기·수도 명의)",
            "- [ ] 채권 발생 시점·견련성 조사",
            "- [ ] 유치권 신고자와 채무자 관계 조사",
            "- [ ] 점유이전금지 가처분 신청 검토",
            "- [ ] 진성 유치권 가능성 시 협상 채널 확보",
        ])

    lines.extend([
        "",
        "## Stage 5 — 점유자 대응 (D+14 ~ D+60)",
        "",
        "- [ ] 1차 내용증명 도달 후 점유자 반응 기록",
        "- [ ] 협상 vs 강제집행 의사결정 (D+30 분기점)",
        "- [ ] 모든 커뮤니케이션 XLSX 일정관리 시트에 기록",
        "",
        "## Stage 6 — 2차 문서 생성·집행 (D+30 ~ D+90)",
        "",
        "- [ ] 강제집행 또는 추가 소송 문서 작성",
        "- [ ] 집행관 사무소 방문 (강제집행 시)",
        "- [ ] 예납금 납부 (200만 ~ 500만원 추정)",
        "- [ ] 1차 계고 → 2차 계고 → 강제집행 입회",
        "- [ ] 노무비·이삿짐 보관료 정산",
        "",
        "## Stage 7 — 명도 완료 후 (D+90 이후)",
        "",
        "- [ ] 부동산 인수 + 시설물 점검",
        "- [ ] 부당이득반환청구 진행 여부 결정",
        "- [ ] 임대차 계약 또는 매각 출구전략 (별도 워크플로우)",
        "- [ ] 비용 정산 (XLSX 비용트래커 시트)",
        "",
        "---",
        "",
        "## 산출 파일 인덱스",
        "",
        f"- 일정관리: `{case_no}_명도일정관리.xlsx`",
        f"- 문서 패키지: `{case_no}_명도문서패키지/`",
        f"- 본 체크리스트: `{case_no}_명도체크리스트.md`",
        "",
        "## 외부 출처 확인 권장",
        "",
        "[검증필요] 다음 사항은 공식 출처 확인 후 사용:",
        "",
        "1. 인도명령 신청기한·인지액·송달료 → 대법원 전자소송 (ecfs.scourt.go.kr)",
        "2. 민사집행법 조항 → 국가법령정보센터 (law.go.kr)",
        "3. 명도 관련 최신 판례 → 대법원 종합법률정보 (glaw.scourt.go.kr)",
        "4. 강제집행 예납금 견적 → 관할 집행관 사무소",
        "",
        "## 다른 스킬과의 연계",
        "",
        "- **잔금조달**: `post-auction-loan-simulator` 스킬",
        "- **세금 계산**: `real-estate-tax-calculator` 스킬",
        "- **법령·판례 검색**: `korea-law-search` MCP",
        "- **사건 조회**: `court-auction` MCP",
        "",
        "---",
        "",
        f"*생성일: {datetime.now().strftime('%Y-%m-%d')}*",
        "*본 체크리스트는 `post-auction-eviction` 스킬에 의해 자동 생성되었습니다.*",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="명도 절차 체크리스트 MD 생성기")
    parser.add_argument("--case-no", required=True)
    parser.add_argument("--auction-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--scenario", required=True, choices=list(SCENARIO_INFO.keys()))
    parser.add_argument("--court", required=True)
    parser.add_argument("--property-addr", default="")
    parser.add_argument("--occupant-name", default="")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    md = build(
        args.case_no, args.auction_date, args.scenario, args.court,
        args.property_addr, args.occupant_name,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"✅ 생성 완료: {out}")


if __name__ == "__main__":
    main()
