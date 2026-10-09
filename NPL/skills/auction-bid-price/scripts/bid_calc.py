#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""경매 입찰가 산정 계산기 (4단계 프로토콜)

사용:
  python3 bid_calc.py --gam 155000000 --cycle 3 --low 53165000 \
      --deal 98000000 --prev 94153000 --drift -0.17 --score 7

계수 수집일: 2026-07-21 / 표본: 수원지법 관할 소형 상업·업무 227개 사건
"""
import argparse, sys, datetime

COLLECTED = datetime.date(2026, 7, 21)

# 유찰회차: (Q1, 중앙값, Q3)  단위 %
CYCLE_RATE = {0:(100,101,111), 1:(76,80,86), 2:(55,62,65),
              3:(35,41,44), 4:(25,28,31), 5:(17,20,21), 6:(12,13,15)}
# 유찰회차: (절편, 기울기, r, 사용가능)
REG = {1:(80.8,0.43,0.128,False), 2:(55.2,1.26,0.568,True),
       3:(36.0,1.93,0.640,True), 4:(25.4,2.06,0.536,True)}

def bidders_from_score(s):
    if s <= 0: return 1
    if s <= 2: return 2
    if s <= 4: return 3
    if s <= 6: return 6
    return 9

def won(n):
    return f"{int(round(n)):,}원"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gam", type=float, required=True, help="감정가(원)")
    p.add_argument("--cycle", type=int, required=True, help="유찰회차 0~6")
    p.add_argument("--low", type=float, required=True, help="최저매각가격(원)")
    p.add_argument("--score", type=int, required=True, help="경쟁강도 순점수")
    p.add_argument("--deal", type=float, default=0, help="인근 실거래가(원). 없으면 0")
    p.add_argument("--prev", type=float, default=0, help="동일건물 직전 낙찰가(원). 없으면 0")
    p.add_argument("--drift", type=float, default=0.0, help="직전낙찰 이후 시장변동률 (-0.17 = 17%% 하락)")
    p.add_argument("--premium", type=float, default=0.012, help="동가경합 방지 프리미엄")
    a = p.parse_args()

    age = (datetime.date.today() - COLLECTED).days
    warn = []
    if age > 365:
        warn.append(f"⚠ 계수가 {age}일 경과. 참고치로만 사용하고 [검증필요] 라벨을 붙일 것.")
    elif age > 182:
        warn.append(f"⚠ 계수가 {age}일 경과. 재수집을 권장합니다.")

    if a.cycle not in CYCLE_RATE:
        sys.exit("유찰회차는 0~6")

    q1, med, q3 = CYCLE_RATE[a.cycle]
    base = a.gam * med / 100
    bidders = bidders_from_score(a.score)

    reg = REG.get(a.cycle)
    if reg and reg[3]:
        icept, slope, r, _ = reg
        rate = icept + slope * min(bidders, 12)
        method = f"회귀식 (절편 {icept} + 기울기 {slope} × 응찰 {bidders}명, r={r})"
    else:
        rate = med
        method = f"중앙값 고정 ({'상관 없음' if a.cycle==1 else '표본 부족'})"
    step2 = a.gam * rate / 100

    caps = {"STEP2 통계기반": step2}
    if a.deal > 0:
        caps["상한A 실거래×80%"] = a.deal * 0.80
    if a.prev > 0:
        caps["상한B 직전낙찰×(1+변동)"] = a.prev * (1 + a.drift)

    binding = min(caps, key=caps.get)
    pre = max(min(caps.values()), a.low)
    final = round(pre * (1 + a.premium) / 1000) * 1000 + 7000

    print("=" * 62)
    print("경매 입찰가 산정 — 4단계 프로토콜")
    print("=" * 62)
    for w in warn: print(w)
    print(f"감정가        {won(a.gam)}")
    print(f"최저매각가격  {won(a.low)}  ({a.low/a.gam*100:.1f}%)")
    print(f"유찰회차      {a.cycle}회   기준 Q1 {q1}% / 중앙 {med}% / Q3 {q3}%")
    print("-" * 62)
    print(f"STEP 1 기준선          {won(base)}   (감정가 × {med}%)")
    print(f"STEP 2 경쟁강도 {a.score:+d}점 → 응찰 {bidders}명 → {rate:.1f}%")
    print(f"       {method}")
    print(f"       통계기반 입찰가 {won(step2)}")
    print("STEP 3 상한 검증")
    for k, v in caps.items():
        mark = " ← 구속" if k == binding else ""
        print(f"       {k:<26} {won(v)}{mark}")
    if pre == a.low:
        print(f"       (최저매각가격이 하한으로 작용)")
    print(f"STEP 4 프리미엄 +{a.premium*100:.1f}% 및 끝자리 조정")
    print("-" * 62)
    print(f"★ 권장 입찰가   {won(final)}")
    print(f"   감정가 대비  {final/a.gam*100:.1f}%")
    print(f"   최저가 대비  {final/a.low*100:.1f}%")
    if a.prev > 0:
        print(f"   직전낙찰 대비 {final/a.prev*100:.1f}%")
    print("=" * 62)
    print("주의: 취득세·체납관리비·명도비를 더한 총투입이 실거래의 80%를 넘지 않는지")
    print("      반드시 별도 확인할 것.")

if __name__ == "__main__":
    main()
