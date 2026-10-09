"""
부동산 세금 계산 엔진 (Real Estate Tax Calculator)
NPL 낙찰 후 회수 시나리오에 적용되는 세금 산정

작성: 2026년 4월
세율 기준: 2026년 1월 법령 기준 (지방세법·종부세법·소득세법·법인세법)

사용법:
    from tax_calculator import calculate_total_tax

    result = calculate_total_tax(
        purchase_price=1_000_000_000,      # 낙찰가 10억
        sale_price=1_200_000_000,          # 매각가 12억
        property_type='house',             # 'house' | 'officetel' | 'commercial' | 'land'
        location='서울특별시 강남구',
        buyer_type='corporation',          # 'individual_1' | 'individual_multi_2' | 'individual_multi_3' | 'corporation'
        holding_months=9,                  # 보유 개월
        area_sqm=84.5,                     # 전용면적 (㎡)
        public_price=None,                 # 실제 공시가격 (모르면 appraisal_price 를 넘긴다)
        appraisal_price=None,              # 감정평가액 — 공시가격 부재 시 × 60% 로 가정
        necessary_expenses=0,              # 필요경비 (명도비·리모델링 등)
        cross_june_1=False,                # 6월 1일 경과 여부
    )
    print(result)
"""

from dataclasses import dataclass, field
from typing import Literal, Optional


# === 조정대상지역 리스트 (간이) ===
ADJUSTMENT_AREAS = {
    '서울특별시': 'all',  # 25개구 전체
    '경기도': [
        '성남시 분당구', '성남시 수정구', '수원시 영통구', '용인시 수지구',
        '안양시 동안구', '과천시', '광명시', '하남시',
        '의왕시', '군포시', '구리시', '고양시 덕양구',
    ],
}


def is_adjustment_area(location: str) -> bool:
    """조정대상지역 판정"""
    if not location:
        return False
    if '서울특별시' in location or '서울 ' in location:
        return True
    if '경기도' in location or '경기 ' in location:
        for area in ADJUSTMENT_AREAS['경기도']:
            if area in location:
                return True
    return False


# === 데이터 클래스 ===

@dataclass
class TaxBreakdown:
    """세목별 세액 분해"""
    acquisition_tax: float = 0           # 취득세
    acquisition_nongtug: float = 0       # 농어촌특별세
    acquisition_education: float = 0     # 지방교육세
    property_tax: float = 0              # 재산세
    property_urban: float = 0            # 도시지역분
    comprehensive_tax: float = 0         # 종합부동산세
    holding_addon: float = 0             # 보유세 부가세 (지방교육세+농특세)
    transfer_tax: float = 0              # 양도소득세 (개인) / 법인세 (법인)
    transfer_addon: float = 0            # 법인세 추가과세 (주택 20% 등)
    local_income_tax: float = 0          # 지방소득세

    @property
    def acquisition_total(self) -> float:
        return self.acquisition_tax + self.acquisition_nongtug + self.acquisition_education

    @property
    def holding_total(self) -> float:
        return self.property_tax + self.property_urban + self.comprehensive_tax + self.holding_addon

    @property
    def transfer_total(self) -> float:
        return self.transfer_tax + self.transfer_addon + self.local_income_tax

    @property
    def grand_total(self) -> float:
        return self.acquisition_total + self.holding_total + self.transfer_total


# === 취득세 계산 ===

def calculate_acquisition_tax(
    price: float,
    property_type: str,
    buyer_type: str,
    is_adj_area: bool,
    area_sqm: Optional[float] = None,
) -> tuple[float, float, float]:
    """
    취득세 + 농특세 + 지방교육세 계산
    반환: (취득세, 농특세, 지방교육세)
    """
    # 법인: 주택은 12% 일괄, 비주택은 4%
    if buyer_type == 'corporation':
        if property_type == 'house':
            rate = 0.12
            # 농특세 12% 중과 시 1.0%
            nongtug_rate = 0.01
            # 지방교육세 0.4%
            education_rate = 0.004
        elif property_type == 'officetel':
            # 오피스텔은 취득세상 비주택 (4%)
            rate = 0.04
            nongtug_rate = 0.002
            education_rate = (0.04 - 0.02) * 0.2  # 0.4%
        elif property_type == 'land':
            rate = 0.04
            nongtug_rate = 0.002
            education_rate = (0.04 - 0.02) * 0.2
        else:  # commercial, factory
            rate = 0.04
            nongtug_rate = 0.002
            education_rate = (0.04 - 0.02) * 0.2

    # 개인
    else:
        if property_type == 'house':
            rate = _individual_house_rate(price, buyer_type, is_adj_area)
            nongtug_rate = _house_nongtug_rate(rate, area_sqm)
            education_rate = _house_education_rate(rate)
        elif property_type == 'officetel':
            rate = 0.04
            nongtug_rate = 0.002
            education_rate = (0.04 - 0.02) * 0.2
        elif property_type == 'land':
            rate = 0.04
            nongtug_rate = 0.002
            education_rate = (0.04 - 0.02) * 0.2
        else:
            rate = 0.04
            nongtug_rate = 0.002
            education_rate = (0.04 - 0.02) * 0.2

    acquisition = price * rate
    nongtug = price * nongtug_rate
    education = price * education_rate

    return acquisition, nongtug, education


def _individual_house_rate(price: float, buyer_type: str, is_adj: bool) -> float:
    """개인 주택 취득세율"""
    if buyer_type == 'individual_1':
        # 1주택: 가액별 누진
        if price <= 600_000_000:
            return 0.01
        elif price <= 900_000_000:
            # 6~9억 누진: (가액 * 2/3억 - 3) * 1/100
            price_eok = price / 100_000_000
            rate = (price_eok * 2/3 - 3) / 100
            return max(0.01, min(0.03, rate))
        else:
            return 0.03

    elif buyer_type == 'individual_multi_2':
        # 2주택
        if is_adj:
            return 0.08
        else:
            # 비조정 2주택은 1주택과 동일
            return _individual_house_rate(price, 'individual_1', False)

    elif buyer_type == 'individual_multi_3':
        # 3주택 이상
        if is_adj:
            return 0.12
        else:
            return 0.08
    return 0.01


def _house_nongtug_rate(tax_rate: float, area_sqm: Optional[float]) -> float:
    """주택 농특세율"""
    # 85㎡ 이하 면제
    if area_sqm is not None and area_sqm <= 85:
        return 0.0
    # 12% 중과
    if tax_rate >= 0.12:
        return 0.01
    # 8% 중과
    if tax_rate >= 0.08:
        return 0.006
    # 일반
    return 0.002


def _house_education_rate(tax_rate: float) -> float:
    """주택 지방교육세율"""
    # 중과 시 0.4% 고정
    if tax_rate >= 0.08:
        return 0.004
    # 일반: 취득세율 × 50% × 20% = 취득세율 × 10%
    return tax_rate * 0.1


# === 보유세 계산 (간이) ===

def calculate_holding_tax(
    public_price: float,
    property_type: str,
    buyer_type: str,
) -> tuple[float, float, float, float]:
    """
    보유세 간이 계산
    반환: (재산세, 도시지역분, 종부세, 부가세)
    """
    if property_type == 'house':
        # 주택 재산세
        taxable = public_price * 0.6  # 공정시장가액비율 60%
        property_tax = _house_property_tax(taxable)
        urban = taxable * 0.0014  # 도시지역분 0.14%

        # 종부세
        if buyer_type == 'corporation':
            # 법인: 공제 없음, 단일세율 (2주택 이하 가정 2.7%)
            compt_taxable = public_price * 0.6
            compt = compt_taxable * 0.027
        elif buyer_type == 'individual_1':
            # 1주택자: 12억 공제
            compt_base = max(0, public_price - 1_200_000_000) * 0.6
            compt = _comprehensive_tax_individual(compt_base, is_3plus=False)
        elif buyer_type == 'individual_multi_2':
            compt_base = max(0, public_price - 900_000_000) * 0.6
            compt = _comprehensive_tax_individual(compt_base, is_3plus=False)
        else:  # multi_3+
            compt_base = max(0, public_price - 900_000_000) * 0.6
            compt = _comprehensive_tax_individual(compt_base, is_3plus=True)

    elif property_type == 'officetel':
        # 주거용 오피스텔은 주택으로 간주 (간이)
        taxable = public_price * 0.6
        property_tax = _house_property_tax(taxable)
        urban = taxable * 0.0014
        compt = 0  # 종부세는 주택 인정 여부에 따라 결정 — 간이 생략

    elif property_type in ('commercial', 'factory'):
        # 건축물: 공정시장가액비율 70%
        taxable = public_price * 0.7
        property_tax = taxable * 0.0025  # 0.25%
        urban = taxable * 0.0014
        compt = 0  # 상가 종부세 없음

    elif property_type == 'land':
        # 토지: 공정시장가액비율 70%, 종합합산 간이 0.3%
        taxable = public_price * 0.7
        property_tax = taxable * 0.003
        urban = 0
        compt = 0  # 토지 종부세는 별도 계산 (나대지 5억 공제 등)

    else:
        return 0, 0, 0, 0

    # 부가세: 재산세 × 20% (지방교육세) + 종부세 × 20% (농특세)
    addon = property_tax * 0.2 + compt * 0.2

    return property_tax, urban, compt, addon


def _house_property_tax(taxable: float) -> float:
    """주택 재산세 (누진)"""
    if taxable <= 60_000_000:
        return taxable * 0.001
    elif taxable <= 150_000_000:
        return taxable * 0.0015 - 30_000
    elif taxable <= 300_000_000:
        return taxable * 0.0025 - 180_000
    else:
        return taxable * 0.004 - 630_000


def _comprehensive_tax_individual(base: float, is_3plus: bool) -> float:
    """개인 종부세 (간이 누진)"""
    if base <= 0:
        return 0

    if is_3plus:
        # 3주택 이상 누진
        brackets = [
            (300_000_000, 0.005, 0),
            (600_000_000, 0.007, 600_000),
            (1_200_000_000, 0.010, 2_400_000),
            (2_500_000_000, 0.020, 14_400_000),
            (5_000_000_000, 0.030, 39_400_000),
            (9_400_000_000, 0.040, 89_400_000),
            (float('inf'), 0.050, 183_400_000),
        ]
    else:
        # 2주택 이하
        brackets = [
            (300_000_000, 0.005, 0),
            (600_000_000, 0.007, 600_000),
            (1_200_000_000, 0.010, 2_400_000),
            (2_500_000_000, 0.013, 6_000_000),
            (5_000_000_000, 0.015, 11_000_000),
            (9_400_000_000, 0.020, 36_000_000),
            (float('inf'), 0.027, 1_045_000_000 / 10),
        ]

    for limit, rate, deduction in brackets:
        if base <= limit:
            return base * rate - deduction
    return 0


# === 양도세 계산 ===

def calculate_transfer_tax(
    sale_price: float,
    purchase_price: float,
    necessary_expenses: float,
    property_type: str,
    buyer_type: str,
    holding_months: int,
    is_adj_area: bool,
    sale_after_may_9_2026: bool = False,
) -> tuple[float, float, float]:
    """
    양도세(개인) 또는 법인세(법인) 계산
    반환: (양도세/법인세, 추가과세, 지방소득세)
    """
    gain = sale_price - purchase_price - necessary_expenses

    if gain <= 0:
        # 손실 매각 — 세금 없음 (법인은 법인세 계산 시 손금산입 가능하나 간이 생략)
        return 0, 0, 0

    # ==== 법인 ====
    if buyer_type == 'corporation':
        # 법인세 기본세율 (과세표준별 누진)
        base_tax = _corporation_base_tax(gain)

        # 추가과세
        addon = 0
        if property_type == 'house':
            # 주택 양도 법인 추가 20%
            addon = gain * 0.2
        elif property_type == 'land':
            # 비사업용 토지 추가 10% (비사업용 판정 전제)
            addon = gain * 0.1
        # 상가·공장은 추가과세 없음

        local = (base_tax + addon) * 0.1
        return base_tax, addon, local

    # ==== 개인 ====
    # 기본공제 250만원
    taxable = max(0, gain - 2_500_000)

    if property_type == 'house' or property_type == 'officetel':
        # 주택 단기 세율
        if holding_months < 12:
            rate = 0.70
            tax = taxable * rate
        elif holding_months < 24:
            rate = 0.60
            tax = taxable * rate
        else:
            # 2년 이상 기본세율
            tax = _individual_progressive_tax(taxable)

        # 다주택 중과 (2026.5.10 이후 + 조정지역)
        if sale_after_may_9_2026 and is_adj_area and 'multi' in buyer_type:
            # 중과세율 적용
            surcharge = 0.20 if buyer_type == 'individual_multi_2' else 0.30
            progressive = _individual_progressive_tax(taxable)
            surcharge_tax = progressive + taxable * surcharge
            tax = max(tax, surcharge_tax)

    elif property_type == 'land' or property_type == 'commercial':
        # 비주택 단기 세율
        if holding_months < 12:
            tax = taxable * 0.50
        elif holding_months < 24:
            tax = taxable * 0.40
        else:
            tax = _individual_progressive_tax(taxable)
    else:
        tax = _individual_progressive_tax(taxable)

    local = tax * 0.1
    return tax, 0, local


def _individual_progressive_tax(taxable: float) -> float:
    """개인 양도세 기본세율 누진"""
    if taxable <= 0:
        return 0
    brackets = [
        (14_000_000, 0.06, 0),
        (50_000_000, 0.15, 1_260_000),
        (88_000_000, 0.24, 5_760_000),
        (150_000_000, 0.35, 15_440_000),
        (300_000_000, 0.38, 19_940_000),
        (500_000_000, 0.40, 25_940_000),
        (1_000_000_000, 0.42, 35_940_000),
        (float('inf'), 0.45, 65_940_000),
    ]
    for limit, rate, deduction in brackets:
        if taxable <= limit:
            return taxable * rate - deduction
    return 0


def _corporation_base_tax(taxable: float) -> float:
    """법인세 기본세율 누진"""
    if taxable <= 0:
        return 0
    if taxable <= 200_000_000:
        return taxable * 0.09
    elif taxable <= 20_000_000_000:
        return taxable * 0.19 - 20_000_000
    elif taxable <= 300_000_000_000:
        return taxable * 0.21 - 420_000_000
    else:
        return taxable * 0.24 - 9_420_000_000


# === 메인 통합 함수 ===

def calculate_total_tax(
    purchase_price: float,
    sale_price: float,
    property_type: Literal['house', 'officetel', 'commercial', 'land', 'factory'],
    location: str = '',
    buyer_type: Literal[
        'individual_1', 'individual_multi_2', 'individual_multi_3', 'corporation'
    ] = 'corporation',
    holding_months: int = 9,
    area_sqm: Optional[float] = None,
    public_price: Optional[float] = None,
    appraisal_price: Optional[float] = None,   # 폐기(2026-08-27). 넘기면 ValueError
    necessary_expenses: float = 0,
    cross_june_1: bool = False,
    sale_after_may_9_2026: bool = False,
) -> dict:
    """
    NPL 낙찰 후 매각 시나리오 전체 세금 계산
    """
    # ===== 공시가격 게이트 (2026-08-27 신설) =====
    # 이 함수는 공시가격을 스스로 만들어 내지 않는다.
    # 종전 두 폴백 — purchase_price * 0.7 (2026-08-26 폐기) 과
    # appraisal_price * 0.6 (2026-08-27 폐기) — 은 오류 없이 조용히 적용돼
    # 「조회를 건너뛴 사실」이 결과 어디에도 남지 않았다. 그래서 전부 예외로 바꾼다.
    if appraisal_price is not None:
        raise ValueError(
            "appraisal_price 인자는 2026-08-27 폐기됐습니다.\n"
            "  이 인자를 받으면 내부에서 감정평가액 × 0.6 을 조용히 만들어 써서, "
            "공시가격을 조회하지 않은 사실이 결과에 남지 않습니다.\n"
            "  먼저 조회하십시오 — 공동주택은 duckdb 주택공시가격, 단독·다가구·근린주택은 "
            "https://www.realtyprice.kr/notice/hpindividual/search.htm\n"
            "  조회에 실패한 경우에만 호출부에서 public_price = 감정평가액 * 0.6 을 "
            "직접 계산해 넘기고, 시도 사실과 실패 사유를 산출물에 적으십시오."
        )

    if public_price is not None and not public_price > 0:
        raise ValueError(
            f"public_price 가 유효하지 않습니다: {public_price!r}. "
            "0 이나 음수는 공시가격이 될 수 없습니다."
        )

    if public_price is None and cross_june_1:
        raise ValueError(
            "공시가격을 확정할 수 없어 보유세를 계산할 수 없습니다.\n"
            "  public_price 에 조회한 실제 공시가격을 넘기십시오.\n"
            "  공동주택            → duckdb 주택공시가격 테이블\n"
            "  단독·다가구·근린주택 → https://www.realtyprice.kr/notice/hpindividual/search.htm\n"
            "  낙찰가에서 공시가격을 추정하는 방식은 2026-08-26 폐기됐습니다 — "
            "회차마다 보유세가 달라지는 오류가 납니다."
        )
    # cross_june_1=False 면 보유세를 계산하지 않으므로 공시가격이 쓰이지 않는다.
    # 여기서 임의의 숫자를 넣으면 리포트에 근거 없는 값이 찍히므로 None 으로 둔다.

    is_adj = is_adjustment_area(location)

    # === 1. 취득 단계 ===
    acq_tax, acq_nongtug, acq_edu = calculate_acquisition_tax(
        purchase_price, property_type, buyer_type, is_adj, area_sqm
    )
    acquisition_total = acq_tax + acq_nongtug + acq_edu

    # === 2. 보유 단계 (6월 1일 경과 시만) ===
    if cross_june_1:
        prop, urban, compt, holding_addon = calculate_holding_tax(
            public_price, property_type, buyer_type
        )
    else:
        prop = urban = compt = holding_addon = 0

    holding_total = prop + urban + compt + holding_addon

    # === 3. 양도 단계 ===
    # 필요경비에 취득세 합산 (세법상 취득부대비용)
    total_necessary = necessary_expenses + acquisition_total

    transfer_tax, transfer_addon, local_income = calculate_transfer_tax(
        sale_price,
        purchase_price,
        total_necessary,
        property_type,
        buyer_type,
        holding_months,
        is_adj,
        sale_after_may_9_2026,
    )
    transfer_total = transfer_tax + transfer_addon + local_income

    # === 4. 세전·세후 순회수액 ===
    gross_gain = sale_price - purchase_price
    total_tax = acquisition_total + holding_total + transfer_total
    net_gain = gross_gain - total_tax

    # === 5. IRR (연환산 간이) ===
    if holding_months > 0:
        gross_return = (sale_price / purchase_price) ** (12 / holding_months) - 1
        net_cash_flow = sale_price - total_tax
        net_return = (net_cash_flow / purchase_price) ** (12 / holding_months) - 1
    else:
        gross_return = 0
        net_return = 0

    return {
        '입력조건': {
            '낙찰가': purchase_price,
            '매각예상가': sale_price,
            '부동산유형': property_type,
            '소재지': location,
            '조정대상지역': is_adj,
            '매입주체': buyer_type,
            '보유개월': holding_months,
            '전용면적': area_sqm,
            '공시가격': public_price if public_price is not None else '미확정(보유세 미계산)',
            '6월1일경과': cross_june_1,
            '2026.5.10이후양도': sale_after_may_9_2026,
        },
        '취득단계': {
            '취득세': round(acq_tax),
            '농어촌특별세': round(acq_nongtug),
            '지방교육세': round(acq_edu),
            '소계': round(acquisition_total),
            '실효세율(%)': round(acquisition_total / purchase_price * 100, 2),
        },
        '보유단계': {
            '재산세': round(prop),
            '도시지역분': round(urban),
            '종합부동산세': round(compt),
            '부가세': round(holding_addon),
            '소계': round(holding_total),
        },
        '양도단계': {
            '양도차익(세전)': round(gross_gain),
            '필요경비합산': round(total_necessary),
            '양도세/법인세': round(transfer_tax),
            '추가과세(주택법인20%등)': round(transfer_addon),
            '지방소득세': round(local_income),
            '소계': round(transfer_total),
        },
        '종합': {
            '세전순이익': round(gross_gain),
            '총세금': round(total_tax),
            '세후순이익': round(net_gain),
            '세금비율(세전순이익대비%)': round(total_tax / gross_gain * 100, 2) if gross_gain > 0 else 0,
            '세전IRR(연환산%)': round(gross_return * 100, 2),
            '세후IRR(연환산%)': round(net_return * 100, 2),
            'IRR차이(%p)': round((gross_return - net_return) * 100, 2),
        },
    }


# === 포맷 출력 함수 ===

def format_kor(amount: float) -> str:
    """한국 원화 억·만원 병기"""
    if amount == 0:
        return '0원'
    sign = '-' if amount < 0 else ''
    a = abs(amount)
    eok = int(a // 100_000_000)
    man = int((a % 100_000_000) // 10_000)
    if eok > 0 and man > 0:
        return f'{sign}{a:,.0f}원 (약 {eok}억 {man:,}만원)'
    elif eok > 0:
        return f'{sign}{a:,.0f}원 (약 {eok}억원)'
    else:
        return f'{sign}{a:,.0f}원 (약 {man:,}만원)'


def print_report(result: dict):
    """결과 리포트 출력"""
    print('=' * 70)
    print('NPL 낙찰 후 세금 시뮬레이션 리포트')
    print('=' * 70)

    i = result['입력조건']
    print('\n[입력 조건]')
    print(f"  낙찰가: {format_kor(i['낙찰가'])}")
    print(f"  매각예상가: {format_kor(i['매각예상가'])}")
    print(f"  부동산유형: {i['부동산유형']}")
    print(f"  소재지: {i['소재지']} (조정대상지역: {'YES' if i['조정대상지역'] else 'NO'})")
    print(f"  매입주체: {i['매입주체']}")
    print(f"  보유개월: {i['보유개월']}개월")

    a = result['취득단계']
    print('\n[취득 단계]')
    print(f"  취득세: {format_kor(a['취득세'])}")
    print(f"  농어촌특별세: {format_kor(a['농어촌특별세'])}")
    print(f"  지방교육세: {format_kor(a['지방교육세'])}")
    print(f"  소계: {format_kor(a['소계'])} (실효세율 {a['실효세율(%)']}%)")

    h = result['보유단계']
    print('\n[보유 단계]')
    print(f"  재산세: {format_kor(h['재산세'])}")
    print(f"  종합부동산세: {format_kor(h['종합부동산세'])}")
    print(f"  소계: {format_kor(h['소계'])}")

    t = result['양도단계']
    print('\n[양도 단계]')
    print(f"  양도차익(세전): {format_kor(t['양도차익(세전)'])}")
    print(f"  양도세/법인세: {format_kor(t['양도세/법인세'])}")
    print(f"  추가과세: {format_kor(t['추가과세(주택법인20%등)'])}")
    print(f"  지방소득세: {format_kor(t['지방소득세'])}")
    print(f"  소계: {format_kor(t['소계'])}")

    s = result['종합']
    print('\n[종합]')
    print(f"  세전 순이익: {format_kor(s['세전순이익'])}")
    print(f"  총 세금: {format_kor(s['총세금'])}")
    print(f"  세후 순이익: {format_kor(s['세후순이익'])}")
    print(f"  세전 IRR(연환산): {s['세전IRR(연환산%)']}%")
    print(f"  세후 IRR(연환산): {s['세후IRR(연환산%)']}%")
    print(f"  IRR 차이: {s['IRR차이(%p)']}%p")
    print('=' * 70)


# === 테스트 ===

if __name__ == '__main__':
    # 테스트 1: 법인이 서울 주택 10억 낙찰 후 9개월 뒤 12억 매각
    print('\n### 테스트 1: 법인 / 서울 주택 / 10억 낙찰 → 12억 매각 (9개월) ###')
    r1 = calculate_total_tax(
        purchase_price=1_000_000_000,
        sale_price=1_200_000_000,
        property_type='house',
        location='서울특별시 강남구',
        buyer_type='corporation',
        holding_months=9,
        area_sqm=84.5,
    )
    print_report(r1)

    # 테스트 2: 개인 2주택자가 비조정지역 상가 5억 낙찰 후 6개월 뒤 6억 매각
    print('\n\n### 테스트 2: 개인 2주택 / 비조정 상가 / 5억 → 6억 (6개월) ###')
    r2 = calculate_total_tax(
        purchase_price=500_000_000,
        sale_price=600_000_000,
        property_type='commercial',
        location='대전광역시 서구',
        buyer_type='individual_multi_2',
        holding_months=6,
    )
    print_report(r2)

    # 테스트 3: 법인이 토지 3억 낙찰 후 11개월 뒤 3.5억 매각
    print('\n\n### 테스트 3: 법인 / 비사업용 토지 / 3억 → 3.5억 (11개월) ###')
    r3 = calculate_total_tax(
        purchase_price=300_000_000,
        sale_price=350_000_000,
        property_type='land',
        location='경기도 파주시',
        buyer_type='corporation',
        holding_months=11,
    )
    print_report(r3)
