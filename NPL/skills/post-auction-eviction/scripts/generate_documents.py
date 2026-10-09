#!/usr/bin/env python3
"""
경매 낙찰 후 명도 절차 문서 자동 생성기

시나리오별로 필요한 법률 문서(인도명령신청서, 강제집행신청서, 내용증명,
명도합의서, 명도소송 소장, 부당이득반환 소장, 유치권 부존재확인 소장)를
사용자 입력값으로 치환하여 완성본 DOCX로 출력한다.

사용법:
    python generate_documents.py --doc-type indo_myeongryeong --params params.json --output 신청서.docx

또는 모든 시나리오 문서를 한 번에:
    python generate_documents.py --scenario A --params params.json --output-dir /path/to/dir/
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


# 한글 폰트 적용 헬퍼
def set_korean_font(run, font_name="맑은 고딕", size_pt=11, bold=False):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), font_name)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)


def add_paragraph(doc, text, *, bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_korean_font(run, size_pt=size, bold=bold)
    return p


def add_title(doc, text):
    add_paragraph(doc, text, bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)


def add_h2(doc, text):
    add_paragraph(doc, text, bold=True, size=13, space_after=10)


def add_warning_footer(doc):
    doc.add_paragraph()  # 여백
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(
        "⚠️ 본 문서는 자동 생성된 초안입니다. 제출 전 다음을 확인하세요:\n"
        "  1. 당사자 표시(주민등록번호·법인등록번호) 정확성\n"
        "  2. 송달주소 유효성\n"
        "  3. 인지액·송달료 최신 기준 (대법원 전자소송)\n"
        "  4. 대항력 있는 임차인·유치권 분쟁 시 변호사·법무사 검토 필수\n"
        "  5. 사건번호·법원명·당사자명 오기 여부 재확인"
    )
    set_korean_font(run, size_pt=9)
    run.italic = True


def setup_document() -> Document:
    """A4, 한글 표준 여백으로 문서 초기화."""
    doc = Document()
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    return doc


# ========== 문서별 생성 함수 ==========

def gen_indo_myeongryeong(params: dict) -> Document:
    """01. 부동산 인도명령 신청서 (시나리오 A, D 공용)"""
    doc = setup_document()
    add_title(doc, "부동산 인도명령 신청서")

    # 사건/당사자 표시
    add_paragraph(doc, f"사건: {params['case_no']} 부동산임의경매(또는 강제경매)", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"신청인(매수인): {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    if params.get("applicant_id"):
        add_paragraph(doc, f"  주민등록번호(법인등록번호): {params['applicant_id']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"피신청인(점유자): {params['occupant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")

    add_h2(doc, "신청취지")
    add_paragraph(
        doc,
        "  피신청인은 신청인에게 별지 목록 기재 부동산을 인도하라.\n  라는 결정을 구합니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "신청이유")
    scenario = params.get("scenario", "A")
    if scenario == "D":
        reason_text = (
            f"  1. 신청인은 위 사건의 매각절차에서 별지 목록 기재 부동산을 매수하여 "
            f"{params.get('payment_date', '')} 매각대금을 완납함으로써 소유권을 취득하였습니다.\n\n"
            "  2. 피신청인은 위 부동산의 임차인으로서 배당요구를 하였고, 배당기일에 "
            "보증금 전액을 배당받음으로써 점유 권원이 소멸하였음에도 불구하고 부동산의 "
            "인도를 거부하고 있습니다.\n\n"
            "  3. 따라서 민사집행법 제136조 제1항에 의하여 신청취지 기재와 같은 결정을 "
            "구하기 위하여 본 신청에 이른 것입니다."
        )
    else:
        reason_text = (
            f"  1. 신청인은 위 사건의 매각절차에서 별지 목록 기재 부동산을 매수하여 "
            f"{params.get('payment_date', '')} 매각대금을 완납함으로써 소유권을 취득하였습니다.\n\n"
            "  2. 피신청인은 정당한 권원 없이 위 부동산을 점유하면서 신청인의 인도 요구에 "
            "응하지 아니하고 있습니다.\n\n"
            "  3. 따라서 민사집행법 제136조 제1항에 의하여 신청취지 기재와 같은 결정을 "
            "구하기 위하여 본 신청에 이른 것입니다."
        )
    add_paragraph(doc, reason_text, size=11)
    add_paragraph(doc, "")

    add_h2(doc, "첨부서류")
    attachments = [
        "1. 매각허가결정 정본 1부",
        "2. 매각대금완납증명 1부",
        "3. 부동산등기부등본 1부",
        "4. 신청인 신분증(법인등기부등본) 사본 1부",
    ]
    if scenario == "D":
        attachments.append("5. 배당표 사본 1부")
    for a in attachments:
        add_paragraph(doc, f"  {a}", size=11, space_after=2)
    add_paragraph(doc, "")

    # 일자 + 신청인
    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  신청인: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"{params['court_name']} 귀중", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=12)

    # 별지
    doc.add_page_break()
    add_h2(doc, "[별지] 부동산의 표시")
    add_paragraph(doc, params["property_description"], size=11)

    add_warning_footer(doc)
    return doc


def gen_naeyong_jeungmyeong(params: dict) -> Document:
    """03. 내용증명 (1차 명도 요청)"""
    doc = setup_document()
    add_title(doc, "내 용 증 명")
    add_paragraph(doc, "")
    add_paragraph(doc, f"수신인: {params['occupant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"발신인: {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    add_paragraph(doc, f"  연락처: {params.get('applicant_phone', '')}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"제목: 부동산 인도 요청 (사건 {params['case_no']})", bold=True, size=12)
    add_paragraph(doc, "")

    body = (
        f"1. 발신인은 귀하가 점유하고 있는 아래 부동산(이하 '본 부동산')을 "
        f"{params['court_name']} {params['case_no']} 부동산경매 사건에서 매수하여 "
        f"{params.get('payment_date', '')} 매각대금을 완납함으로써 적법하게 소유권을 취득한 매수인입니다.\n\n"
        "2. 본 부동산의 표시\n"
        f"   {params['property_description']}\n\n"
        "3. 발신인은 위와 같이 본 부동산의 소유자로서 귀하에게 본 부동산의 인도를 정중히 요청드립니다.\n\n"
        f"4. 본 통고가 도달한 날로부터 {params.get('demand_days', 14)}일 이내에 자진하여 본 부동산을 "
        "인도하여 주시기 바랍니다. 만약 위 기한 내에 인도가 이루어지지 아니할 경우 발신인은 "
        "민사집행법 제136조에 의한 부동산 인도명령 신청, 강제집행 신청 등 법적 조치를 취할 "
        "예정이며, 이로 인하여 발생하는 일체의 비용(집행비용·변호사비·노무비 등) 및 본 부동산 "
        "점유로 인한 부당이득(월세 상당액)은 귀하에게 청구할 것임을 알려드립니다.\n\n"
        "5. 또한 자진 이주 시 이사 일정·이사비 협의 등 원만한 해결을 희망하므로, 본 통고를 "
        "받으신 후 가능한 한 신속히 발신인에게 연락주시기 바랍니다.\n\n"
        "6. 본 통고는 향후 법적 분쟁에 대비한 증거자료로 사용될 수 있음을 알려드립니다."
    )
    add_paragraph(doc, body, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  발신인: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)

    add_warning_footer(doc)
    return doc


def gen_myeongdo_hapuiseo(params: dict) -> Document:
    """04. 명도합의서"""
    doc = setup_document()
    add_title(doc, "명 도 합 의 서")

    add_paragraph(doc, f"매수인(이하 '갑'): {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"점유자(이하 '을'): {params['occupant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(
        doc,
        f"갑과 을은 {params['court_name']} {params['case_no']} 부동산경매 사건의 매각 부동산 "
        f"(아래 표시)에 관하여 다음과 같이 명도에 합의한다.",
        size=11,
    )
    add_paragraph(doc, "")
    add_h2(doc, "[부동산의 표시]")
    add_paragraph(doc, params["property_description"], size=11)
    add_paragraph(doc, "")

    moveout_date = params.get("moveout_date", "협의 후 기재")
    isabi = params.get("isabi", "협의 후 기재")
    isabi_advance = params.get("isabi_advance", "협의 후 기재")
    isabi_balance = params.get("isabi_balance", "협의 후 기재")

    clauses = [
        f"제1조 (이주 완료 기한) 을은 {moveout_date}까지 본 부동산에서 자진 이주하여 갑에게 인도한다.",
        f"제2조 (이사비) 갑은 을에게 이사비로 금 {isabi}원을 지급한다. 다만, 본 합의서 작성 시 금 {isabi_advance}원을 선지급하고, 이주 완료 및 열쇠 인수 시 잔액 금 {isabi_balance}원을 지급한다.",
        "제3조 (시설물 원상유지) 을은 이주 시까지 본 부동산의 시설물(전기·수도·가스·내장재 등)을 정상 상태로 유지하고, 임의로 훼손하지 아니한다.",
        "제4조 (잔존 동산 처분 위임) 을이 이주 후 본 부동산에 남긴 동산은 갑이 임의로 처분할 수 있으며, 을은 그 처분에 대하여 일체의 이의를 제기하지 아니한다.",
        "제5조 (위약 시 효과) 을이 제1조의 기한 내에 이주를 완료하지 아니하는 경우, 갑은 즉시 강제집행을 진행할 수 있으며, 을은 본 합의서에 의한 강제집행에 동의하고 이의를 제기하지 아니한다. 이 경우 갑이 지급한 이사비는 위약금으로 갑이 회수한다.",
        f"제6조 (부당이득) 을이 제1조의 기한을 초과하여 점유하는 경우, 그 초과 일수에 대하여 일 금 {params.get('daily_unfair_gain', '협의')}원의 부당이득금을 갑에게 지급한다.",
        "제7조 (관할) 본 합의에 관한 분쟁의 관할은 본 부동산 소재지 관할 법원으로 한다.",
        "제8조 (공증) 본 합의서는 공증사무소에서 인증함으로써 집행권원의 효력을 가진다.",
    ]
    for c in clauses:
        add_paragraph(doc, c, size=11, space_after=10)

    add_paragraph(doc, "")
    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  갑: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, f"  을: {params['occupant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)

    add_warning_footer(doc)
    return doc


def gen_isabi_yeongsujeung(params: dict) -> Document:
    """04b. 이사비 영수증"""
    doc = setup_document()
    add_title(doc, "영 수 증")
    add_paragraph(doc, "")
    add_paragraph(doc, f"금 액: 금 {params.get('isabi', '_____')}원", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "")
    add_paragraph(
        doc,
        f"위 금액을 {params['court_name']} {params['case_no']} 부동산경매 사건의 매각 부동산 "
        f"(소재지: {params.get('property_short_addr', params['property_description'])})의 명도에 따른 "
        "이사비로 정히 영수함.",
        size=11,
    )
    add_paragraph(doc, "")
    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  영수인: {params['occupant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)

    add_warning_footer(doc)
    return doc


def gen_gangje_jiphaeng_sincheong(params: dict) -> Document:
    """05. 강제집행신청서 (인도명령 확정 후)"""
    doc = setup_document()
    add_title(doc, "부동산 인도 강제집행 신청서")

    add_paragraph(doc, f"채권자(매수인): {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"채무자(점유자): {params['occupant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"집행권원: {params['court_name']} {params['case_no']} 부동산인도명령 결정", bold=True, size=11)
    add_paragraph(
        doc,
        f"  결정일자: {params.get('indo_decision_date', '_____')}\n"
        f"  확정일자: {params.get('indo_confirm_date', '_____')}",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "신청취지")
    add_paragraph(
        doc,
        "  채권자의 채무자에 대한 위 집행권원에 기하여 별지 목록 기재 부동산에 대한 "
        "인도 강제집행을 실시하여 주시기 바랍니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "첨부서류")
    for a in [
        "1. 인도명령 결정 정본 1부",
        "2. 송달증명서 1부",
        "3. 확정증명서 1부",
        "4. 부동산등기부등본 1부",
        "5. 채권자 신분증(법인등기부등본) 사본 1부",
    ]:
        add_paragraph(doc, f"  {a}", size=11, space_after=2)

    add_paragraph(doc, "")
    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  채권자: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"{params['execution_office']} 귀중", bold=True, size=12)

    doc.add_page_break()
    add_h2(doc, "[별지] 부동산의 표시")
    add_paragraph(doc, params["property_description"], size=11)

    add_warning_footer(doc)
    return doc


def gen_myeongdo_sojang(params: dict) -> Document:
    """06. 건물명도소송 소장 (시나리오 C)"""
    doc = setup_document()
    add_title(doc, "소     장")

    add_paragraph(doc, f"원고: {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"피고: {params['occupant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, "사건명: 건물명도등 청구의 소", bold=True, size=12)
    add_paragraph(doc, f"소가: 금 {params.get('lawsuit_value', '_____')}원", size=11)
    add_paragraph(doc, "")

    add_h2(doc, "청구취지")
    add_paragraph(
        doc,
        "1. 피고는 원고에게 별지 목록 기재 부동산을 인도하라.\n"
        f"2. 피고는 원고에게 {params.get('possession_start_date', '소유권 취득일')}부터 "
        f"위 부동산 인도 완료일까지 매월 금 {params.get('monthly_unfair_gain', '_____')}원의 비율에 의한 "
        "금원을 지급하라.\n"
        "3. 소송비용은 피고가 부담한다.\n"
        "4. 제1, 2항은 가집행할 수 있다.\n"
        "라는 판결을 구합니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "청구원인")
    add_paragraph(
        doc,
        f"1. 원고는 {params['court_name']} {params['case_no']} 부동산경매 사건의 매각절차에서 "
        f"별지 목록 기재 부동산을 매수하여 {params.get('payment_date', '_____')} 매각대금을 완납하고 "
        "소유권을 취득하였습니다.\n\n"
        "2. 피고는 위 부동산을 임차하여 점유하고 있으나, 그 임대차계약은 원고가 매수하기 전 이미 "
        "기간이 만료되었거나 또는 원고가 임대차계약의 갱신·승계를 원하지 아니하므로 점유할 권원이 "
        "없습니다. (※ 사실관계에 따라 수정 필요)\n\n"
        "3. 또한 피고는 원고가 소유권을 취득한 이후에도 본 부동산을 무단 점유함으로써 원고에게 "
        f"매월 금 {params.get('monthly_unfair_gain', '_____')}원 상당의 차임 상당 부당이득을 얻고 "
        "이로 인하여 원고에게 동액 상당의 손해를 가하고 있습니다.\n\n"
        "4. 따라서 원고는 피고에 대하여 별지 목록 기재 부동산의 인도와 차임 상당 부당이득의 반환을 "
        "구하기 위하여 본 소송에 이른 것입니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "입증방법")
    for a in [
        "갑 제1호증: 매각허가결정 정본",
        "갑 제2호증: 매각대금완납증명",
        "갑 제3호증: 부동산등기부등본",
        "갑 제4호증: 임대차계약서 사본 (해당 시)",
        "갑 제5호증: 감정평가서(차임 상당액 입증)",
    ]:
        add_paragraph(doc, f"  {a}", size=11, space_after=2)
    add_paragraph(doc, "")

    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  원고: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"{params['court_name']} 귀중", bold=True, size=12)

    doc.add_page_break()
    add_h2(doc, "[별지] 부동산의 표시")
    add_paragraph(doc, params["property_description"], size=11)

    add_warning_footer(doc)
    return doc


def gen_budangidet_banhwan(params: dict) -> Document:
    """07. 부당이득반환청구 소장"""
    doc = setup_document()
    add_title(doc, "소     장")

    add_paragraph(doc, f"원고: {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"피고: {params['occupant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, "사건명: 부당이득금반환 청구의 소", bold=True, size=12)
    add_paragraph(doc, f"소가: 금 {params.get('lawsuit_value', '_____')}원", size=11)
    add_paragraph(doc, "")

    add_h2(doc, "청구취지")
    add_paragraph(
        doc,
        f"1. 피고는 원고에게 금 {params.get('claim_amount', '_____')}원 및 이에 대하여 "
        f"이 사건 소장 부본 송달일 다음 날부터 다 갚는 날까지 연 12%의 비율에 의한 금원을 지급하라.\n"
        "2. 소송비용은 피고가 부담한다.\n"
        "3. 제1항은 가집행할 수 있다.\n"
        "라는 판결을 구합니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "청구원인")
    add_paragraph(
        doc,
        f"1. 원고는 {params['court_name']} {params['case_no']} 부동산경매 사건에서 별지 목록 기재 "
        f"부동산을 매수하여 {params.get('payment_date', '_____')} 매각대금을 완납하고 소유권을 취득하였습니다.\n\n"
        f"2. 피고는 위 부동산을 {params.get('possession_start_date', '_____')}부터 "
        f"{params.get('possession_end_date', '인도 완료일')}까지 정당한 권원 없이 점유함으로써 "
        f"매월 금 {params.get('monthly_unfair_gain', '_____')}원의 차임 상당 이익을 얻고 원고에게 "
        "동액 상당의 손해를 가하였습니다.\n\n"
        f"3. 따라서 피고는 원고에게 위 점유 기간에 해당하는 부당이득금 합계 "
        f"금 {params.get('claim_amount', '_____')}원을 반환할 의무가 있습니다.\n\n"
        "4. 이에 본 소송에 이른 것입니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "입증방법")
    for a in [
        "갑 제1호증: 매각대금완납증명",
        "갑 제2호증: 부동산등기부등본",
        "갑 제3호증: 감정평가서(차임 상당액 입증)",
        "갑 제4호증: 점유 사실 입증자료",
    ]:
        add_paragraph(doc, f"  {a}", size=11, space_after=2)
    add_paragraph(doc, "")

    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  원고: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"{params['court_name']} 귀중", bold=True, size=12)

    doc.add_page_break()
    add_h2(doc, "[별지] 부동산의 표시")
    add_paragraph(doc, params["property_description"], size=11)

    add_warning_footer(doc)
    return doc


def gen_yuchikwon_bujeonjae(params: dict) -> Document:
    """08. 유치권 부존재확인 소장 (시나리오 E)"""
    doc = setup_document()
    add_title(doc, "소     장")

    add_paragraph(doc, f"원고: {params['applicant_name']}", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['applicant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"피고: {params['occupant_name']} (유치권 신고자)", bold=True, size=11)
    add_paragraph(doc, f"  주소: {params['occupant_addr']}", size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, "사건명: 유치권 부존재확인 청구의 소", bold=True, size=12)
    add_paragraph(doc, f"소가: 금 {params.get('lawsuit_value', '_____')}원 (유치권 주장 채권액 기준)", size=11)
    add_paragraph(doc, "")

    add_h2(doc, "청구취지")
    add_paragraph(
        doc,
        "1. 별지 목록 기재 부동산에 대한 피고의 유치권은 존재하지 아니함을 확인한다.\n"
        "2. 소송비용은 피고가 부담한다.\n"
        "라는 판결을 구합니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "청구원인")
    add_paragraph(
        doc,
        f"1. 원고는 {params['court_name']} {params['case_no']} 부동산경매 사건에서 별지 목록 기재 "
        f"부동산을 매수하여 {params.get('payment_date', '_____')} 매각대금을 완납하고 소유권을 취득하였습니다.\n\n"
        f"2. 피고는 위 사건의 매각절차에서 금 {params.get('claimed_yuchikwon', '_____')}원의 채권을 "
        "근거로 유치권을 신고하였으나, 다음과 같은 사유로 그 유치권은 인정될 수 없습니다.\n\n"
        "  가. 점유의 부존재 또는 불법성\n"
        f"     {params.get('reason_possession', '※ 사실관계에 맞게 기재. 예: 경매개시결정 기입등기 후 점유 시작, 점유의 객관적 증거 부존재 등')}\n\n"
        "  나. 채권과 목적물의 견련성 부존재\n"
        f"     {params.get('reason_link', '※ 예: 주장 채권은 본 부동산의 보존·개량을 위한 비용이 아님')}\n\n"
        "  다. 유치권 배제 특약 또는 변제기 미도래\n"
        f"     {params.get('reason_other', '※ 사실관계에 따라 추가 기재')}\n\n"
        "3. 따라서 피고가 주장하는 유치권은 존재하지 아니하므로 본 청구에 이른 것입니다.",
        size=11,
    )
    add_paragraph(doc, "")

    add_h2(doc, "입증방법")
    for a in [
        "갑 제1호증: 매각대금완납증명",
        "갑 제2호증: 부동산등기부등본",
        "갑 제3호증: 매각물건명세서 (유치권 신고 기재)",
        "갑 제4호증: 점유 부존재 입증자료(현장 사진, 주민등록 사실조사 등)",
        "갑 제5호증: 채권 부존재·견련성 부존재 입증자료",
    ]:
        add_paragraph(doc, f"  {a}", size=11, space_after=2)
    add_paragraph(doc, "")

    add_paragraph(doc, f"  {params.get('filing_date', date.today().strftime('%Y. %m. %d.'))}", align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"  원고: {params['applicant_name']}    (인)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=11)
    add_paragraph(doc, "")
    add_paragraph(doc, f"{params['court_name']} 귀중", bold=True, size=12)

    doc.add_page_break()
    add_h2(doc, "[별지] 부동산의 표시")
    add_paragraph(doc, params["property_description"], size=11)

    add_warning_footer(doc)
    return doc


# ========== 시나리오별 매핑 ==========

DOC_GENERATORS = {
    "indo_myeongryeong": ("01_부동산인도명령신청서", gen_indo_myeongryeong),
    "naeyong_jeungmyeong": ("03_내용증명_1차명도요청", gen_naeyong_jeungmyeong),
    "myeongdo_hapuiseo": ("04_명도합의서", gen_myeongdo_hapuiseo),
    "isabi_yeongsujeung": ("04b_이사비영수증", gen_isabi_yeongsujeung),
    "gangje_jiphaeng": ("05_강제집행신청서", gen_gangje_jiphaeng_sincheong),
    "myeongdo_sojang": ("06_건물명도소송_소장", gen_myeongdo_sojang),
    "budangidet_banhwan": ("07_부당이득반환청구_소장", gen_budangidet_banhwan),
    "yuchikwon_bujeonjae": ("08_유치권부존재확인_소장", gen_yuchikwon_bujeonjae),
}

SCENARIO_DOCS = {
    "A": ["indo_myeongryeong", "naeyong_jeungmyeong", "gangje_jiphaeng"],
    "B": ["myeongdo_hapuiseo", "isabi_yeongsujeung", "indo_myeongryeong"],  # 인도명령은 보험용
    "C": ["myeongdo_sojang", "budangidet_banhwan"],
    "D": ["indo_myeongryeong", "naeyong_jeungmyeong", "gangje_jiphaeng"],  # 배당받은 임차인용 변형
    "E": ["yuchikwon_bujeonjae", "indo_myeongryeong"],  # 승소 후 인도명령
}


def main():
    parser = argparse.ArgumentParser(description="명도 절차 문서 자동 생성기")
    parser.add_argument("--doc-type", choices=list(DOC_GENERATORS.keys()),
                        help="단일 문서 생성 시 사용. scenario와 택일.")
    parser.add_argument("--scenario", choices=list(SCENARIO_DOCS.keys()),
                        help="시나리오 단위 일괄 생성 시 사용.")
    parser.add_argument("--params", required=True, help="JSON 입력 파일 경로")
    parser.add_argument("--output", help="단일 문서 출력 경로 (--doc-type용)")
    parser.add_argument("--output-dir", help="시나리오 일괄 생성 출력 디렉토리 (--scenario용)")
    args = parser.parse_args()

    with open(args.params, "r", encoding="utf-8") as f:
        params = json.load(f)

    if args.doc_type:
        if not args.output:
            print("❌ --doc-type 사용 시 --output 필요", file=sys.stderr)
            sys.exit(1)
        _, generator = DOC_GENERATORS[args.doc_type]
        doc = generator(params)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(out_path)
        print(f"✅ 생성 완료: {out_path}")
    elif args.scenario:
        if not args.output_dir:
            print("❌ --scenario 사용 시 --output-dir 필요", file=sys.stderr)
            sys.exit(1)
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        params["scenario"] = args.scenario
        for doc_type in SCENARIO_DOCS[args.scenario]:
            filename, generator = DOC_GENERATORS[doc_type]
            case_prefix = params.get("case_no", "사건").replace(" ", "")
            full_name = f"{case_prefix}_{filename}.docx"
            doc = generator(params)
            out_path = out_dir / full_name
            doc.save(out_path)
            print(f"✅ {out_path.name}")
        print(f"\n총 {len(SCENARIO_DOCS[args.scenario])}개 문서 생성됨: {out_dir}")
    else:
        print("❌ --doc-type 또는 --scenario 중 하나 필요", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
