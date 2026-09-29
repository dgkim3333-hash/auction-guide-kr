"""
post-auction-loan-simulator: Excel 산출물 자동 생성 스크립트

사용법:
    python build_excel.py <input_json_path> <output_xlsx_path>

또는 직접 import 후 build_excel(params, output_path) 호출

입력 JSON 구조:
{
  "property": {
    "name": "강남구 역삼동 아파트",
    "type": "아파트",
    "address": "...",
    "case_number": "2024타경12345"
  },
  "amounts": {
    "winning_bid_10k": 100000,    // 낙찰가 (만원)
    "appraisal_10k": 120000,       // 감정가 (만원)
    "monthly_rent_10k": 400        // 월 임대료 (만원)
  },
  "borrower": {
    "type": "SPC",                  // 대부업체/SPC/개인(다주택)/개인(1주택)/법인사업자
    "market_rate_pct": 5.0          // 시장 기준금리 (%)
  },
  "loan": {
    "duration_years": 20,           // 대출 기간
    "holding_years": 3,             // 보유 기간
    "amortization": "원리금균등"
  },
  "scenarios": {                     // null이면 차주 유형 디폴트 사용
    "conservative": {"ltv": 0.50, "rate_spread": 1.5, "vacancy": 0.10, "opex": 0.20, "exit_multiple": 1.05, "exit_cost": 0.05},
    "moderate":     {"ltv": 0.60, "rate_spread": 1.0, "vacancy": 0.05, "opex": 0.15, "exit_multiple": 1.15, "exit_cost": 0.04},
    "aggressive":   {"ltv": 0.70, "rate_spread": 0.5, "vacancy": 0.02, "opex": 0.10, "exit_multiple": 1.30, "exit_cost": 0.03}
  }
}
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation


# ============================================================
# 차주 유형별 LTV·금리 디폴트 매핑
# ============================================================
BORROWER_DEFAULTS = {
    "대부업체": {
        "conservative": {"ltv": 0.40, "rate_spread": 3.0},
        "moderate":     {"ltv": 0.50, "rate_spread": 2.0},
        "aggressive":   {"ltv": 0.60, "rate_spread": 1.5},
    },
    "SPC": {
        "conservative": {"ltv": 0.50, "rate_spread": 1.5},
        "moderate":     {"ltv": 0.60, "rate_spread": 1.0},
        "aggressive":   {"ltv": 0.70, "rate_spread": 0.5},
    },
    "개인(다주택)": {
        "conservative": {"ltv": 0.30, "rate_spread": 0.5},
        "moderate":     {"ltv": 0.40, "rate_spread": 0.3},
        "aggressive":   {"ltv": 0.50, "rate_spread": 0.0},
    },
    "개인(1주택)": {
        "conservative": {"ltv": 0.50, "rate_spread": 0.3},
        "moderate":     {"ltv": 0.60, "rate_spread": 0.0},
        "aggressive":   {"ltv": 0.70, "rate_spread": -0.3},
    },
    "법인사업자": {
        "conservative": {"ltv": 0.50, "rate_spread": 1.0},
        "moderate":     {"ltv": 0.60, "rate_spread": 0.5},
        "aggressive":   {"ltv": 0.70, "rate_spread": 0.0},
    },
}

SCENARIO_DEFAULTS_NON_LTV_RATE = {
    "conservative": {"vacancy": 0.10, "opex": 0.20, "exit_multiple": 1.05, "exit_cost": 0.05},
    "moderate":     {"vacancy": 0.05, "opex": 0.15, "exit_multiple": 1.15, "exit_cost": 0.04},
    "aggressive":   {"vacancy": 0.02, "opex": 0.10, "exit_multiple": 1.30, "exit_cost": 0.03},
}

# ============================================================
# 스타일 정의
# ============================================================
FONT_HEADER = Font(name="맑은 고딕", size=14, bold=True, color="FFFFFF")
FONT_SUBHEADER = Font(name="맑은 고딕", size=12, bold=True, color="000000")
FONT_LABEL = Font(name="맑은 고딕", size=11, bold=False)
FONT_INPUT = Font(name="맑은 고딕", size=11, color="0000FF", bold=True)
FONT_FORMULA = Font(name="맑은 고딕", size=11, color="000000")
FONT_LINK = Font(name="맑은 고딕", size=11, color="008000")
FONT_WARNING = Font(name="맑은 고딕", size=11, color="FFFFFF", bold=True)

FILL_HEADER = PatternFill("solid", start_color="1F4E78")
FILL_SUBHEADER = PatternFill("solid", start_color="D9D9D9")
FILL_INPUT = PatternFill("solid", start_color="FFFF00")
FILL_WARNING = PatternFill("solid", start_color="C00000")
FILL_GOOD = PatternFill("solid", start_color="C6EFCE")
FILL_NEUTRAL = PatternFill("solid", start_color="FFEB9C")
FILL_BAD = PatternFill("solid", start_color="FFC7CE")

BORDER_THIN = Border(
    left=Side(style="thin", color="BFBFBF"),
    right=Side(style="thin", color="BFBFBF"),
    top=Side(style="thin", color="BFBFBF"),
    bottom=Side(style="thin", color="BFBFBF"),
)

ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")

NUM_FMT_KRW = '#,##0_-;(#,##0);"-"'
NUM_FMT_PCT = "0.0%"
NUM_FMT_RATE = '0.00"%"'
NUM_FMT_RATIO = "0.00"


# ============================================================
# 헬퍼 함수
# ============================================================
def merge_scenarios(user_scenarios, borrower_type):
    """사용자 시나리오 입력과 차주 디폴트를 병합"""
    base = BORROWER_DEFAULTS.get(borrower_type, BORROWER_DEFAULTS["SPC"])
    result = {}
    for key in ["conservative", "moderate", "aggressive"]:
        # LTV·금리는 차주 디폴트
        merged = {**base[key], **SCENARIO_DEFAULTS_NON_LTV_RATE[key]}
        # 사용자 입력이 있으면 덮어쓰기
        if user_scenarios and key in user_scenarios:
            merged.update(user_scenarios[key])
        result[key] = merged
    return result


def set_input_cell(ws, cell, value, fmt=None):
    """입력 셀 (파란 글씨, 노란 배경)"""
    ws[cell] = value
    ws[cell].font = FONT_INPUT
    ws[cell].fill = FILL_INPUT
    ws[cell].border = BORDER_THIN
    if fmt:
        ws[cell].number_format = fmt


def set_label_cell(ws, cell, value):
    """라벨 셀"""
    ws[cell] = value
    ws[cell].font = FONT_LABEL
    ws[cell].border = BORDER_THIN
    ws[cell].alignment = ALIGN_LEFT


def set_formula_cell(ws, cell, formula, fmt=None, link=False):
    """수식 셀"""
    ws[cell] = formula
    ws[cell].font = FONT_LINK if link else FONT_FORMULA
    ws[cell].border = BORDER_THIN
    if fmt:
        ws[cell].number_format = fmt


def set_header_row(ws, row, headers, start_col="A"):
    """헤더 행 작성"""
    start_idx = ord(start_col) - ord("A")
    for i, h in enumerate(headers):
        col = get_column_letter(start_idx + i + 1)
        cell = f"{col}{row}"
        ws[cell] = h
        ws[cell].font = FONT_HEADER
        ws[cell].fill = FILL_HEADER
        ws[cell].alignment = ALIGN_CENTER
        ws[cell].border = BORDER_THIN


def set_subheader_cell(ws, cell, value):
    """소제목 셀"""
    ws[cell] = value
    ws[cell].font = FONT_SUBHEADER
    ws[cell].fill = FILL_SUBHEADER
    ws[cell].alignment = ALIGN_LEFT
    ws[cell].border = BORDER_THIN


# ============================================================
# Sheet 1: 입력 가정값
# ============================================================
def build_sheet1_inputs(wb, params):
    ws = wb.active
    ws.title = "1.입력가정값"

    # 컬럼 폭
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 18

    # 안내문 (1~6행)
    ws["A1"] = "post-auction-loan-simulator 입력 가정값"
    ws["A1"].font = Font(name="맑은 고딕", size=16, bold=True, color="1F4E78")
    ws.merge_cells("A1:E1")

    notice = (
        "⚠️ 본 시뮬레이션의 LTV·금리 가정값은 일반적 시장 기준이며 거래 은행 직접 확인 필수. "
        "노란 배경 셀은 사용자 입력 항목이며, 값 변경 시 모든 시트가 자동 재계산됩니다."
    )
    ws["A2"] = notice
    ws["A2"].font = Font(name="맑은 고딕", size=10, color="C00000", italic=True)
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.merge_cells("A2:E2")
    ws.row_dimensions[2].height = 30

    # === 기본 정보 ===
    set_subheader_cell(ws, "A4", "[기본 정보]")
    ws.merge_cells("A4:E4")

    set_label_cell(ws, "A5", "물건명")
    set_input_cell(ws, "B5", params["property"].get("name", ""))

    set_label_cell(ws, "A6", "물건유형")
    set_input_cell(ws, "B6", params["property"].get("type", ""))

    set_label_cell(ws, "A7", "주소")
    set_input_cell(ws, "B7", params["property"].get("address", ""))
    ws.merge_cells("B7:E7")

    set_label_cell(ws, "A8", "사건번호")
    set_input_cell(ws, "B8", params["property"].get("case_number", ""))

    set_label_cell(ws, "A9", "분석일자")
    set_input_cell(ws, "B9", datetime.now().strftime("%Y-%m-%d"))

    # === 금액 정보 ===
    set_subheader_cell(ws, "A11", "[금액 정보] (단위: 만원)")
    ws.merge_cells("A11:E11")

    set_label_cell(ws, "A12", "낙찰 예상가")
    set_input_cell(ws, "B12", params["amounts"]["winning_bid_10k"], NUM_FMT_KRW)

    set_label_cell(ws, "A13", "감정가")
    set_input_cell(ws, "B13", params["amounts"]["appraisal_10k"], NUM_FMT_KRW)

    set_label_cell(ws, "A14", "월 임대료")
    set_input_cell(ws, "B14", params["amounts"]["monthly_rent_10k"], NUM_FMT_KRW)

    set_label_cell(ws, "A15", "낙찰가 / 감정가 비율")
    set_formula_cell(ws, "B15", "=B12/B13", NUM_FMT_PCT)

    # === 차주 정보 ===
    set_subheader_cell(ws, "A17", "[차주 정보]")
    ws.merge_cells("A17:E17")

    set_label_cell(ws, "A18", "명의 유형")
    set_input_cell(ws, "B18", params["borrower"]["type"])
    # 데이터 검증
    dv = DataValidation(
        type="list",
        formula1='"대부업체,SPC,개인(다주택),개인(1주택),법인사업자"',
        allow_blank=False,
    )
    ws.add_data_validation(dv)
    dv.add("B18")

    set_label_cell(ws, "A19", "시장 기준금리 (%)")
    set_input_cell(ws, "B19", params["borrower"]["market_rate_pct"], NUM_FMT_RATE)

    # === 대출 조건 ===
    set_subheader_cell(ws, "A21", "[대출 조건]")
    ws.merge_cells("A21:E21")

    set_label_cell(ws, "A22", "대출 기간 (년)")
    set_input_cell(ws, "B22", params["loan"]["duration_years"])

    set_label_cell(ws, "A23", "보유 기간 (년)")
    set_input_cell(ws, "B23", params["loan"]["holding_years"])

    set_label_cell(ws, "A24", "상환 방식")
    set_input_cell(ws, "B24", params["loan"].get("amortization", "원리금균등"))

    # === 시나리오 가정값 ===
    set_subheader_cell(ws, "A26", "[시나리오 가정값]")
    ws.merge_cells("A26:E26")

    # 헤더
    set_header_row(ws, 27, ["항목", "보수", "중립", "공격적"], "A")

    scenarios = params["_resolved_scenarios"]
    rows_data = [
        ("LTV (%)", "ltv", NUM_FMT_PCT, False),
        ("금리 가산 (%p)", "rate_spread", '0.00"%p"', False),
        ("적용 금리 (%)", None, NUM_FMT_RATE, "rate"),  # 계산 행
        ("공실률 (%)", "vacancy", NUM_FMT_PCT, False),
        ("운영비율 (%)", "opex", NUM_FMT_PCT, False),
        ("매각가 배수", "exit_multiple", NUM_FMT_RATIO, False),
        ("매각비용 비율 (%)", "exit_cost", NUM_FMT_PCT, False),
    ]

    row = 28
    for label, key, fmt, special in rows_data:
        set_label_cell(ws, f"A{row}", label)
        if special == "rate":
            # 적용금리 = 시장금리 + 가산
            set_formula_cell(ws, f"B{row}", f"=$B$19+B{row-1}", fmt)
            set_formula_cell(ws, f"C{row}", f"=$B$19+C{row-1}", fmt)
            set_formula_cell(ws, f"D{row}", f"=$B$19+D{row-1}", fmt)
        else:
            set_input_cell(ws, f"B{row}", scenarios["conservative"][key], fmt)
            set_input_cell(ws, f"C{row}", scenarios["moderate"][key], fmt)
            set_input_cell(ws, f"D{row}", scenarios["aggressive"][key], fmt)
        row += 1

    # 명명 규칙 (다른 시트에서 참조용 셀 위치)
    # B12: 낙찰가, B13: 감정가, B14: 월임대료
    # B19: 시장금리, B22: 대출기간, B23: 보유기간
    # B28-D28: LTV, B30-D30: 적용금리, B31-D31: 공실률, B32-D32: 운영비율
    # B33-D33: 매각배수, B34-D34: 매각비용

    return ws


# ============================================================
# Sheet 2: 3시나리오 비교
# ============================================================
def build_sheet2_comparison(wb):
    ws = wb.create_sheet("2.3시나리오비교")

    ws.column_dimensions["A"].width = 30
    for col in ["B", "C", "D"]:
        ws.column_dimensions[col].width = 18

    ws["A1"] = "3가지 시나리오 비교"
    ws["A1"].font = Font(name="맑은 고딕", size=16, bold=True, color="1F4E78")
    ws.merge_cells("A1:D1")

    set_header_row(ws, 3, ["항목", "보수", "중립", "공격적"], "A")

    inp = "'1.입력가정값'!"
    # 시나리오별 컬럼 매핑: 보수=B, 중립=C, 공격=D (입력시트와 동일)

    rows = []

    # 시트2 실제 행 매핑 (헤더 행=3, 데이터 시작 행=4)
    # row 4: [입력 인자] (subheader)
    # row 5: LTV
    # row 6: 적용 금리
    # row 7: 공실률
    # row 8: 운영비율
    # row 9: [자금조달] (subheader)
    # row 10: 대출 가능액
    # row 11: 자기자본
    # row 12: [월간 현금흐름] (subheader)
    # row 13: 월 임대료
    # row 14: 월 NOI (공실차감)
    # row 15: 월 실효임대수익
    # row 16: 월 원리금 (PMT)
    # row 17: 월 순현금흐름
    # row 18: [연간 지표] (subheader)
    # row 19: 연간 NOI (실효)
    # row 20: 연간 원리금
    # row 21: DSCR
    # row 22: 캐시 일드
    # row 23: [매각 시나리오] (subheader)
    # row 24: 매각 예상가
    # row 25: 매각 비용
    # row 26: 잔존 대출원금
    # row 27: 세전 매각 회수
    # row 28: [수익률 종합] (subheader)
    # row 29: 월 순현흐름 × 보유 합
    # row 30: 총 회수액
    # row 31: 총 자기자본 수익률
    # row 32: 자기자본 IRR (연환산)
    # row 33: [판정] (subheader)
    # row 34: DSCR 판정
    # row 35: IRR 판정

    # [입력 인자]
    rows.append(("[입력 인자]", "subheader", None))
    rows.append(("LTV", "link", [f"={inp}B28", f"={inp}C28", f"={inp}D28"], NUM_FMT_PCT))
    rows.append(("적용 금리", "link", [f"={inp}B30", f"={inp}C30", f"={inp}D30"], NUM_FMT_RATE))
    rows.append(("공실률", "link", [f"={inp}B31", f"={inp}C31", f"={inp}D31"], NUM_FMT_PCT))
    rows.append(("운영비율", "link", [f"={inp}B32", f"={inp}C32", f"={inp}D32"], NUM_FMT_PCT))

    # [자금조달]  (시작 row 9, 첫 데이터 row 10)
    rows.append(("[자금조달] (만원)", "subheader", None))
    # 대출가능액 = 낙찰가 × LTV  (LTV는 row 5)
    rows.append(("대출 가능액", "formula", [
        f"={inp}B12*B5", f"={inp}B12*C5", f"={inp}B12*D5"
    ], NUM_FMT_KRW))
    # 자기자본 = 낙찰가 - 대출가능액 (row 10)
    rows.append(("자기자본", "formula", [
        f"={inp}B12-B10", f"={inp}B12-C10", f"={inp}B12-D10"
    ], NUM_FMT_KRW))

    # [월간 현금흐름] (시작 row 12, 첫 데이터 row 13)
    rows.append(("[월간 현금흐름] (만원)", "subheader", None))
    rows.append(("월 임대료", "link", [f"={inp}B14", f"={inp}B14", f"={inp}B14"], NUM_FMT_KRW))
    # 월 NOI = 월임대료(row13) × (1 - 공실률(row7))
    rows.append(("월 NOI (공실차감)", "formula", [
        f"=B13*(1-B7)", f"=C13*(1-C7)", f"=D13*(1-D7)"
    ], NUM_FMT_KRW))
    # 월 실효임대수익 = NOI(row14) × (1 - 운영비(row8))
    rows.append(("월 실효임대수익", "formula", [
        f"=B14*(1-B8)", f"=C14*(1-C8)", f"=D14*(1-D8)"
    ], NUM_FMT_KRW))
    # 월 PMT: 적용금리(row6, %단위), 대출원금(row10)
    rows.append(("월 원리금 (PMT)", "formula", [
        f"=PMT(B6/100/12, {inp}B22*12, -B10)",
        f"=PMT(C6/100/12, {inp}B22*12, -C10)",
        f"=PMT(D6/100/12, {inp}B22*12, -D10)"
    ], NUM_FMT_KRW))
    # 월 순현금흐름 = 실효임대(row15) - PMT(row16)
    rows.append(("월 순현금흐름", "formula", [
        f"=B15-B16", f"=C15-C16", f"=D15-D16"
    ], NUM_FMT_KRW))

    # [연간 지표] (시작 row 18, 첫 데이터 row 19)
    rows.append(("[연간 지표]", "subheader", None))
    # 연간 NOI 실효 = 월 실효(row15) × 12
    rows.append(("연간 NOI (실효, 만원)", "formula", [
        f"=B15*12", f"=C15*12", f"=D15*12"
    ], NUM_FMT_KRW))
    # 연간 원리금 = 월 PMT(row16) × 12
    rows.append(("연간 원리금 (만원)", "formula", [
        f"=B16*12", f"=C16*12", f"=D16*12"
    ], NUM_FMT_KRW))
    # DSCR = 연간 NOI(row19) / 연간 원리금(row20)
    rows.append(("DSCR", "formula", [
        f"=IF(B20=0,0,B19/B20)", f"=IF(C20=0,0,C19/C20)", f"=IF(D20=0,0,D19/D20)"
    ], NUM_FMT_RATIO))
    # 캐시 일드 = 월순현흐름(row17) × 12 / 자기자본(row11)
    rows.append(("캐시 일드 (자기자본 대비)", "formula", [
        f"=IF(B11=0,0,B17*12/B11)", f"=IF(C11=0,0,C17*12/C11)", f"=IF(D11=0,0,D17*12/D11)"
    ], NUM_FMT_PCT))

    # [매각 시나리오] (시작 row 23, 첫 데이터 row 24)
    rows.append(("[매각 시나리오] (만원)", "subheader", None))
    # 매각 예상가 = 낙찰가 × 매각배수 (입력시트 B33/C33/D33)
    rows.append(("매각 예상가", "formula", [
        f"={inp}B12*{inp}B33", f"={inp}B12*{inp}C33", f"={inp}B12*{inp}D33"
    ], NUM_FMT_KRW))
    # 매각 비용 = 매각가(row24) × 매각비용비율 (입력 B34/C34/D34)
    rows.append(("매각 비용", "formula", [
        f"=B24*{inp}B34", f"=C24*{inp}C34", f"=D24*{inp}D34"
    ], NUM_FMT_KRW))
    # 잔존 대출원금 = 대출원금(row10) + CUMPRINC(금리(row6), 대출기간*12, 대출원금, 1, 보유기간*12, 0)
    # 보유기간 × 12 ≤ 대출기간 × 12 보장 필요. CUMPRINC는 음수이므로 더하면 잔존원금
    # 보유기간이 대출기간 이상인 경우 잔존원금 0 처리 (IFERROR)
    rows.append(("잔존 대출원금", "formula", [
        f"=IFERROR(B10+CUMPRINC(B6/100/12, {inp}B22*12, B10, 1, MIN({inp}B23*12,{inp}B22*12), 0), 0)",
        f"=IFERROR(C10+CUMPRINC(C6/100/12, {inp}B22*12, C10, 1, MIN({inp}B23*12,{inp}B22*12), 0), 0)",
        f"=IFERROR(D10+CUMPRINC(D6/100/12, {inp}B22*12, D10, 1, MIN({inp}B23*12,{inp}B22*12), 0), 0)"
    ], NUM_FMT_KRW))
    # 세전 매각 회수 = 매각가(row24) - 매각비용(row25) - 잔존원금(row26)
    rows.append(("세전 매각 회수", "formula", [
        f"=B24-B25-B26", f"=C24-C25-C26", f"=D24-D25-D26"
    ], NUM_FMT_KRW))

    # [수익률 종합] (시작 row 28, 첫 데이터 row 29)
    rows.append(("[수익률 종합]", "subheader", None))
    # 월 순현흐름(row17) × 보유기간*12
    rows.append(("월 순현금흐름 × 보유기간 합 (만원)", "formula", [
        f"=B17*{inp}B23*12", f"=C17*{inp}B23*12", f"=D17*{inp}B23*12"
    ], NUM_FMT_KRW))
    # 총 회수액 = 월순합(row29) + 매각회수(row27)
    rows.append(("총 회수액 (만원)", "formula", [
        f"=B29+B27", f"=C29+C27", f"=D29+D27"
    ], NUM_FMT_KRW))
    # 총 자기자본 수익률 = (총회수(row30) - 자기자본(row11)) / 자기자본(row11)
    rows.append(("총 자기자본 수익률 (보유기간)", "formula", [
        f"=IF(B11=0,0,(B30-B11)/B11)",
        f"=IF(C11=0,0,(C30-C11)/C11)",
        f"=IF(D11=0,0,(D30-D11)/D11)"
    ], NUM_FMT_PCT))
    # 연환산 IRR = (1 + 총수익률(row31))^(1/보유년) - 1
    # 음수일 경우 (1+음수)^(1/n)에서 n이 정수 아니면 #NUM. IFERROR로 보호
    rows.append(("자기자본 IRR (연환산, 근사)", "formula", [
        f"=IFERROR((1+B31)^(1/{inp}B23)-1, -1)",
        f"=IFERROR((1+C31)^(1/{inp}B23)-1, -1)",
        f"=IFERROR((1+D31)^(1/{inp}B23)-1, -1)"
    ], NUM_FMT_PCT))

    # [판정]
    rows.append(("[판정]", "subheader", None))
    # DSCR(row21) 기반
    rows.append(("DSCR 판정", "formula", [
        f'=IF(B21>=1.25,"안전",IF(B21>=1,"보통","위험"))',
        f'=IF(C21>=1.25,"안전",IF(C21>=1,"보통","위험"))',
        f'=IF(D21>=1.25,"안전",IF(D21>=1,"보통","위험"))'
    ], None))
    # IRR(row32) 기반
    rows.append(("IRR 판정", "formula", [
        f'=IF(B32>=0.15,"GO",IF(B32>=0.08,"검토","NO-GO"))',
        f'=IF(C32>=0.15,"GO",IF(C32>=0.08,"검토","NO-GO"))',
        f'=IF(D32>=0.15,"GO",IF(D32>=0.08,"검토","NO-GO"))'
    ], None))

    # 작성
    row = 4
    for item in rows:
        if item[1] == "subheader":
            set_subheader_cell(ws, f"A{row}", item[0])
            ws.merge_cells(f"A{row}:D{row}")
        elif item[1] in ("formula", "link"):
            set_label_cell(ws, f"A{row}", item[0])
            fmt = item[3] if len(item) > 3 else None
            cells = ["B", "C", "D"]
            for i, col in enumerate(cells):
                if item[1] == "link":
                    set_formula_cell(ws, f"{col}{row}", item[2][i], fmt, link=True)
                else:
                    set_formula_cell(ws, f"{col}{row}", item[2][i], fmt)
        row += 1

    # DSCR(row 21)·IRR(row 32) 조건부 서식
    ws.conditional_formatting.add(
        "B21:D21",
        CellIsRule(operator="greaterThanOrEqual", formula=["1.25"], fill=FILL_GOOD)
    )
    ws.conditional_formatting.add(
        "B21:D21",
        CellIsRule(operator="lessThan", formula=["1"], fill=FILL_BAD)
    )
    ws.conditional_formatting.add(
        "B32:D32",
        CellIsRule(operator="greaterThanOrEqual", formula=["0.15"], fill=FILL_GOOD)
    )
    ws.conditional_formatting.add(
        "B32:D32",
        CellIsRule(operator="lessThan", formula=["0.08"], fill=FILL_BAD)
    )

    return ws


# ============================================================
# Sheet 3: 월별 현금흐름 (중립 시나리오 기준)
# ============================================================
def build_sheet3_monthly(wb, holding_years):
    ws = wb.create_sheet("3.월별현금흐름")

    ws.column_dimensions["A"].width = 8
    for col in "BCDEFG":
        ws.column_dimensions[col].width = 15

    ws["A1"] = "월별 현금흐름 (중립 시나리오 기준)"
    ws["A1"].font = Font(name="맑은 고딕", size=16, bold=True, color="1F4E78")
    ws.merge_cells("A1:G1")

    notice = "본 시트는 중립 시나리오 기준입니다. 보수·공격적 시나리오는 시트 2의 종합 결과를 참조하세요."
    ws["A2"] = notice
    ws["A2"].font = Font(name="맑은 고딕", size=10, italic=True, color="595959")
    ws.merge_cells("A2:G2")

    set_header_row(ws, 4, ["월차", "대출잔액", "이자분", "원금분", "월 NOI(실효)", "월 순현금흐름", "누적 현금흐름"], "A")

    inp = "'1.입력가정값'!"
    cmp_ = "'2.3시나리오비교'!"

    # 중립 시나리오 셀 참조 (시트2 정정된 행번호 기준)
    rate_ref = f"{cmp_}C6"          # 적용금리 (%)
    principal_ref = f"{cmp_}C10"    # 대출원금
    equity_ref = f"{cmp_}C11"       # 자기자본
    monthly_eff_ref = f"{cmp_}C15"  # 월 실효임대수익
    sale_recovery_ref = f"{cmp_}C27" # 세전 매각 회수
    duration_months = f"{inp}B22*12"

    # 시점 0: 자기자본 유출
    ws["A5"] = 0
    ws["A5"].font = FONT_FORMULA
    ws["A5"].alignment = ALIGN_CENTER
    ws["A5"].border = BORDER_THIN

    # 대출잔액(시점 0) = 대출원금
    set_formula_cell(ws, "B5", f"={principal_ref}", NUM_FMT_KRW, link=True)
    # 이자분/원금분/NOI는 시점 0에 0
    set_formula_cell(ws, "C5", "=0", NUM_FMT_KRW)
    set_formula_cell(ws, "D5", "=0", NUM_FMT_KRW)
    set_formula_cell(ws, "E5", "=0", NUM_FMT_KRW)
    # 월 순현흐름(시점 0) = -자기자본 (IRR 계산용)
    set_formula_cell(ws, "F5", f"=-{equity_ref}", NUM_FMT_KRW)
    set_formula_cell(ws, "G5", "=F5", NUM_FMT_KRW)

    # 시점 1 ~ N (N = holding_years × 12)
    n_months = holding_years * 12
    last_row = 5
    for k in range(1, n_months + 1):
        row = 5 + k
        last_row = row
        # 월차
        ws[f"A{row}"] = k
        ws[f"A{row}"].font = FONT_FORMULA
        ws[f"A{row}"].alignment = ALIGN_CENTER
        ws[f"A{row}"].border = BORDER_THIN

        # 대출잔액 (k 시점) = 원금 + CUMPRINC(1, k)
        # 보유 기간이 대출 기간 초과 시 IFERROR 처리
        set_formula_cell(ws, f"B{row}",
            f"=IFERROR({principal_ref}+CUMPRINC({rate_ref}/100/12, {duration_months}, {principal_ref}, 1, MIN({k},{duration_months}), 0), 0)",
            NUM_FMT_KRW)
        # 이자분
        set_formula_cell(ws, f"C{row}",
            f"=IFERROR(-IPMT({rate_ref}/100/12, {k}, {duration_months}, {principal_ref}), 0)",
            NUM_FMT_KRW)
        # 원금분
        set_formula_cell(ws, f"D{row}",
            f"=IFERROR(-PPMT({rate_ref}/100/12, {k}, {duration_months}, {principal_ref}), 0)",
            NUM_FMT_KRW)
        # 월 NOI (실효)
        set_formula_cell(ws, f"E{row}", f"={monthly_eff_ref}", NUM_FMT_KRW, link=True)
        # 월 순현금흐름 = NOI - (이자+원금)
        set_formula_cell(ws, f"F{row}", f"=E{row}-C{row}-D{row}", NUM_FMT_KRW)
        # 누적 현금흐름
        set_formula_cell(ws, f"G{row}", f"=G{row-1}+F{row}", NUM_FMT_KRW)

    # 매각 시점 행 (별도 추가) — 마지막 월에 매각 회수 가산
    sale_row = last_row + 1
    ws[f"A{sale_row}"] = "매각"
    ws[f"A{sale_row}"].font = FONT_SUBHEADER
    ws[f"A{sale_row}"].alignment = ALIGN_CENTER
    ws[f"A{sale_row}"].fill = FILL_SUBHEADER
    ws[f"A{sale_row}"].border = BORDER_THIN
    set_formula_cell(ws, f"B{sale_row}", "=0", NUM_FMT_KRW)
    set_formula_cell(ws, f"C{sale_row}", "=0", NUM_FMT_KRW)
    set_formula_cell(ws, f"D{sale_row}", "=0", NUM_FMT_KRW)
    set_formula_cell(ws, f"E{sale_row}", "=0", NUM_FMT_KRW)
    # 매각 회수
    set_formula_cell(ws, f"F{sale_row}", f"={sale_recovery_ref}", NUM_FMT_KRW, link=True)
    set_formula_cell(ws, f"G{sale_row}", f"=G{sale_row-1}+F{sale_row}", NUM_FMT_KRW)

    # IRR 계산 (월별 F 컬럼 전체)
    # IRR 함수에 초기 추정치 0.01 (월 1%) 명시 — 수렴 실패 방지
    irr_row = sale_row + 2
    set_subheader_cell(ws, f"A{irr_row}", "월간 IRR")
    set_formula_cell(ws, f"B{irr_row}", f"=IFERROR(IRR(F5:F{sale_row}, 0.01), 0)", NUM_FMT_PCT)
    set_subheader_cell(ws, f"A{irr_row+1}", "연환산 IRR (정밀)")
    set_formula_cell(ws, f"B{irr_row+1}", f"=IFERROR((1+B{irr_row})^12-1, 0)", NUM_FMT_PCT)

    return ws, sale_row


# ============================================================
# Sheet 4: 임계 LTV 분석
# ============================================================
def build_sheet4_breakeven(wb):
    ws = wb.create_sheet("4.임계LTV분석")

    ws.column_dimensions["A"].width = 12
    for col in "BCDE":
        ws.column_dimensions[col].width = 18

    ws["A1"] = "임계 LTV 분석 (DSCR 곡선)"
    ws["A1"].font = Font(name="맑은 고딕", size=16, bold=True, color="1F4E78")
    ws.merge_cells("A1:E1")

    notice = "DSCR=1.0 임계 LTV는 임대수익으로 부채상환이 가능한 최대 레버리지 비율입니다. 적용 LTV가 임계치에서 멀수록 안전합니다."
    ws["A2"] = notice
    ws["A2"].font = Font(name="맑은 고딕", size=10, italic=True, color="595959")
    ws["A2"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A2:E2")
    ws.row_dimensions[2].height = 30

    set_header_row(ws, 4, ["LTV", "대출원금(만원)", "월 PMT(만원)", "DSCR", "판정"], "A")

    inp = "'1.입력가정값'!"
    cmp_ = "'2.3시나리오비교'!"

    # 중립 시나리오 기준 LTV 변동
    bid_cell = f"{inp}B12"
    rate_cell = f"{cmp_}C6"  # 중립 적용금리 (%)
    duration_cell = f"{inp}B22"
    noi_annual = f"{cmp_}C19"  # 연간 NOI (실효, 시트2 row 19)

    ltv_values = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    for i, ltv in enumerate(ltv_values):
        row = 5 + i
        # LTV
        ws[f"A{row}"] = ltv
        ws[f"A{row}"].font = FONT_INPUT
        ws[f"A{row}"].fill = FILL_INPUT
        ws[f"A{row}"].number_format = NUM_FMT_PCT
        ws[f"A{row}"].border = BORDER_THIN
        # 대출원금
        set_formula_cell(ws, f"B{row}", f"={bid_cell}*A{row}", NUM_FMT_KRW)
        # 월 PMT (금리 %단위 → /100/12)
        set_formula_cell(ws, f"C{row}",
            f"=PMT({rate_cell}/100/12, {duration_cell}*12, -B{row})",
            NUM_FMT_KRW)
        # DSCR = 연간 NOI / (월 PMT × 12)
        set_formula_cell(ws, f"D{row}",
            f"=IF(C{row}=0, 0, {noi_annual}/(C{row}*12))",
            NUM_FMT_RATIO)
        # 판정
        set_formula_cell(ws, f"E{row}",
            f'=IF(D{row}>=1.25,"안전",IF(D{row}>=1,"보통",IF(D{row}>=0.8,"주의","위험")))',
            None)

    # DSCR 컬럼 조건부 서식
    last_row = 5 + len(ltv_values) - 1
    ws.conditional_formatting.add(
        f"D5:D{last_row}",
        ColorScaleRule(
            start_type="num", start_value=0.5, start_color="F8696B",
            mid_type="num", mid_value=1.0, mid_color="FFEB84",
            end_type="num", end_value=1.5, end_color="63BE7B"
        )
    )

    # 임계 LTV 계산
    summary_row = last_row + 2
    set_subheader_cell(ws, f"A{summary_row}", "임계 LTV (DSCR=1.0)")
    # 임계 대출원금 = 연간 NOI / PMT_factor_연간
    # PMT_factor_연간 = PMT(rate/100/12, duration*12, -1) * 12
    set_formula_cell(ws, f"B{summary_row}",
        f"={noi_annual}/(PMT({rate_cell}/100/12, {duration_cell}*12, -1)*12)",
        NUM_FMT_KRW)
    set_label_cell(ws, f"C{summary_row}", "임계 LTV →")
    set_formula_cell(ws, f"D{summary_row}",
        f"=B{summary_row}/{bid_cell}",
        NUM_FMT_PCT)

    set_subheader_cell(ws, f"A{summary_row+1}", "임계 LTV (DSCR=1.25)")
    set_formula_cell(ws, f"B{summary_row+1}",
        f"=({noi_annual}/1.25)/(PMT({rate_cell}/100/12, {duration_cell}*12, -1)*12)",
        NUM_FMT_KRW)
    set_label_cell(ws, f"C{summary_row+1}", "임계 LTV →")
    set_formula_cell(ws, f"D{summary_row+1}",
        f"=B{summary_row+1}/{bid_cell}",
        NUM_FMT_PCT)

    # DSCR 곡선 차트
    chart = LineChart()
    chart.title = "LTV vs DSCR 곡선"
    chart.x_axis.title = "LTV"
    chart.y_axis.title = "DSCR"
    chart.height = 10
    chart.width = 18

    data = Reference(ws, min_col=4, min_row=4, max_row=last_row, max_col=4)
    cats = Reference(ws, min_col=1, min_row=5, max_row=last_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    ws.add_chart(chart, f"G4")

    return ws


# ============================================================
# Sheet 5: 민감도 분석
# ============================================================
def build_sheet5_sensitivity(wb):
    ws = wb.create_sheet("5.민감도분석")

    ws.column_dimensions["A"].width = 18
    for col in "BCDEFG":
        ws.column_dimensions[col].width = 15

    ws["A1"] = "민감도 분석 (중립 시나리오 기준)"
    ws["A1"].font = Font(name="맑은 고딕", size=16, bold=True, color="1F4E78")
    ws.merge_cells("A1:G1")

    notice = "각 변수를 ±10% 변동시킬 때 자기자본 IRR의 변화를 측정합니다. 가장 보수적 조합에서도 양(+)의 IRR이면 견고한 투자입니다."
    ws["A2"] = notice
    ws["A2"].font = Font(name="맑은 고딕", size=10, italic=True, color="595959")
    ws["A2"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A2:G2")
    ws.row_dimensions[2].height = 30

    inp = "'1.입력가정값'!"
    cmp_ = "'2.3시나리오비교'!"

    # === 매트릭스 1: 금리 × 매각가 ===
    set_subheader_cell(ws, "A4", "[매트릭스 1] 금리 × 매각가 → 자기자본 IRR (연환산 근사)")
    ws.merge_cells("A4:E4")

    set_header_row(ws, 5, ["금리 / 매각가", "매각가 -10%", "매각가 기준", "매각가 +10%"], "A")

    # 매트릭스 1 셀 매핑:
    # B6: 금리-1%p, 매각가-10% / C6: 금리-1%p, 매각가 기준 / D6: 금리-1%p, 매각가+10%
    # B7: 금리 기준, 매각가-10% / C7: 기준 / D7: 매각가+10%
    # B8: 금리+1%p, ... 

    # 간이 IRR 근사 계산식:
    # 자기자본 = 낙찰가 × (1 - LTV)
    # 월 PMT_변동 = PMT(금리변동/12, 기간*12, -대출원금)
    # 월 순현흐름 = NOI(실효) - 월 PMT
    # 매각 회수 = 매각가 × 매각배수 × 매각배수변동 - 매각비용 - 잔존원금(금리변동)
    # 총수익 = 월순현흐름 × 보유기간*12 + 매각 회수
    # IRR = (1 + (총수익-자기자본)/자기자본)^(1/보유년) - 1

    # 단순화를 위해 다음 변수만 변동:
    # - 금리: 중립금리 ± 1%p
    # - 매각가: 매각가 × (1 ± 10%)

    bid = f"{inp}B12"
    ltv = f"{cmp_}C5"             # 시트2 LTV (row 5)
    base_rate = f"{cmp_}C6"       # 시트2 적용금리 (row 6, % 단위)
    duration = f"{inp}B22"
    holding = f"{inp}B23"
    monthly_eff = f"{cmp_}C15"    # 시트2 월 실효임대수익 (row 15)
    exit_mult = f"{inp}C33"
    exit_cost = f"{inp}C34"
    equity = f"{cmp_}C11"         # 시트2 자기자본 (row 11)

    rate_offsets = [-1, 0, 1]
    sale_multipliers = [0.9, 1.0, 1.1]
    rate_labels = ["금리 -1%p", "금리 기준", "금리 +1%p"]

    for i, ro in enumerate(rate_offsets):
        row = 6 + i
        set_label_cell(ws, f"A{row}", rate_labels[i])
        for j, sm in enumerate(sale_multipliers):
            col = chr(ord("B") + j)
            # 변동 금리 (% 단위)
            r = f"({base_rate}+{ro})/100/12"
            # 대출원금
            P = f"({bid}*{ltv})"
            # 변동 월 PMT
            pmt = f"PMT({r}, {duration}*12, -{P})"
            # 월 순현흐름 = 월 NOI 실효 - 월 PMT
            mcf = f"({monthly_eff}-{pmt})"
            # 잔존원금 (변동 금리)
            remaining = f"({P}+CUMPRINC({r}, {duration}*12, {P}, 1, MIN({holding}*12,{duration}*12), 0))"
            # 매각 회수 = 매각가×배수×변동 - 매각비용×(매각가×배수×변동) - 잔존
            sale_price = f"({bid}*{exit_mult}*{sm})"
            recovery = f"({sale_price}*(1-{exit_cost})-{remaining})"
            # 총 회수 = 월순현흐름×보유*12 + 매각회수
            total = f"({mcf}*{holding}*12+{recovery})"
            # 총 수익률
            total_return = f"(({total}-{equity})/{equity})"
            # 연환산 IRR (IFERROR 보호: 음수 총수익률 시 #NUM 방지)
            irr = f"IFERROR((1+{total_return})^(1/{holding})-1, -1)"
            set_formula_cell(ws, f"{col}{row}", f"={irr}", NUM_FMT_PCT)

    # 조건부 서식 (매트릭스 1)
    ws.conditional_formatting.add(
        "B6:D8",
        ColorScaleRule(
            start_type="min", start_color="F8696B",
            mid_type="percentile", mid_value=50, mid_color="FFEB84",
            end_type="max", end_color="63BE7B"
        )
    )

    # === 매트릭스 2: 공실률 × 임대료 ===
    set_subheader_cell(ws, "A11", "[매트릭스 2] 공실률 × 임대료 → 자기자본 IRR (연환산 근사)")
    ws.merge_cells("A11:E11")

    set_header_row(ws, 12, ["임대료 / 공실률", "공실 -5%p", "공실 기준", "공실 +10%p"], "A")

    rent_offsets = [0.9, 1.0, 1.1]
    vacancy_offsets = [-0.05, 0, 0.10]
    rent_labels = ["임대료 -10%", "임대료 기준", "임대료 +10%"]

    base_rent = f"{inp}B14"
    base_vacancy = f"{cmp_}C7"
    base_opex = f"{cmp_}C8"

    for i, ro in enumerate(rent_offsets):
        row = 13 + i
        set_label_cell(ws, f"A{row}", rent_labels[i])
        for j, vo in enumerate(vacancy_offsets):
            col = chr(ord("B") + j)
            # 변동 임대료·공실률
            rent_var = f"({base_rent}*{ro})"
            vac_var = f"MAX(0,{base_vacancy}+{vo})"
            # 월 NOI 실효
            mcf_eff_var = f"({rent_var}*(1-{vac_var})*(1-{base_opex}))"
            # 월 PMT (금리는 중립, % 단위)
            r = f"{base_rate}/100/12"
            P = f"({bid}*{ltv})"
            pmt = f"PMT({r}, {duration}*12, -{P})"
            mcf = f"({mcf_eff_var}-{pmt})"
            remaining = f"({P}+CUMPRINC({r}, {duration}*12, {P}, 1, MIN({holding}*12,{duration}*12), 0))"
            sale_price = f"({bid}*{exit_mult})"
            recovery = f"({sale_price}*(1-{exit_cost})-{remaining})"
            total = f"({mcf}*{holding}*12+{recovery})"
            total_return = f"(({total}-{equity})/{equity})"
            irr = f"IFERROR((1+{total_return})^(1/{holding})-1, -1)"
            set_formula_cell(ws, f"{col}{row}", f"={irr}", NUM_FMT_PCT)

    ws.conditional_formatting.add(
        "B13:D15",
        ColorScaleRule(
            start_type="min", start_color="F8696B",
            mid_type="percentile", mid_value=50, mid_color="FFEB84",
            end_type="max", end_color="63BE7B"
        )
    )

    # === 핵심 시사점 ===
    set_subheader_cell(ws, "A18", "[핵심 시사점]")
    ws.merge_cells("A18:E18")

    insights = [
        "1. 가장 보수적 조합(금리+1%p × 매각가-10%)에서 양(+)의 IRR을 유지하면 다운사이드 보호 우수",
        "2. 임대료보다 공실률 변동이 IRR에 더 큰 영향을 줄 수 있으며, 임차인 안정성 확보가 핵심",
        "3. 매각가 가정의 ±10% 변동은 보유 기간이 짧을수록 IRR에 더 큰 영향",
        "4. 본 매트릭스는 모든 변수가 독립적으로 변동한다고 가정. 실제로는 금리 상승 시 공실률·매각가도 동반 악화 가능",
    ]
    for i, txt in enumerate(insights):
        ws[f"A{19+i}"] = txt
        ws[f"A{19+i}"].font = Font(name="맑은 고딕", size=10, color="595959")
        ws.merge_cells(f"A{19+i}:E{19+i}")

    return ws


# ============================================================
# Main 빌드 함수
# ============================================================
def build_excel(params: dict, output_path: str):
    # 시나리오 병합
    user_scenarios = params.get("scenarios")
    borrower_type = params["borrower"]["type"]
    params["_resolved_scenarios"] = merge_scenarios(user_scenarios, borrower_type)

    # 빈 워크북 생성
    wb = Workbook()

    # 시트 빌드
    build_sheet1_inputs(wb, params)
    build_sheet2_comparison(wb)
    build_sheet3_monthly(wb, params["loan"]["holding_years"])
    build_sheet4_breakeven(wb)
    build_sheet5_sensitivity(wb)

    # 저장
    wb.save(output_path)
    print(f"✅ Excel 파일 생성 완료: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        # 데모용 기본 파라미터
        demo_params = {
            "property": {
                "name": "데모 아파트",
                "type": "아파트",
                "address": "서울시 강남구 역삼동 123-45",
                "case_number": "2024타경12345"
            },
            "amounts": {
                "winning_bid_10k": 100000,
                "appraisal_10k": 120000,
                "monthly_rent_10k": 400
            },
            "borrower": {
                "type": "SPC",
                "market_rate_pct": 5.0
            },
            "loan": {
                "duration_years": 20,
                "holding_years": 3,
                "amortization": "원리금균등"
            },
            "scenarios": None  # 차주 디폴트 사용
        }
        output = "/tmp/demo_output.xlsx"
        build_excel(demo_params, output)
    else:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            params = json.load(f)
        build_excel(params, sys.argv[2])
