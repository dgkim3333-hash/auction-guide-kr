---
name: "court-case-docs"
description: "법원경매정보(courtauction.go.kr, 무료)에서 사건번호 하나의 서류를 전부 받아 사건 폴더에 정리한다 — 감정평가서 PDF, 매각물건명세서 PDF, 현황조사서(사진 포함) PDF, 사건내역·기일내역·문건/송달내역 PDF(화면 표를 떠서 weasyprint 로 변환). 등기부는 인터넷등기소 링크만 있어 받지 않는다. Claude in Chrome 필요. JS 한 호출 45초 제한 때문에 단계를 쪼개 실행한다. 트리거: 사건 서류 받아줘, 감정평가서 받아줘, 매각물건명세서 PDF, 현황조사서 사진, 문건송달내역 PDF, 법원경매정보에서 서류, 지지옥션 없이 서류, 타경 서류 일괄."
---

# court-case-docs — 사건 서류 일괄 받기 (법원경매정보)

> **수강생판 안내 (2026-09-29)** — 모든 `[확정]` 은 「2026-09-29 Claude in Chrome 세션에서 직접 클릭·다운로드해 확인」이 출처입니다.
> 사이트 화면 요소 id 는 바뀔 수 있습니다. 확신도 라벨은 저장소 공통 4종만 씁니다.
> **받은 서류는 개인 검토용입니다.** 감정평가서는 감정평가법인 저작물이고, 매각물건명세서 파일명에는 참여관 실명이 들어 있습니다. 남에게 나눠 주거나 인터넷에 올리지 마세요.

## 입력 · 출력

| | |
|---|---|
| 입력 | 법원명 + 사건번호 (예: 서울중앙 2024타경00000) |
| 출력 폴더 | `{다운로드}\{사건번호}_{법원}_{소재지 요약}\` |
| 파일 | 감정평가서.pdf · 매각물건명세서.pdf · 현황조사서.pdf(사진 포함) · 현황조사_사진1~N.jpg · 사건내역.pdf · 기일내역.pdf · 문건송달내역.pdf · 사건요약.txt |

`[확정 — 2026-09-29 실측]` 결과: 감정평가서 16쪽 · 매각물건명세서 2쪽 · 현황조사서 5쪽(사진 3장 포함) · 사건내역 2쪽 · 기일내역 1쪽 · 문건송달 4쪽.

## 전제

- 01단원 완료. `chrome://settings/content/automaticDownloads` 「허용됨」에 `https://www.courtauction.go.kr` — **없으면 두 번째 파일부터 조용히 사라진다** `[확정 — 2026-09-29 실측]`
- 서류 공개 시점(사이트 「이용시 유의사항」 원문, 2026-09-29 조회): **매각물건명세서는 매각기일 1주 전부터, 현황조사서·감정평가서는 2주 전부터** 매각기일까지만 조회된다. 그 전에는 버튼이 없다 — 오류가 아니다.
- `pip install weasyprint --break-system-packages` (실측 70.0), 폰트 `Noto Sans CJK KR`

## 어떤 서류가 어떻게 받아지나 `[확정 — 2026-09-29 실측]`

| 서류 | 받는 방법 |
|---|---|
| 감정평가서 | 경매사건검색 → [감정평가서] → 팝업 iframe `sbx_iframeTest` 의 src(`ca.kapanet.or.kr/view/...`)를 새 탭으로 → 그 페이지 안 iframe이 **직접 PDF 주소**(`.../DJ-xxxxxx.pdf`) → 같은 출처에서 fetch → blob 다운로드 |
| 매각물건명세서 | 사건내역 물건내역의 [매각물건명세서] → 새 탭 `ecfs.scourt.go.kr` 문서뷰어 → 하단 **[파일저장]** (좌표 클릭, 스크린샷으로 위치 확인) |
| 현황조사서 | [현황조사서] 팝업(HTML). 탭 2개(현황조사내역·부동산표시목록) + [사진보기] 팝업. 사진은 `img` src 가 base64(`data:image/png` 라고 적혀 있지만 실제 JPEG). 페이지 버튼으로 1~N장 |
| 사건내역 · 기일내역 · 문건/송달내역 | 화면 탭 3개. **PDF 버튼 없음** → 표를 HTML로 떠서 `html_to_pdf.py` 로 A4 PDF |
| 등기부등본 | 사이트는 인터넷등기소 링크만 제공 → **받지 않는다** (유료 발급) |

---

## 절차

한 JS 호출은 **20초 이내**로 쪼걠다. 탭 전환 + 사진 3장 대기(합 24초)를 한 번에 넣었더니 타임아웃이 났다 `[확정 — 2026-09-29 실측]` (스크립트는 뒤에서 끝까지 돌아 파일은 생겼지만 결과를 못 받는다).

### 1. 사건 열기

```
navigate → https://www.courtauction.go.kr/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ159M00.xml   (경매사건검색)
```
법원 선택(기본 서울중앙) · 연도 combobox · 번호 입력 → [검색].

### 2. 탭 3개 텍스트 → HTML 떠내기

| 요소 | id `[확정 — 2026-09-29 실측]` |
|---|---|
| 탭 헤더 | `mf_wfm_mainFrame_tac_srchRsltDvs_tab_tabs{1,2,3}_tabHTML` |
| 탭 본문 | `mf_wfm_mainFrame_tac_srchRsltDvs_contents_content{1,2,3}` |

탭을 클릭한 뒤 **2초 기다리고** 아래 `snap()` 으로 본문을 떠다. 숨겨진 요소를 빼고 복제해야 탭 전환 잔여물이 안 섞인다.

```javascript
function snap(root){
  const hid=[];
  root.querySelectorAll('*').forEach(e=>{
    if(!e.offsetParent && !['TBODY','TR','COLGROUP','COL'].includes(e.tagName)){ e.setAttribute('data-hid','1'); hid.push(e); }
  });
  const c=root.cloneNode(true); hid.forEach(e=>e.removeAttribute('data-hid'));
  c.querySelectorAll('[data-hid],script,style,button,input,select,img,caption').forEach(e=>e.remove());
  c.querySelectorAll('*').forEach(e=>{e.removeAttribute('style');e.removeAttribute('class');});
  return c.innerHTML;
}
// 예: 사건내역
const html = snap(document.getElementById('mf_wfm_mainFrame_tac_srchRsltDvs_contents_content1'));
const blob = new Blob([html], {type:'text/html'}); const a=document.createElement('a');
a.href=URL.createObjectURL(blob); a.download='사건내역.html'; document.body.appendChild(a); a.click(); a.remove();
```

세 탭을 각각 `사건내역.html` · `기일내역.html` · `문건송달내역.html` 로 받는다 (호출 3번).

### 3. 감정평가서

버튼 `title="감정평가서 보기"` → 팝업 iframe `sbx_iframeTest` 의 src 를 읽어 **새 탭**으로 연다 → 그 페이지 안 iframe 의 src 가 PDF 주소 → 같은 출처에서 `fetch` → blob → `감정평가서.pdf` 로 다운로드.

### 4. 현황조사서 + 사진

| 요소 | id / 접두어 `[확정 — 2026-09-29 실측]` |
|---|---|
| 열기 버튼 | `mf_wfm_mainFrame_btn_curstExmndc` |
| 팝업 접두어 | `mf_wfm_mainFrame_curstExmndcPopUp_wframe_` |
| 내부 탭 | `tac_curstExmnRletIndct_tab_tabs{1,2}_tabHTML` |
| 사진 버튼 | `btn_showPicPopUp` → 사진 팝업 접두어 `..._showPicOpenPopUp_wframe_` |
| 사진 페이지 · 이미지 | `pgl_gdsDtlSrchPage_page_{i}` · `img_csPic` |
| 닫기 | `..._showPicOpenPopUp_close` · `mf_wfm_mainFrame_curstExmndcPopUp_close` |

1. 팝업 열고 탭 2개를 `snap()` 으로 떠서 `현황조사서.html` 로
2. 사진 팝업 열고 페이지 1~N 을 넘기며 `img_csPic` 의 src(base64)를 `현황조사_사진{i}.jpg` 로 저장 — **한 호출에 사진 1~2장씩**
3. 팝업 두 개 닫기

> [!WARNING]
> 버튼 텍스트로 찾을 때 `button` 이 아니라 **`input[type=button]`** 인 경우가 있다(현황조사서) `[확정 — 2026-09-29 실측]`. `title` 속성으로 찾는다.

### 5. 매각물건명세서

버튼 「매각물건명세서」 → 새 탭 `ecfs.scourt.go.kr` 문서뷰어 → 하단 **[파일저장]**. 좌표 클릭이므로 **스크린샷으로 버튼 위치를 먼저 확인**한다.
받은 파일명에 **참여관 실명**이 들어 있다 → `매각물건명세서.pdf` 로 바꿔 저장하고 원래 파일명은 어디에도 적지 않는다.

### 6. HTML → PDF

```
python html_to_pdf.py 사건내역.html 사건내역.pdf
python html_to_pdf.py 기일내역.html 기일내역.pdf
python html_to_pdf.py 문건송달내역.html 문건송달내역.pdf
python html_to_pdf.py 현황조사서.html 현황조사서.pdf --images 현황조사_사진1.jpg 현황조사_사진2.jpg 현황조사_사진3.jpg
```

### 7. 확인 · 정리

- 다운로드 폴더에 파일이 **실제로 생겼는지 bash 로 확인**한다. 호출 성공은 증거가 아니다.
- 크기와 `file` 명령으로 PDF/JPEG 인지 확인한다.
- 사건 폴더로 **복사**한다. 다운로드 폴더에서 `mv` 가 `Operation not permitted` 로 막힐 수 있다 `[확정 — 2026-09-29 실측]` → 복사 후 원본은 남기고 보고.
- 자동 다운로드를 나중에 허용하면 **밀린 파일이 한꺼번에 중복으로 떨어진다** (사진2 ×3, 사진3 ×2 발생) → md5 로 중복 정리.
- `사건요약.txt`: 사건번호 · 법원 · 소재지 · 매각기일 · 받은 파일 목록 · 못 받은 서류와 사유.

---

## 안 될 때

| 증상 | 원인 | 해결 |
|---|---|---|
| [감정평가서]·[현황조사서] 버튼이 없다 | 공개 시점 전 (명세서 1주·나머지 2주 전부터) | 정상. 매각기일 2주 안에 다시 |
| 두 번째 파일부터 안 생긴다 | 자동 다운로드 미허용 | 01단원 3단계 |
| JS 타임아웃 | 한 호출 45초 초과 | 20초 이내로 쪼갠다. 파일은 생겼을 수 있으니 폴더 확인 |
| `input[type=button]` 을 못 찾는다 | `button` 으로 검색 | `title` 속성으로 |
| 한글이 □ 로 나온다 | 폰트 없음 | `Noto Sans CJK KR` 설치 확인 |
| 사진이 PNG 가 아니다 | src 표기와 실제가 다름 | 정상. JPEG 로 저장 |

## 하지 않는 것

- 받은 서류를 저장소·단톡방·인터넷에 올리기 — 감정평가서는 감정평가법인 저작물, 명세서 파일명에 실명
- 등기부를 이 경로로 받으려 하기 — 인터넷등기소 별도 발급
- 화면 표 PDF 를 원본처럼 쓰기 — 「화면을 옮긴 것, 원문과 다를 수 있음」 문구가 붙는다. 입찰 전 경매계 재확인
- 특정 물건의 입찰을 권하기

AI 분석은 검토 출발점입니다. 실제 입찰 전 등기부·매각물건명세서 원문과 전문가 확인이 필요합니다.
