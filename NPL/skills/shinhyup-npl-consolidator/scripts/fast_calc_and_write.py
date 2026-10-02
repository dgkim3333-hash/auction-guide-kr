#!/usr/bin/env python3
"""
신협 NPL 전체현황 - 고속 값 계산 & 입력 스크립트

핵심 전략: Excel 수식을 전혀 사용하지 않는다.
모든 계산(대출잔액, 대출이자, 상환 추정, 가지급금)을 Python에서 수행하고,
결과를 "순수 값(value only)"으로 셀에 입력한다.
→ Recalculate formulas 단계가 완전히 제거되어 처리 속도가 대폭 향상된다.

사용법:
    python scripts/fast_calc_and_write.py <마스터파일> <출력파일> [신규파일1 신규파일2 ...]

    - 신규 파일 없이 마스터 파일만 지정하면: 기존 행의 계산 컨럼만 재산정
    - 신규 파일을 함께 지정하면: 신규 데이터 추가 + 전체 계산 산정
"""

import sys
import os
import math
from datetime import date
from copy import copy

try:
    import openpyxl
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Font, Alignment, Border, Side, numbers
except ImportError:
    print("ERROR: openpyxl 필요. pip install openpyxl --break-system-packages")
    sys.exit(1)


# ============================================================
# 1. 경매신청비용(가지급금) 계산 함수 — 순수 Python, 수식 없음
# ============================================================

def calc_auction_cost(appraisal_value, bond_amount, stakeholders=5, properties=1):
    """
    경매신청비용(가지급금)을 Python 값으로 산정한다.
    Excel 수식이 아닌 최종 숫자만 반환한다.
    """
    if not appraisal_value or appraisal_value <= 0:
        return None
    if not bond_amount or bond_amount <= 0:
        return None

    v = appraisal_value

    # --- 신청비용 ---
    registration_tax = int(bond_amount * 0.002)
    education_tax = int(registration_tax * 0.2)
    delivery_fee = (stakeholders + 3) * 10 * 5200
    registration_fee = properties * 3000
    application_sub = registration_tax + education_tax + delivery_fee + registration_fee

    # --- 감정평가수수료 ---
    if v <= 140_909_090:
        appraisal_fee = 240_000
    elif v <= 500_000_000:
        appraisal_fee = int(v * 0.0011 + 84_000)
    elif v <= 1_000_000_000:
        appraisal_fee = int(v * 0.0009 + 184_000)
    elif v <= 5_000_000_000:
        appraisal_fee = int(v * 0.0006 + 484_000)
    elif v <= 10_000_000_000:
        appraisal_fee = int(v * 0.0005 + 984_000)
    else:
        appraisal_fee = int(v * 0.0004 + 1_984_000)

    appraisal_expense = int(appraisal_fee * 0.2)
    appraisal_sub = int((appraisal_fee + appraisal_expense) * 1.1)

    # --- 현황조사수수료 ---
    survey_fee = 70_000

    # --- 신문공고료 ---
    newspaper_fee = 220_000
    if properties > 2:
        newspaper_fee += (properties - 2) * 110_000

    # --- 매각수수료 ---
    if v <= 10_000_000:
        sale_fee = 200_000
    elif v <= 50_000_000:
        sale_fee = int((v - 10_000_000) * 0.015 + 200_000)
    elif v <= 100_000_000:
        sale_fee = int((v - 50_000_000) * 0.01 + 803_000)
    elif v <= 300_000_000:
        sale_fee = int((v - 100_000_000) * 0.008 + 1_303_000)
    elif v <= 500_000_000:
        sale_fee = int((v - 300_000_000) * 0.006 + 2_903_000)
    elif v <= 1_000_000_000:
        sale_fee = int((v - 500_000_000) * 0.004 + 4_103_000)
    elif v <= 3_000_000_000:
        sale_fee = int((v - 1_000_000_000) * 0.002 + 6_103_000)
    else:
        sale_fee = int((v - 3_000_000_000) * 0.001 + 10_103_000)

    prepayment_sub = appraisal_sub + survey_fee + newspaper_fee + sale_fee

    return application_sub + prepayment_sub


# ============================================================
# 2. 대출잔액 / 대출이자 / 상환 추정 계산 함수
# ============================================================

def calc_loan_balance(bond_max_amount):
    """채권최고액 ÷ 1.2 → 대출잔액 (원 단위 절사)"""
    if not bond_max_amount or bond_max_amount <= 0:
        return None
    return int(bond_max_amount / 1.2)


def calc_loan_interest(claim_amount, loan_balance):
    """청구금액 - 대출잔액 → 대출이자"""
    if claim_amount is None or loan_balance is None:
        return None, None, None  # interest_total, note, adjusted_balance
    
    if claim_amount < loan_balance:
        # 상환 추정: 10% 상환 1회 적용
        adjusted_balance = int(loan_balance * 0.9)
        interest = claim_amount - adjusted_balance
        if interest < 0:
            # 보정 후에도 음수면 추가 상환 가능성
            return interest, "추가 상환 가능성, 10% 상환 추정 적용", adjusted_balance
        return interest, "10% 상환 추정 적용", adjusted_balance
    else:
        interest = claim_amount - loan_balance
        return interest, None, loan_balance


# ============================================================
# 3. 셀 값 안전 읽기 유틸
# ============================================================

def safe_num(val):
    """셀 값을 숫자로 변환. 수식 문자열이면 None 반환."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        s = val.strip().replace(',', '').replace('원', '').replace(' ', '')
        if s.startswith('='):
            return None  # Excel 수식 → 값 없음
        if s in ('', '-', 'N/A', 'n/a'):
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


# ============================================================
# 4. 메인: 마스터 파일 열고 → 계산 → 값만 쓰기
# ============================================================

def process_master(master_path, output_path):
    """
    마스터 파일의 모든 데이터 행에 대해:
    - P열(대출잔액), Q+R열(이자), S열(가지급금)을 Python으로 계산
    - 결과를 순수 값으로 셀에 직접 입력 (수식 없음)
    - 기존 수식이 있으면 계산된 값으로 대체
    """
    print(f"📂 마스터 파일 로드: {master_path}")
    wb = openpyxl.load_workbook(master_path)
    ws = wb.active

    # 컨럼 인덱스 (B열=2부터 시작)
    COL_B_NO = 2
    COL_O_APPRAISAL = 15   # 감정가
    COL_P_BALANCE = 16      # 대출잔액
    COL_Q_NORMAL_INT = 17   # 정상이자
    COL_R_OVERDUE_INT = 18  # 연체이자
    COL_S_ADVANCE = 19      # 가지급금
    COL_T_TOTAL_CLAIM = 20  # 채권합계(청구금액)
    COL_V_BOND_MAX = 22     # 채권최고액
    COL_W_RATE = 23         # 이자율
    COL_X_OVERDUE_RATE = 24 # 연체이자율
    COL_Y_NOTE = 25         # 비고

    # 헤더 행 찾기 (보통 3행)
    header_row = 3
    data_start = header_row + 1

    calc_count = {
        'balance': 0,
        'interest': 0,
        'repayment': 0,
        'advance': 0,
        'skipped': 0,
    }

    total_rows = ws.max_row
    print(f"📊 전체 행 수: {total_rows}, 데이터 시작: {data_start}행")

    for row_idx in range(data_start, total_rows + 1):
        # 빈 행 스킵 (No. 컨럼이 비어있으면)
        no_val = ws.cell(row=row_idx, column=COL_B_NO).value
        if no_val is None:
            continue

        bond_max = safe_num(ws.cell(row=row_idx, column=COL_V_BOND_MAX).value)
        appraisal = safe_num(ws.cell(row=row_idx, column=COL_O_APPRAISAL).value)
        claim_total = safe_num(ws.cell(row=row_idx, column=COL_T_TOTAL_CLAIM).value)

        notes = []
        existing_note = ws.cell(row=row_idx, column=COL_Y_NOTE).value
        if existing_note and isinstance(existing_note, str):
            # 기존 자동산정 메모 제거 후 원본 비고 유지
            cleaned = existing_note
            for tag in ["10% 상환 추정 적용", "추가 상환 가능성", "산정 이상", "자동산정"]:
                cleaned = cleaned.replace(tag, "").strip(", ")
            if cleaned:
                notes.append(cleaned)

        # --- 대출잔액 산정 (P열) ---
        if bond_max and bond_max > 0:
            loan_balance = calc_loan_balance(bond_max)
            ws.cell(row=row_idx, column=COL_P_BALANCE).value = loan_balance
            calc_count['balance'] += 1
        else:
            loan_balance = safe_num(ws.cell(row=row_idx, column=COL_P_BALANCE).value)

        # --- 대출이자 산정 (Q+R열) ---
        if claim_total and loan_balance:
            interest, note, adjusted_balance = calc_loan_interest(claim_total, loan_balance)
            
            if adjusted_balance != loan_balance:
                # 상환 추정 적용됨 → P열 보정
                ws.cell(row=row_idx, column=COL_P_BALANCE).value = adjusted_balance
                calc_count['repayment'] += 1
            
            if note:
                notes.append(note)

            if interest is not None:
                # 청구금액 - 대출잔액 = 정상이자(Q컨럼)에 전액 입력
                ws.cell(row=row_idx, column=COL_Q_NORMAL_INT).value = max(0, int(interest))
                # R컨럼(연체이자)은 별도 연체이자 정보가 원본에 있을 때만 입력
                # 자동 산정에서는 건드리지 않는다
                
                calc_count['interest'] += 1

        # --- 가지급금 산정 (S열) ---
        if appraisal and bond_max:
            advance = calc_auction_cost(appraisal, bond_max)
            if advance:
                ws.cell(row=row_idx, column=COL_S_ADVANCE).value = advance
                calc_count['advance'] += 1

        # --- 비고 업데이트 ---
        if notes:
            ws.cell(row=row_idx, column=COL_Y_NOTE).value = ", ".join(notes)

    # --- 금액 서식 적용 ---
    number_format = '#,##0'
    for row_idx in range(data_start, total_rows + 1):
        for col in [COL_O_APPRAISAL, COL_P_BALANCE, COL_Q_NORMAL_INT,
                     COL_R_OVERDUE_INT, COL_S_ADVANCE, COL_T_TOTAL_CLAIM, 22]:  # V열=22
            cell = ws.cell(row=row_idx, column=col)
            if isinstance(cell.value, (int, float)):
                cell.number_format = number_format

    # --- 저장 ---
    print(f"\n💾 저장: {output_path}")
    wb.save(output_path)
    wb.close()

    print(f"""
✅ 고속 계산 완료 (수식 재계산 없음 — 모든 값 Python 산정)

💰 산정 결과
  - 대출잔액 산정: {calc_count['balance']}건 (채권최고액 ÷ 1.2)
  - 대출이자 산정: {calc_count['interest']}건 (청구금액 - 대출잔액)
  - 상환 추정 적용: {calc_count['repayment']}건 (10% 상환 추정)
  - 가지급금 산정: {calc_count['advance']}건 (경매비용 자동계산)
  - 스킵(데이터 부족): {calc_count['skipped']}건
""")

    return calc_count


# ============================================================
# 5. CLI 진입점
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python fast_calc_and_write.py <마스터파일.xlsx> <출력파일.xlsx>")
        sys.exit(1)
    
    master = sys.argv[1]
    output = sys.argv[2]
    
    if not os.path.exists(master):
        print(f"ERROR: 파일 없음 - {master}")
        sys.exit(1)
    
    process_master(master, output)
