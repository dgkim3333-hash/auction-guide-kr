---
name: "ggi-doc-download"
description: "지지옥션(www.ggi.co.kr)에서 경매·예정물건 서류 PDF(등기부 건물·토지, 건축물대장, 감정평가서, 매각물건명세서, 현황조사서 등)를 받아 물건 폴더 01_원본서류에 바로 저장하는 절차. auction-property-card·npl-analysis·ggi-interest-npl-scan으로 지지옥션 물건을 분석하거나 서류를 수집할 때 반드시 함께 사용한다. 트리거: 지지옥션 다운로드, 서류 다 받아서, 등기부 받아줘, 관련 정보 모두 다운로드, 원본서류 저장, 다운로드 폴더에 저장됨, 폴더로 옮겨, file.ggi.co.kr, PDF가 깨졌다, Request Blocked, 166바이트."
---

> **수강생판 안내 (2026-10-02)** — 강사가 실제로 쓰는 스킬을 경로·회사 식별정보만 바꿔 옮긴 것입니다.
> - 작업 루트 `C:\AI\NPL\` · 실거래 창고 `C:\AI\경매창고.duckdb`(03단원) · 회사명·법인번호·연락처는 `[내 회사명]`·`[법인등록번호]`·`[연락처]` 로 비워 두었습니다.
> - `ggi-*`(지지옥션) · `suhyup-*`·`shinhyup-*` · `lender-auction-radar` · `coefficient-*` · `bid-win-curve` · `pipeline-health-check` 와 예약작업은 **유료 사이트 로그인·강사 사내 DB·수집 스크립트가 전제**입니다. 저장소에 함께 올렸지만 그 환경이 없으면 그대로는 돌지 않습니다.
> - `00_시장데이터\` 아래 낙찰 DB·계수이력·수집 스크립트(`calc_coeff.py`·`load_ggi_csv.py` 등)는 강사 사내 자산이라 저장소에 없습니다. 없으면 본문의 **고정 계수표 [추정]** 를 씁니다.

# 지지옥션 서류 PDF → 물건 폴더 저장 절차

지지옥션에서 받은 서류는 **물건 폴더의 `01_원본서류\`에 바로 저장**한다. Downloads에 두고 끝내지 않는다.
분석 스킬(auction-property-card · npl-analysis · ggi-interest-npl-scan)의 서류 수집 단계에서 이 절차를 쓴다.

## 왜 이 스킬이 있나 (2026-09-26 실측, 동부2계 2026타경163)

| 시도 | 결과 |
|---|---|
| 샌드박스 bash `curl`로 file.ggi.co.kr PDF 직접 받기 | **지지옥션이 「400 Request Blocked」 HTML(166바이트)을 돌려줌** → `.pdf` 이름의 깨진 파일이 폴더에 남았고, 삭제 권한이 없어 지우지도 못함 |
| PDF Tools `fetch_pdf_from_url` → OneDrive 물건 폴더 지정 | **거부** — 허용 폴더가 `Documents`·`Downloads`·`Desktop` 뿐 |
| PDF Tools → Downloads 저장 | 성공 |
| Excel VBA `FileCopy`로 Downloads → 물건 폴더 복사 | **자동 권한 분류기가 차단** — 같은 결과를 다른 도구로 우회 시도 금지 |
| 사용자 승인 후 Downloads 폴더를 세션에 연결 → bash `cp` → `cmp` 대조 | 성공 |

## 절차

### 1. PDF 주소 확보 (www 호스트만)
- 상세·뷰어는 `https://www.ggi.co.kr` 만 쓴다(`web.ggi.co.kr`은 무한루프, apex는 502). 예정물건 토큰 절차는 ggi-interest-npl-scan 1-1을 따른다.
- 뷰어 `/detail/scheduled/viewer?...` 에서 「등기 (N)」·「건축물대장」 탭을 누르면 iframe이 `https://file.ggi.co.kr/kyungmae_new/<Dungki_new|Gunmul_New|...>/<법원코드>/<연도>/<파일>.pdf` 를 연다.
- 등기는 드롭다운에서 [건물]·[토지]를 각각 골라 주소를 따로 얻는다.
- 주소는 `new URL(iframe.src)` 의 `origin + pathname` 만 읽는다. **쿼리스트링·토큰은 출력하지 않는다**(도구가 BLOCKED 처리하고, 토큰은 계정 정보다). 쿼리 없이도 PDF가 200으로 온다.

### 2. PDF Tools로 물건 폴더에 직접 저장 (1순위)
```
mcp__PDF_Tools__fetch_pdf_from_url(
  url = <origin+pathname>,
  destination_dir = <물건폴더>\01_원본서류,
  filename = <표준 파일명>)
```
표준 파일명: `등기부_건물_<짧은주소>_<열람일YYYYMMDD>열람.pdf` / `등기부_토지_...` / `건축물대장_<짧은주소>_<발급일>발급.pdf` / `감정평가서_...` / `매각물건명세서_...` / `현황조사서_...`

- **PDF Tools 허용 폴더에 `C:\AI\NPL` 가 추가돼 있으면 여기서 끝난다.** (설정 allowed_directories. 목록은 기본값을 대체하므로 Documents·Downloads·Desktop도 함께 넣어야 한다 — 사용자 설정 사항이며 Claude가 바꾸지 않는다.)

### 3. 2가 「This server is only allowed to access …」로 거부되면
1. 같은 호출을 `destination_dir = %USERPROFILE%\Downloads` 로 다시 한다. 파일명 앞에 `<계><사건번호>_` 를 붙여 구분한다.
2. **대화형 세션**: `mcp__cowork__request_cowork_directory(path="%USERPROFILE%\Downloads")` 로 연결을 요청한다(사용자 승인 팝업). 승인되면 bash에서
   ```
   cp "/sessions/<세션>/mnt/Downloads/<파일>" "<물건폴더 mount 경로>/01_원본서류/<표준 파일명>"
   cmp <원본> <사본> && echo IDENTICAL
   file <사본>      # "PDF document, N pages" 인지 확인
   ```
   세션 mount 경로는 연결 결과 메시지에 나온 경로를 그대로 쓴다.
3. **무인 실행(예약작업)**: 승인 팝업 도구를 부르지 않는다. Downloads에 저장한 파일명·크기·쪽수를 보고에 적고 「01_원본서류로 이동 필요」를 남긴다.

### 4. 하지 않는 것
- 샌드박스 `curl`·`wget`·Python requests로 file.ggi.co.kr 받기 — 차단 HTML이 `.pdf`로 저장된다.
- Excel VBA·PowerShell 등으로 파일 복사 우회 — 권한 분류기 차단 대상.
- 크기·형식 확인 없이 「저장 완료」 보고 — 반드시 `file`(PDF·쪽수)과 `cmp`(원본 일치)로 확인한다. 1KB 미만 `.pdf`는 차단 응답이다.
- 깨진 파일 방치 — 생겼으면 같은 이름의 정상 파일로 덮어쓰거나, 사용자에게 삭제를 요청한다.

### 5. 저장 후
- 내용 판독은 PDF Tools `read_pdf_content`(텍스트 레이어) → 숫자가 비면 `render_pdf_page`로 이미지 판독.
- 물건 폴더에 `지지옥션_수집원문_<YYYYMMDD>.md` 를 남기고 「다운로드 PDF」 목록에 파일명·쪽수·열람/발급일·고유번호를 적는다. 지지옥션 alg AI시세는 적지 않는다.

## 변경 이력
| 날짜 | 내용 |
|---|---|
| 2026-09-26 | 신설 — 동부2계 2026타경163 수집 중 curl 차단·PDF Tools 폴더 제한·VBA 복사 차단을 겪고 Downloads 연결 후 복사로 해결한 절차를 정리 |

