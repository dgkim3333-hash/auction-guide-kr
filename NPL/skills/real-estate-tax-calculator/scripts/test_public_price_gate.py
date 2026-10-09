"""tax_calculator 공시가격 게이트 — 행동 검증 + 변이 검증"""
import importlib.util, sys, pathlib

def load(path):
    spec = importlib.util.spec_from_file_location("tc_"+str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

BASE = dict(purchase_price=1_818_693_534, sale_price=1_900_000_000,
            property_type="house", buyer_type="corporation",
            location="서울 중랑구", holding_months=12)

def run(tc):
    """(차단건수, 통과여부, 보유세) 반환"""
    blocked = 0
    # T1 공시가격 없이 보유세 계산 요구
    try: tc.calculate_total_tax(**BASE, cross_june_1=True)
    except ValueError: blocked += 1
    # T2 appraisal_price 전달
    try: tc.calculate_total_tax(**BASE, cross_june_1=True, appraisal_price=1_517_947_669)
    except ValueError: blocked += 1
    # T3 public_price=0
    try: tc.calculate_total_tax(**BASE, cross_june_1=True, public_price=0)
    except ValueError: blocked += 1
    # T4 실측 공시가격 → 정상 통과 + 보유세가 낙찰가와 무관해야
    a = tc.calculate_total_tax(**BASE, cross_june_1=True, public_price=588_000_000)
    b = tc.calculate_total_tax(**{**BASE, "purchase_price": 1_000_000_000},
                               cross_june_1=True, public_price=588_000_000)
    보유A = a['보유단계']['소계'] if '보유단계' in a else None
    보유B = b['보유단계']['소계'] if '보유단계' in b else None
    return blocked, (보유A is not None and 보유A == 보유B), 보유A

src = pathlib.Path("scripts/tax_calculator.py")
tc = load(str(src))
blocked, 불변, 보유 = run(tc)
print(f"[고친 판] 차단 {blocked}/3   보유세 낙찰가 무관: {불변}   보유세 {보유:,.0f}원" if 보유 else
      f"[고친 판] 차단 {blocked}/3   보유세 낙찰가 무관: {불변}")
ok1 = (blocked == 3 and 불변)
print("  →", "✓ 통과" if ok1 else "✗ 실패")

# ===== 변이 검증: 방어를 되돌리면 테스트가 실패해야 한다 =====
mut = src.read_text(encoding='utf-8').replace(
    '    if appraisal_price is not None:\n        raise ValueError(',
    '    if appraisal_price is not None:\n        public_price = appraisal_price * 0.6\n    if False:\n        raise ValueError(')
mp = pathlib.Path("/tmp/_mutant.py"); mp.write_text(mut, encoding='utf-8')
mblocked, m불변, _ = run(load(str(mp)))
print(f"[변이 판  ] 차단 {mblocked}/3")
ok2 = (mblocked < 3)
print("  →", "✓ 변이가 잡힘 (테스트가 무력하지 않다)" if ok2 else "✗ 변이를 못 잡음 — 테스트가 가짜다")

sys.exit(0 if (ok1 and ok2) else 1)
