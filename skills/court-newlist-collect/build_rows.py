# -*- coding: utf-8 -*-
"""
court-newlist-collect / build_rows.py
법원경매정보 원본 JSON(collect.js [D] 산출물) → 02단원 신건레이더 원자료 CSV

  python build_rows.py court_newlist_raw_20260930.json --out court_newlist_20260930.csv \
      [--usage 전체|주거|업무상업|토지] [--master "{작업폴더}/_기록/_마스터_신건.csv"] [--exclude-known]

규칙 출처
- 물건 묶기·시도 판정      : 09단원 3절 (2026-09-29 실측 [확정])
- 용도 코드표·용도군 분류  : 09단원 5-1절 (2026-09-30 물건상세검색 콤보박스 실측 [확정])
- 열 구성·구간 라벨·신규 키 : 02단원 3절 [1]·[3]·[2-1] 을 그대로 따른다 (여기서 다시 정하지 않는다)
- 금액                      : 원 단위 정수. 축약 금지.

--usage (기본 전체)
  전체     주거 + 업무상업 + 산업·복합 + 토지 (차량·운송장비 40000·30000 은 항상 제외)
  주거     아파트 · 다세대·연립 · 단독·다가구 · 오피스텔(주거) · 주상복합 · 기숙사
  업무상업 02단원과 같은 범위 (근린주택 · 업무시설 · 집합상가 · 근린상가 · 오피스텔(업무) · 기타상업)
  토지     건물 목록이 없는 토지만 (지목이 용도가 된다)

출력 열 (02단원 3절 [1] 12열 + 슬라이서용 3열 + 구간 3열 + 신규 1열)
  사건번호, 법원, 매각기일, 소재지, 용도, 감정가, 최저가, 최저가율, 건물면적, 토지면적, 조회수, 비고,
  시도, 시군구, 용도군, 감정가 규모대, 남은 날, 조회수 구간, 신규
"""
import argparse, csv, json, re, sys
from collections import defaultdict
from datetime import date, datetime

# ── 3-2절 법원 약칭 (지지옥션 표기와 같음) ─────────────────────────────
COURT_SHORT = {
    "서울중앙지방법원": "중앙", "서울동부지방법원": "동부", "서울서부지방법원": "서부",
    "서울남부지방법원": "남부", "서울북부지방법원": "북부", "의정부지방법원": "의정부",
    "고양지원": "고양", "남양주지원": "남양주", "부천지원": "부천", "수원지방법원": "수원",
    "성남지원": "성남", "여주지원": "여주", "평택지원": "평택", "안산지원": "안산", "안양지원": "안양",
}

# ── 09단원 5-1절 용도 소분류 코드 [확정 — 2026-09-30 물건상세검색 콤보박스 실측] ──
SCLS_NAME = {  # 주거용건물 20100
    "20101":"단독주택","20102":"다가구주택","20103":"다중주택","20104":"아파트","20105":"연립주택",
    "20106":"다세대주택","20107":"기숙사","20108":"빌라","20109":"상가주택","20110":"오피스텔","20111":"주상복합",
    # 상업용및업무용 21100
    "21101":"근린생활시설","21102":"문화및집회시설","21103":"종교시설","21104":"판매시설","21105":"운수시설",
    "21106":"의료시설","21107":"교육연구시설","21108":"노유자시설","21109":"수련시설","21110":"운동시설",
    "21111":"업무시설","21112":"숙박시설","21113":"위락시설","21114":"교정및군사시설","21115":"방송통신시설",
    "21116":"발전시설","21117":"묘지관련시설","21118":"관광휴게시설",
    # 산업용및기타특수용 22100
    "22101":"공장","22102":"창고시설","22103":"위험물저장및처리시설","22104":"자동차관련시설",
    "22105":"동물및식물관련시설","22106":"분뇨및쓰레기처리시설",
    # 용도복합용 23100
    "23101":"주/상용건물","23102":"주/산용건물","23103":"기타복합용건물",
}
JIMOK = {  # 토지 지목 10100
    "10101":"전","10102":"답","10103":"과수원","10104":"목장용지","10105":"임야","10106":"광천지","10107":"염전",
    "10108":"대지","10109":"공장용지","10110":"학교용지","10111":"주차장","10112":"주유소용지","10113":"창고용지",
    "10114":"도로","10115":"철도용지","10116":"제방","10117":"하천","10118":"구거","10119":"유지","10120":"양어장",
    "10121":"수도용지","10122":"공원","10123":"체육용지","10124":"유원지","10125":"종교용지","10126":"사적지",
    "10127":"묘지","10128":"잡종지",
}
SANGGA_JUTAEK = {"20109", "23101"}   # 상가주택, 주/상용건물 → 근린주택
EOPMU = "21111"                       # 업무시설
PANMAE = "21104"                      # 판매시설
GEUNSAENG = "21101"                   # 근린생활시설
JIPHAP = "03"                         # mokGbncd 집합건물
TOJI = "01"                           # mokGbncd 토지
USAGE_GROUPS = ("전체", "주거", "업무상업", "토지")

def num(s):
    try: return int(str(s).replace(",", "").strip() or 0)
    except ValueError: return 0

def ymd(s):
    s = str(s or "")[:8]
    return datetime.strptime(s, "%Y%m%d").date() if len(s) == 8 and s.isdigit() else None

def first_m2(text):
    m = re.search(r"([\d,]+\.?\d*)\s*㎡", text or "")
    return float(m.group(1).replace(",", "")) if m else 0.0

def sum_floor_m2(text):
    """일반건물: 층별 ㎡ 합계. '연면적제외' 줄과 '(현황 …)' 괄호 안은 뻐다. [확정 — 2026-09-29 실측]"""
    total = 0.0
    for line in (text or "").splitlines():
        if "연면적제외" in line: continue
        line = re.sub(r"\([^)]*현황[^)]*\)", "", line)
        for m in re.finditer(r"([\d,]+\.?\d*)\s*㎡", line):
            total += float(m.group(1).replace(",", ""))
    return round(total, 2)

# ── 02단원 3절 [3] 구간 라벨 — 원문 그대로 ─────────────────────────────
def bin_amount(v):
    if not v: return "⑧ 미상"
    if v < 100_000_000: return "① 100,000,000원 미만"
    if v < 300_000_000: return "② 100,000,000~300,000,000원"
    if v < 500_000_000: return "③ 300,000,000~500,000,000원"
    if v < 1_000_000_000: return "④ 500,000,000~1,000,000,000원"
    if v < 3_000_000_000: return "⑤ 1,000,000,000~3,000,000,000원"
    if v < 5_000_000_000: return "⑥ 3,000,000,000~5,000,000,000원"
    return "⑦ 5,000,000,000원 이상"

def bin_days(d, today):
    if d is None: return "④ 30일 초과"
    n = (d - today).days
    if n <= 7: return "① 7일 이내"
    if n <= 14: return "② 8~14일"
    if n <= 30: return "③ 15~30일"
    return "④ 30일 초과"

def bin_views(v):
    # [확정 — 2026-09-29 실측] 법원경매정보 목록의 inqCnt 는 385건 중 384건이 0 → 한 구간으로만 표시
    return "⓪ 미제공(법원경매정보)"

def classify(items):
    """09단원 5-1절 표. items = 같은 물건의 목록 행들. (용도군, 용도) 또는 None(제외)
    판정 순서: 근린주택 → 업무상업 → 주거 → 산업·복합 → 토지(건물 목록 없음). 차량·기타(30000·40000)는 제외."""
    scls = {str(x.get("sclsUtilCd") or "") for x in items}
    lcls = {str(x.get("lclsUtilCd") or "") for x in items}
    moks = {str(x.get("mokGbncd") or "") for x in items}
    usg = " ".join(str(x.get("dspslUsgNm") or "") for x in items)
    jip = JIPHAP in moks
    # 업무상업 (02단원 범위 그대로)
    if scls & SANGGA_JUTAEK: return ("업무상업", "근린주택")
    if EOPMU in scls:
        only_op = "오피스텔" in usg and not re.search(r"상가|사무|근린|판매", usg)
        if only_op: return ("업무상업", "오피스텔(업무)")
        return ("업무상업", "사무실" if jip else "빌딩")
    if PANMAE in scls: return ("업무상업", "상가" if jip else "대형판매시설")
    if GEUNSAENG in scls: return ("업무상업", "상가") if jip else ("업무상업", "근린시설")
    other_biz = sorted(c for c in scls if c.startswith("211"))
    if other_biz: return ("업무상업", SCLS_NAME.get(other_biz[0], "기타상업"))
    # 주거
    if "20104" in scls: return ("주거", "아파트")
    if scls & {"20105", "20106", "20108"}: return ("주거", "다세대·연립")
    if scls & {"20101", "20102", "20103"}: return ("주거", "단독·다가구")
    if "20110" in scls: return ("주거", "오피스텔(주거)")
    if "20111" in scls: return ("주거", "주상복합")
    if "20107" in scls: return ("주거", "기숙사")
    # 산업·복합
    ind = sorted(c for c in scls if c.startswith("221") or c in ("23102", "23103"))
    if ind: return ("산업복합", SCLS_NAME.get(ind[0], "기타"))
    # 토지 — 건물 목록이 하나도 없을 때만
    if moks and moks <= {TOJI}:
        jm = sorted(JIMOK.get(str(x.get("sclsUtilCd") or ""), "") for x in items)
        jm = [j for j in jm if j]
        return ("토지", jm[0] if len(set(jm)) == 1 else "토지(복수지목)") if jm else ("토지", "토지")
    return None

def usage_ok(group, want):
    if want == "전체": return True
    return group == want

def sido_of(printst):
    s = (printst or "").strip()
    if s.startswith("서울"): return "서울"
    if s.startswith("경기"): return "경기"
    return None

def short_addr(printst):
    s = (printst or "").strip()
    s = s.replace("서울특별시", "서울", 1).replace("경기도", "경기", 1)
    return s

def sgg_of(addr):
    tok = addr.split()
    if len(tok) < 2: return ""
    sgg = tok[1]
    if len(tok) >= 3 and tok[1].endswith("시") and tok[2].endswith("구"):
        sgg = tok[1] + " " + tok[2]
    return sgg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw"); ap.add_argument("--out", required=True)
    ap.add_argument("--master", help="02단원 _기록/_마스터_신건.csv (키 = 법원|사건번호|물건번호)")
    ap.add_argument("--exclude-known", action="store_true", help="마스터에 있는 물건은 출력에서 뻐다")
    ap.add_argument("--today", help="YYYYMMDD (기본 오늘)")
    ap.add_argument("--usage", default="전체", choices=USAGE_GROUPS, help="용도군 (기본 전체)")
    a = ap.parse_args()

    today = ymd(a.today) if a.today else date.today()
    data = json.load(open(a.raw, encoding="utf-8"))
    rows = data["rows"] if isinstance(data, dict) else data

    # 6-1절: (법원, saNo, maemulSer) 로 묶는다. 한 물건이 토지·건물 목록 여러 줄로 온다 [확정 — 2026-09-29 실측]
    groups = defaultdict(list)
    for r in rows: groups[(r.get("__court") or r.get("jiwonNm"), r.get("saNo"), str(r.get("maemulSer")))].append(r)

    known = set()
    if a.master:
        with open(a.master, encoding="utf-8-sig", newline="") as f:
            for line in csv.reader(f):
                if line and line[0] and line[0] != "키": known.add(line[0].strip())

    out, skipped = [], {"유찰": 0, "시도": 0, "용도": 0}
    case_count = defaultdict(int)
    for (court, sano, ser), items in groups.items():
        head = items[0]
        if str(head.get("yuchalCnt")) != "0": skipped["유찰"] += 1; continue
        sido = sido_of(head.get("printSt"))
        if not sido: skipped["시도"] += 1; continue
        cls = classify(items)
        if not cls or not usage_ok(cls[0], a.usage): skipped["용도"] += 1; continue
        case_count[(court, head.get("srnSaNo"))] += 1
        out.append((court, sano, ser, items, sido, cls))

    result = []
    for court, sano, ser, items, sido, (bigcls, usage) in out:
        head = items[0]
        court_s = COURT_SHORT.get(head.get("jiwonNm") or "", court)
        dept = re.sub(r"^경매", "", str(head.get("jpDeptNm") or "").strip())
        case = re.sub(r"타경", "-", str(head.get("srnSaNo") or ""))
        if case_count[(court, head.get("srnSaNo"))] > 1: case += f"[{ser}]"
        addr = short_addr(head.get("printSt"))
        bldg = [x for x in items if str(x.get("mokGbncd")) in ("02", "03")]
        land = [x for x in items if str(x.get("mokGbncd")) == TOJI]
        jip = any(str(x.get("mokGbncd")) == JIPHAP for x in items)
        if jip: b_area = first_m2(bldg[0].get("convAddr") if bldg else "")
        else: b_area = sum(sum_floor_m2(x.get("pjbBuldList") or x.get("convAddr")) for x in bldg)
        l_area = round(sum(first_m2(x.get("convAddr")) for x in land), 2)   # 집합건물 대지권은 목록에 없어 0 [확정 — 2026-09-29 실측]
        gam, low = num(head.get("gamevalAmt")), num(head.get("minmaePrice"))
        mg = ymd(head.get("maeGiil"))
        key = f"{court_s}|{head.get('srnSaNo')}|{ser}"      # 02단원 2-1 신건 키
        is_new = key not in known
        if a.exclude_known and not is_new: continue
        result.append({
            "사건번호": case, "법원": f"{court_s}{dept}" if dept else court_s,
            "매각기일": mg.isoformat() if mg else "", "소재지": addr, "용도": usage,
            "감정가": gam, "최저가": low, "최저가율": round(low / gam * 100, 1) if gam else "",
            "건물면적": b_area, "토지면적": l_area, "조회수": "", "비고": str(head.get("mulBigo") or "").strip(),
            "시도": sido, "시군구": sgg_of(addr), "용도군": bigcls,
            "감정가 규모대": bin_amount(gam), "남은 날": bin_days(mg, today), "조회수 구간": bin_views(None),
            "신규": "신규" if is_new else "기존", "_키": key,
        })

    # 6-3절 정렬: 매각기일 → 서울 먼저 → 법원 → 사건번호
    result.sort(key=lambda r: (r["매각기일"], 0 if r["시도"] == "서울" else 1, r["법원"], r["사건번호"]))
    cols = ["사건번호","법원","매각기일","소재지","용도","감정가","최저가","최저가율","건물면적","토지면적",
            "조회수","비고","시도","시군구","용도군","감정가 규모대","남은 날","조회수 구간","신규"]
    with open(a.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(result)

    bycls = defaultdict(int)
    for r in result: bycls[r["용도군"] + "/" + r["용도"]] += 1
    print(f"원본 행 {len(rows):,} → 물건 {len(groups):,} → 신건·서울경기·{a.usage} {len(result):,}건")
    print(f"제외: 유찰≠0 {skipped['유찰']:,} / 시도 밖 {skipped['시도']:,} / 용도 밖 {skipped['용도']:,}")
    print("용도군/용도:", dict(sorted(bycls.items())), "| 신규:", sum(1 for r in result if r["신규"] == "신규"))
    print("→ 마스터 갱신은 엑셀 검사(02단원 3절 [4])가 끝난 뒤에만 한다. 이 스크립트는 마스터를 쓰지 않는다.")

if __name__ == "__main__":
    main()
