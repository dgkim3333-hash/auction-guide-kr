# 실전 오류 사례집 (Real Cases Reference)

## 사례 1: NO_MANDATORY_REQUEST_PARAMETERS_ERROR 발생

### 상황
관악구 공매 조회 시 필수 파라미터 누락

### 잘못된 호출 (❌)
```python
get_public_auction_items(
    lctn_sdnm="서울특별시",
    lctn_sggnm="관악구",
    num_of_rows=50,
    opbd_dt_end="20260420",
    opbd_dt_start="20260120"
)
```

### 응답
```json
{
  "total_count": 0,
  "items": [],
  "_debug_raw_response": "{\"result\":{\"resultCode\":\"11\",\"resultMsg\":\"NO_MANDATORY_REQUEST_PARAMETERS_ERROR\"}}"
}
```

### 올바른 호출 (✅)
```python
get_public_auction_items(
    cltr_type_cd="0001",                                                    # ← 추가
    prpt_div_cd="0007,0010,0005,0004,0002,0003,0006,0008,0011,0013",       # ← 추가
    lctn_sdnm="서울특별시",
    lctn_sggnm="관악구",
    num_of_rows=50,
    opbd_dt_end="20260420",
    opbd_dt_start="20260120"
)
```

### 교훈
**MCP 도구 정의상 Optional이지만 API는 필수로 요구한다.**

---

## 사례 2: 시행착오로 엉뚱한 파라미터 추가

### 상황 — 하지 말아야 할 행동의 예
오류 메시지 받은 후 임의로 파라미터를 추가하며 반복 시도

### 잘못된 시도들 (❌)
```python
# 시도 1: dsps_mthod_cd 추가
get_public_auction_items(
    lctn_sdnm="서울특별시", lctn_sggnm="관악구",
    dsps_mthod_cd="0001", cltr_type_cd="0001",  # 필수 하나만 추가
    ...
)
# → 여전히 NO_MANDATORY_REQUEST_PARAMETERS_ERROR

# 시도 2: bid_div_cd 추가
get_public_auction_items(
    ..., bid_div_cd="1", ...
)
# → 여전히 오류

# 시도 3: pbct_stat_cd 추가
get_public_auction_items(
    ..., pbct_stat_cd="3", ...
)
# → 여전히 오류
```

### 올바른 대응
**오류 메시지 받는 즉시 체크리스트 확인**:
1. cltr_type_cd 있는가?
2. prpt_div_cd 있는가? (쉼표구분 복수)
3. opbd_dt_start/end 있는가?

이 3개 중 빠진 것을 먼저 추가한다. 다른 파라미터는 건드리지 않는다.

### 교훈
**필수 3종이 아닌 파라미터를 추가하는 것은 해결이 아니다.**

---

## 사례 3: 날짜 포맷 오류

### 잘못된 형식 (❌)
```python
opbd_dt_start="2026-01-20"   # 하이픈 포함
opbd_dt_start="2026/01/20"   # 슬래시 포함
opbd_dt_start="20260120 1100" # 시간 포함
```

### 올바른 형식 (✅)
```python
opbd_dt_start="20260120"     # yyyyMMdd 8자리만
opbd_dt_end="20260420"
```

### 교훈
**응답 필드 cltrOpbdDt는 12자리(시간 포함)이나, 요청 필드는 8자리만.**

---

## 사례 4: 구코드 사용

### 증상
오류는 없으나 `total_count: 0` 허수 응답

### 잘못된 호출 (❌)
```python
get_public_auction_items(
    cltr_type_cd="0001",
    prpt_div_cd="0101",   # ← 구코드
    ...
)
# → total_count: 0, 오류 메시지 없음
```

### 올바른 호출 (✅)
```python
get_public_auction_items(
    cltr_type_cd="0001",
    prpt_div_cd="0007",   # ← v2 신코드 (압류재산)
    # 또는 전체: "0007,0010,0005,0004,0002,0003,0006,0008,0011,0013"
    ...
)
```

### 교훈
**v1 구코드(0101, 0201, 0301)는 영구 삭제되지 않고 남아있으나 데이터를 반환하지 않는다. 디버깅이 어려운 함정.**

---

## 사례 5: 타임아웃 방지

### 증상
```json
{"error": "network_error", "message": "API server timed out (15s)"}
```

### 잘못된 호출 (❌)
```python
# 전국 1년치 조회
get_public_auction_items(
    cltr_type_cd="0001",
    prpt_div_cd="0007,0010,0005,0004,0002,0003,0006,0008,0011,0013",
    opbd_dt_start="20250420",  # 1년 전
    opbd_dt_end="20260420",
    num_of_rows=500  # 너무 많음
)
```

### 올바른 호출 (✅)
```python
# 단계적 축소: 지역 지정 + 3개월로
get_public_auction_items(
    cltr_type_cd="0001",
    prpt_div_cd="0007,0010,0005,0004,0002,0003,0006,0008,0011,0013",
    lctn_sdnm="서울특별시",     # ← 지역 지정
    lctn_sggnm="관악구",        # ← 시/군/구 지정
    opbd_dt_start="20260120",   # ← 3개월
    opbd_dt_end="20260420",
    num_of_rows=50              # ← 적정 수준
)
```

### 교훈
**온비드 API는 응답 크기에 민감. 지역·기간·행수로 점진적 축소.**

---

## 사례 6: 응답 해석 — 유찰 체감률 읽기

### 응답 예시 (봉천동 933-21)
```json
{
  "apslEvlAmt": 379273600,           // 감정가 3.79억
  "lowstBidPrcIndctCont": "75855000", // 최저입찰가 7,585만
  "apslPrcCtrsLowstBidRto": 20,      // 감정가 대비 20%
  "feeRate": 80,                      // 체감률 80%
  "pbctStatNm": "낙찰",
  "scfbAmt": "95610000",              // 낙찰가 9,561만
  "apslPrcCtrsScfbPrcRto": 25.21,    // 낙찰가율 25.21%
  "vldBddrNope": 4                    // 유효입찰자 4명
}
```

### 해석
- **9차례 유찰** 끝에 체감률 80%(최저가가 감정가의 20%)에서 낙찰
- 4명이 경쟁하여 최저가 대비 126% 낙찰 but 감정가 대비는 25.21% 불과
- NPL 관점: 감정가의 15-20% 수준에서 매입해야 수익 가능

---

## 사례 7: 특정 번지 조회 실패 시

### 증상
`lctn_emd_nm="봉천동"` 추가하면 일부 물건이 누락되는 경우 있음

### 원인
봉천동은 법정동은 1개이나 행정동은 11개 (봉천본동, 은천동, 성현동 등)로 매핑 차이 발생 가능

### 대응
1. 1차: `lctn_emd_nm` 지정
2. 누락 의심 시: `lctn_emd_nm` 제거하고 시/군/구만으로 조회
3. 물건명에서 "봉천동" 포함만 필터링

```python
# 1차
items1 = get_public_auction_items(lctn_sggnm="관악구", lctn_emd_nm="봉천동", ...)

# 2차 (보완) — 시/군/구만으로 넓게 조회 후 물건명 필터링
items2 = get_public_auction_items(lctn_sggnm="관악구", ...)
filtered = [x for x in items2['items'] if '봉천동' in x.get('onbidCltrNm', '')]
```

---

## 요약: 체크리스트

호출 직전 반드시 확인:

```
[  ] cltr_type_cd="0001"?
[  ] prpt_div_cd = v2 신코드(쉼표구분)?
[  ] opbd_dt_start/end = yyyyMMdd 8자리?
[  ] 시도명 공식 전체명?
[  ] dsps_mthod_cd, bid_div_cd 등 불필요 파라미터 생략?
[  ] num_of_rows 50 이하?
[  ] 조회 범위(기간+지역) 적정?
```
