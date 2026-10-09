---
name: "ggi-newlist-collect"
description: "지지옥션(ggi.co.kr)에서 서울·경기 업무·상업 용도의 '신건'(유찰 0회, 매각기일 미래)을 브라우저로 수집해 탐색(슬라이서 드릴다운)·원자료·피벗집계·대시보드 4시트 엑셀을 만드는 스킬. 탐색 시트는 excel-explore-sheet 스킬 양식을 그대로 따르며, 슬라이서를 겹쳐 누르면 15행부터 해당 물건만 즉시 펼쳐진다. 산출물 서식은 매 회차 동일해야 하므로 직전 회차 xlsx를 먼저 열어 대조한다. 무인 실행이므로 승인 팝업 도구를 부르지 않고, 파일이 잠기면 닫아달라고 요청하는 대신 _v2 로 저장하고 보고한다. 실패로 산출물을 지울 때는 마스터도 함께 되돌린다 — 엑셀만 지우면 그 물건이 기존으로 묻혀 영영 보고되지 않는다. 사용자가 \"신건 수집\", \"신건 레이더\", \"이번 주 신건\", \"신건 뽑아줘\", \"지지옥션 신건\", \"신건 대시보드\", \"서울 경기 상가 신건\", \"업무상업 신건\", \"신건 엑셀\", \"새로 나온 물건\", \"신규 경매 물건\", \"ggi 신건\", \"신건 갱신\", \"신건 피벗\", \"신건 마스터 대조\", \"신건 탐색 시트\", \"슬라이서로 걸러보게\" 등을 언급하거나 주간 신건 수집 스케줄이 실행될 때 반드시 사용한다. 낙찰결과 수집(ggi-collect)과는 다른 스킬로, 진행 중인 신건 물건 목록 수집 전용이다."
---

> **수강생판 안내 (2026-10-02)** — 강사가 실제로 쓰는 스킬을 경로·회사 식별정보만 바꿔 옮긴 것입니다.
> - 작업 루트 `C:\AI\NPL\` · 실거래 창고 `C:\AI\경매창고.duckdb`(03단원) · 회사명·법인번호·연락처는 `[내 회사명]`·`[법인등록번호]`·`[연락처]` 로 비워 두었습니다.
> - `ggi-*`(지지옥션) · `suhyup-*`·`shinhyup-*` · `lender-auction-radar` · `coefficient-*` · `bid-win-curve` · `pipeline-health-check` 와 예약작업은 **유료 사이트 로그인·강사 사내 DB·수집 스크립트가 전제**입니다. 저장소에 함께 올렸지만 그 환경이 없으면 그대로는 돌지 않습니다.
> - `00_시장데이터\` 아래 낙찰 DB·계수이력·수집 스크립트(`calc_coeff.py`·`load_ggi_csv.py` 등)는 강사 사내 자산이라 저장소에 없습니다. 없으면 본문의 **고정 계수표 [추정]** 를 씁니다.

# 지지옥션 신건 레이더 수집

서울·경기의 **업무·상업 용도 신건**(유찰 0회 + 매각기일 미래)을 수집해
`탐색 / 원자료 / 피벗집계 / 대시보드` **4시트** 엑셀을 만든다.

낙찰결과를 받는 `ggi-collect`와 목적이 다르다. 이 스킬은 **아직 매각 전인 물건**을 본다.

## ★★ 무인 실행 원칙 (2026-09-08 신설)

이 스킬은 **매주 수요일 10:30 무인 예약작업**(`ggi-newlist-wed`)에서 호출되고,
`ggi-running-collect` 도 브라우저 절차를 여기서 가져다 쓴다. 그 회차에는 사람이 없다.

- **승인 팝업을 띄우는 도구를 호출하지 않는다.**
  `mcp__cowork__allow_cowork_file_delete` · `mcp__cowork__request_cowork_directory` · `AskUserQuestion`.
  무인 회차에 부르면 `AbortError: Tool permission stream closed` 로 회차가 통째로 끊긴다
  (2026-09-08 `suhyup-npl-daily-scan` 실사고).
- **사용자에게 파일을 닫아달라고 요청하고 기다리지 않는다.** STEP 8 「파일 교체가 막힐 때」를 따른다.
- **오류로 끊겼다가 「이어서 진행」 신호를 받으면 빈 응답으로 끝내지 않는다.**
  미완료 단계를 찾아 마치고 반드시 보고한다.

## ★ 매 회차 같은 모습이어야 한다

산출물은 주간 반복물이다. **직전 회차 파일을 먼저 열어 서식을 대조한 뒤** 만든다.
스킬에 안 적힌 값(글자 크기·색·행 높이·열 너비·컬럼 순서·문구)을 임의로 정하면
사용자는 "양식이 전부 바뀌었다"고 느낀다. 실측으로 발생했다(2026-09-02).

```python
import openpyxl
wb = openpyxl.load_workbook(직전회차_xlsx)   # 읽기 전용으로만 쓴다
ws = wb['대시보드']
print({k: v.width for k, v in ws.column_dimensions.items() if v.width})
print({k: v.height for k, v in ws.row_dimensions.items() if v.height})
for c in ['B2','B3','B5','B6']:
    print(c, ws[c].font.name, ws[c].font.size, ws[c].font.bold)
```

아래 「확정 서식」 표와 다르면 **직전 회차 쪽이 맞다** — 표를 고치지 말고 사용자에게 알린다.

## 저장 위치

```
C:\AI\NPL\온비드\지지옥션_신건레이더\
```

- 주간 파일: `지지옥션_신건_대시보드_서울경기_YYYYMMDD.xlsx`
- 원본 CSV: `ggi_newlist_YYYYMMDD.csv`
- 마스터: `_마스터_사건번호.csv` (누적 사건번호 목록, 신규 판정용)

## 사전 조건

| 조건 | 확인 방법 |
|---|---|
| 크롬 실행 + Claude in Chrome 활성 | `tabs_context_mcp` 성공 |
| **지지옥션 로그인 세션 유효** | STEP 1에서 반드시 검증 |
| **ggi.co.kr 자동 다운로드 허용** | 아래 "다운로드 차단" 항목 참조 |
| Excel 설치 + 대상 파일 닫혀 있음 | Excel MCP는 COM 독점 접근 필요 |

**로그인이 풀려도 페이지는 정상으로 보이고 검색도 된다. 결과 건수만 조용히 줄어든다.**

### ★ 다운로드 차단 — 가장 흔한 실패

크롬은 같은 사이트에서 **두 번째 자동 다운로드부터 차단**한다. 차단되면
`a.click()`은 성공한 것처럼 보이고 파일만 안 생긴다. 반드시 파일 존재를 확인한다.

해결: `chrome://settings/content/automaticDownloads` 에 `https://www.ggi.co.kr` 허용 추가.

한 회차에 다운로드는 **1회만** 하도록 설계한다. 파서를 고쳐 재수집해야 하면
차단이 걸리므로, 파서 검증(소재지 파싱 실패 0건)을 **다운로드 전에** 끝낸다.

★ 그래도 차단되면 승인 도구를 부르지 말고, 브라우저 안에서 집계까지 끝내
결과 수치를 보고에 싣고 「CSV 저장 실패 — 다운로드 차단」을 명시한다.

---

## STEP 1 — 진입 및 로그인 확인

```
navigate → https://www.ggi.co.kr/search/total_search.asp
```

```javascript
/로그아웃/.test(document.body.textContent)   // true 여야 함
```

false면 즉시 중단하고 재로그인을 요청한다. 진행하지 않는다.
(요청은 보고에 적는 것으로 끝낸다. 응답을 기다리지 않는다.)

최상위가 `https://www.ggi.co.kr/` 로 리다이렉트되어 `frmSearch`가 없을 수 있다.
정상이다 — STEP 3의 숨은 iframe 안에 폼이 살아 있다.

---

## STEP 2 — 검색 조건

`total_search.asp`에 직접 가면 폼(`frmSearch`)이 **최상위 document**에 있다.

`resultchk1`(경매종합검색, value `N`)을 선택하고 `chk_ipchalresult()`를 호출한다.
입찰당일결과 모드(`resultchk2`)가 아니다.

| 필드 | 값 | 의미 |
|---|---|---|
| `resAuctionResult` | `01` | **신건** (전용 옵션이 있다) |
| `resYouchalCnt1` / `resYouchalCnt2` | `0` / `0` | 유찰 0회 (이중 안전장치) |
| `resSiDo` | `09`=서울, `02`=경기 | 시도별로 따로 돌린다 |
| `resSiGuGun` / `resEMDong` | 빈 값 | 시도 전체 |
| `pgesize` | `100` | 페이지당 건수 |
| `nowPge` | 1,2,3… | 페이지 번호 |
| `SDay` | 기본값 유지 | 기본이 "오늘 이후"라 매각기일 미래만 나온다 |

`resAuctionResult` 참고값: `A1,01`=진행+신건 / `A1`=진행(구건) / `01`=신건 /
`01A`=신건(금일공고) / `02`=유찰 / `03,06`=매각.

### 용도 (`resuse` 체크박스)

`useall`은 해제하고 아래 13개만 체크한다.

```
22 빌딩          23 사무실        21 상가          24 점포(근린시설)
25 근린시설      12 아파트상가    14 주상복합(상가) 20 시장
D3 대형판매시설  B1 오피스텔      B2 오피스텔(상가) J2 아파트형공장(상가)
03 근린주택
```

**`26 오피스텔(주거용)`은 제외한다.** 주거용이다.

---

## STEP 3 — 수집 (숨은 iframe + 재시도)

최상위에서 `frmSearch.submit()`을 하면 페이지가 이동하며 헬퍼 함수가 사라진다.
**숨은 iframe 안에서 제출**해야 최상위 컨텍스트가 살아남는다.

```javascript
let fr = document.getElementById('__gg');
if (!fr) { fr = document.createElement('iframe'); fr.id='__gg';
  fr.style.cssText='position:fixed;left:-9999px;width:1400px;height:900px';
  document.body.appendChild(fr); }
await new Promise(r => { fr.onload = r; fr.src='https://www.ggi.co.kr/search/total_search.asp'; });
await new Promise(r => setTimeout(r, 1800));

window.__USE=['22','23','21','24','25','12','14','20','D3','B1','B2','J2','03'];

window.__set = function (page, sido) {
  const fr=document.getElementById('__gg'), d=fr.contentDocument, w=fr.contentWindow;
  const f=d.frmSearch;
  const r1=d.getElementById('resultchk1'); if(r1){r1.checked=true; try{w.chk_ipchalresult();}catch(e){}}
  const S=(n,v)=>{const e=[...f.elements].find(x=>x.name===n); if(e) e.value=v;};
  S('resAuctionResult','01');
  S('resYouchalCnt1','0'); S('resYouchalCnt2','0');
  S('resSiDo',sido); S('resSiGuGun',''); S('resEMDong','');
  [...f.elements].filter(e=>e.name==='resuse').forEach(e=>{e.checked=window.__USE.includes(e.value);});
  const ua=[...f.elements].find(e=>e.name==='useall'); if(ua) ua.checked=false;
  S('pgesize','100'); S('nowPge',String(page));
  return f;
};
window.__total = function (doc) {
  const m=(doc.body.textContent||'').match(/총\s*([\d,]+)\s*건/);
  return m ? +m[1].replace(/,/g,'') : null;
};
```

### 재시도 필수 — 간헐적 0건 응답이 있다

서버가 이유 없이 빈 결과를 돌려준다. **재시도 없이 돌리면 지역 하나가 조용히 통째로 빠진다.**

```javascript
window.__collect = async function (sido, sidoName) {
  const fr=document.getElementById('__gg'); let all=[], tot=null, fail=[];
  for (let p=1; p<=20; p++) {
    let got=null;
    for (let a=0; a<3; a++) {
      const f=window.__set(p,sido);
      const done=new Promise(r=>{fr.onload=r;}); f.submit(); await done;
      await new Promise(r=>setTimeout(r,1100+a*800));
      const rows=window.__parse(fr.contentDocument,sidoName);
      const T=window.__total(fr.contentDocument);
      if (rows.length>0 || T===0) { got={rows,T}; break; }
    }
    if (!got) { fail.push(p); break; }
    tot=got.T; all=all.concat(got.rows);
    if (all.length>=tot || got.rows.length===0) break;
  }
  return {tot, rows:all, fail};
};
```

### 총 건수 대조

서버의 `총 N 건`과 실제 수집 건수가 **반드시 같아야 한다.** 다르면 보고에 명시한다.

---

## STEP 4 — 파서

### ★ 표 탐지: 행 수 하한을 두지 말 것

`rows.length > 10` 같은 조건은 마지막 소량 페이지를 통째로 버린다.
행 수가 아니라 **셀 개수(>=7)가 있는 행이 가장 많은 표**를 고른다.

### ★ 소재지: `c3[1]`을 그대로 쓰면 안 된다

물건기본내역 칸에는 사건번호 줄 뒤에 **물건종별 줄**(예: `상가`, `근린건물`)이나
**특이사항 줄**(예: `[입찰외 대항력임차인]`)이 끼어드는 행이 있다.
`c3[1]`을 소재지로 쓰면 그런 행에서 `상가`가 주소가 되어 시·군·구 파싱이 깨진다.

**시도명으로 시작하는 첫 줄**을 소재지로 고른다.

```javascript
window.__parse = function (doc, sidoName) {
  const TX=el=>(el.textContent||'').replace(/ /g,' ');
  const cand=[...doc.querySelectorAll('table')].filter(x=>TX(x).includes('물건기본내역'));
  let t=null,best=0;
  for (const x of cand){const n=[...x.rows].filter(r=>r.cells.length>=7).length; if(n>best){best=n;t=x;}}
  if(!t) return [];
  const L=c=>TX(c).split('\n').map(s=>s.trim()).filter(Boolean);
  const num=s=>+String(s).replace(/[^\d]/g,'')||0;
  const SIDO=/^(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주)\s/;
  const out=[];
  for (let i=1;i<t.rows.length;i++){
    const r=t.rows[i]; if(r.cells.length<7) continue;
    const c2=L(r.cells[2]),c3=L(r.cells[3]),c4=L(r.cells[4]),c5=L(r.cells[5]),
          c6=L(r.cells[6]),c7=L(r.cells[7]||r.cells[6]);
    if(!c2.length||!c3.length) continue;
    const head=(c3[0]||'').split(/\s+/);
    if(!/\d{4}-\d+/.test(head[1]||'')) continue;
    const addr = c3.find(s=>SIDO.test(s)) || '';
    const jong = c3.slice(1).find(s=>s!==addr && !/^\[/.test(s) && !/㎡/.test(s)) || '';
    const bigo = c3.filter(s=>/^\[/.test(s)).join(' ').replace(/[\[\]]/g,'').replace(/\s+/g,' ').trim();
    const money=c4.filter(x=>/^[\d,]+$/.test(x)).map(num);
    const ar=TX(r.cells[3]).replace(/\s+/g,' ');
    out.push({시도:sidoName, 매각기일:(c2[0]||''), 잔여:(c2[1]||''), 용도:c2[c2.length-1]||'',
      물건종별:jong, 법원계:head[0]||'', 사건번호:head[1]||'', 소재지:addr, 비고:bigo,
      감정가:money[0]||0, 최저가:money[1]||0, 상태:(c5[0]||''),
      최저가율:num((c5.join(' ').match(/\((\d+)%\)/)||[])[1]),
      건물면적:num((ar.match(/건물\s*([\d,]+)㎡/)||[])[1]),
      토지면적:num((ar.match(/토지\s*([\d,]+)㎡/)||[])[1]),
      조회수:num(c6[0]||0), 추가정보:(c7.join(' ')||'').replace(/·/g,' ').trim()});
  }
  return out;
};
```

`비고`가 중요하다. `대항력임차인`, `유치권`, `지분매각`, `입찰외`, `선순위임차권` 등이 여기 들어온다.
표본의 약 40%가 비고를 갖는다.

### 다운로드 전 검증 (필수)

```javascript
all.filter(r=>!r.소재지).length   // 0이어야 한다
```

0이 아니면 파서를 고친 뒤 **다시 수집**한다. 다운로드는 그 다음이다.

---

## STEP 5 — CSV 다운로드

BOM 붙인 UTF-8 CSV로 한 번만 내려받는다.

```javascript
const csv='\ufeff'+window.__TSV.split('\n')
  .map(l=>l.split('\t').map(c=>'"'+c.replace(/"/g,'""')+'"').join(',')).join('\r\n');
const b=new Blob([csv],{type:'text/csv;charset=utf-8'});
const a=document.createElement('a'); a.href=URL.createObjectURL(b);
a.download='ggi_newlist_YYYYMMDD.csv';
document.body.appendChild(a); a.click();
```

**다운로드 폴더(`%USERPROFILE%\Downloads`)에 파일이 실제로 생겼는지 확인한다.**
없으면 크롬이 차단한 것이다 — 위 "다운로드 차단" 항목대로 처리한다.

---

## STEP 6 — 파생 컬럼

CSV를 읽어 아래 컬럼을 붙인다.

| 컬럼 | 산출 방법 |
|---|---|
| 시·군·구 | 소재지 2번째 토큰. 단 `○○시 ○○구` 형태면 시 단위를 쓴다 |
| 시·군·구 상세 | `○○시 ○○구` 형태면 둘을 붙인다 |
| 법원 | 법원계에서 뒤의 `숫자+계`를 떼어낸다 (`남부5계` → `남부`) |
| 용도대분류 | 아래 표 |
| 매각기일월 | `YYYY-MM` |
| 잔여일수 | 매각기일 − 수집일 |
| 잔여 구간 | ① 7일 이내 / ② 8~14일 / ③ 15~30일 / ④ 30일 초과 |
| 감정가 규모대 | ① 100,000,000원 미만 / ② 100,000,000~300,000,000원 / ③ 300,000,000~500,000,000원 / ④ 500,000,000~1,000,000,000원 / ⑤ 1,000,000,000~3,000,000,000원 / ⑥ 3,000,000,000~5,000,000,000원 / ⑦ 5,000,000,000원 이상 |
| 건물㎡당 감정가(원) | 감정가 ÷ 건물면적 (0이면 공란) |
| 조회수 구간 | ① 50회 미만 / ② 50~99회 / ③ 100~199회 / ④ 200회 이상 |
| 신규 | 마스터에 `법원계+사건번호` 키가 없으면 `신규`, 있으면 `기존` |

**용도대분류 매핑**

| 대분류 | 포함 용도 |
|---|---|
| 업무시설 | 빌딩, 사무실 |
| 집합상가 | 상가, 아파트상가, 주상복합(상가), 아파트형공장(상가), 시장, 대형판매시설 |
| 근린상가 | 점포(근린시설), 근린시설 |
| 오피스텔 | 오피스텔, 오피스텔(상가) |
| 근린주택 | 근린주택 |

구간 라벨은 **원 단위 풀 콤마**로 쓴다. `3억~5억원` 같은 축약은 금지다.
라벨이 길어 차트가 답답하면 라벨을 줄이지 말고 **가로 막대(BarStacked)** 로 바꾼다.

`매각기일월`은 피벗 축으로 쓰지 않는다. 신건은 기일이 한 달 안에 몰려 값이 1개뿐이라
차트가 무의미하다. 대신 `잔여 구간`을 쓴다.

정렬은 `매각기일 → 시도 → 법원계 → 사건번호`. 그 뒤 `연번`을 1부터 붙인다.

## 마스터 대조 (신규 판정)

1. `_마스터_사건번호.csv`를 읽는다 (없으면 전부 `신규`).
2. `법원계 + 사건번호`를 키로 대조한다. 사건번호만으로는 법원이 달라도 겹칠 수 있다.
3. 이번 회차 키를 마스터에 추가해 저장한다.

★ **마스터 추가는 엑셀(STEP 7~8)이 완성된 뒤에 하는 것이 안전하다.**
먼저 넣고 엑셀이 실패하면 그 물건이 다음 주에 `기존`으로 묻혀 영영 보고되지 않는다.
순서를 바꿀 수 없다면 아래 「실패했을 때」의 되돌리기 규칙을 반드시 지킨다.

---

## STEP 7 — 엑셀 산출물 (4시트)

시트 순서: **탐색 → 원자료 → 피벗집계 → 대시보드**.
**처음부터 최종 저장 위치에 파일을 만든다.**
나중에 시트를 다른 파일로 옮기면 피벗 원본이 외부 참조로 깨지고 슬라이서 연결이 끊긴다.

빌드 순서는 `excel-explore-sheet` 스킬의 3단계를 그대로 따른다.
**1단계 openpyxl(정적) → 2단계 Excel MCP(표·수식·슬라이서·피벗·차트) → 3단계 XML 패치.**
**openpyxl로 파일을 다시 저장하면 슬라이서가 삭제되고 피벗차트가 일반 차트로 강등된다.**
그래서 기존 파일에 시트를 덧붙이지 않고 처음부터 다시 만든다.

### 탐색 시트 (사용자가 가장 많이 쓰는 화면)

`excel-explore-sheet` 스킬을 **함께 읽는다.** 레이아웃·수식·행 높이 규약이 거기 있다.
아래는 이 산출물에 고정된 값이다.

| 항목 | 값 |
|---|---|
| 표 이름 | `TBL_EXPLORE` — **한글 표 이름은 Excel COM이 거부한다** |
| 원본 표 | `A500:U{500+N}` (헤더 500행, 데이터 501행~) |
| 결과 스필 | `A15` 1개 |
| 키 열 | `F`(사건번호) — 빈 값이 없다 |
| 보조열 | `Z500` 헤더, `Z501~` `=SUBTOTAL(103,F{행})` |
| 열 구성 21개 | 연번·시도·시·군·구·법원·법원계·사건번호·매각기일·잔여일수·잔여 구간·용도·용도대분류·소재지·비고·감정가·감정가 규모대·최저가·건물면적·토지면적·조회수·조회수 구간·신규 |
| **B열 너비 17 / C열 19** | 요약 패널이 B4:C9라 좁으면 값이 잘린다. 결과표 시도·시군구가 넓어지는 건 감수한다 |
| 행 높이 | 1행 22 / 4~9행 각 24 / 10~12행 각 20 / 13행 22 / 14행 30 |
| 틀고정 | `A15` (열 고정 없음) |

요약 6칸 (C4:C9) — **표를 만든 뒤에** 넣는다.

```
C4 =SUBTOTAL(103,TBL_EXPLORE[사건번호])
C5 =SUBTOTAL(109,TBL_EXPLORE[감정가])
C6 =IFERROR(ROUND(SUBTOTAL(101,TBL_EXPLORE[감정가]),0),0)
C7 =IFERROR(SUBTOTAL(104,TBL_EXPLORE[감정가]),0)
C8 =SUBTOTAL(109,TBL_EXPLORE[최저가])
C9 =IFERROR(ROUND(SUBTOTAL(103,TBL_EXPLORE[사건번호])/COUNTA(TBL_EXPLORE[사건번호])*100,1),0)
A15 =LET(a,FILTER($A$501:$U${끝행},$Z$501:$Z${끝행}=1,""),IF(a="","",a))
```

**표 슬라이서 8개** (`create-table-slicer`, `TBL_EXPLORE`에 연결). 위치는 아무 셀이나
잡고 3단계에서 pt로 정렬한다.

```
SL_시도  SL_시군구  SL_법원  SL_용도대분류
SL_감정가규모대  SL_잔여구간  SL_조회수구간  SL_신규
```

3단계 XML 패치에서 `twoCellAnchor` → `absoluteAnchor`로 바꿔 한 줄로 정렬한다.

```
left = 302 + i*142 (i=0..7),  top = 48,  width = 134
height = 170, 단 SL_시군구·SL_법원 212 / SL_감정가규모대 200
```

`left`를 250 이하로 잡으면 **요약 패널을 덮는다**(2026-09-02 실측).

### 원자료

`TBL_GGI` 표(`TableStyleMedium2`). 컬럼 순서 28개 — **바꾸지 않는다.**

```
연번 시도 시·군·구 시·군·구 상세 법원 법원계 사건번호 매각기일 잔여일수 잔여 구간
용도 용도대분류 물건종별 소재지 비고 감정가 최저가 최저가율 감정가 규모대
건물면적 토지면적 건물㎡당 감정가(원) 조회수 조회수 구간 상태 매각기일월 신규 추가정보
```

금액·건수는 `#,##0`, 날짜는 `yyyy-mm-dd`,
**연번·사건번호는 콤마 없이 General/텍스트**로 둔다. 틀고정 `A2`.

열 너비(확정): A 6 · C 10 · D 14 · E 10 · G 13 · H 12 · I 9 · J 13 · K 14 · L 11 ·
M 10 · N 52 · O 26 · P 16 · R 9 · S 30 · T 10 · V 18 · W 8 · X 13 · Y 7 · Z 11 · AA 7 · AB 40
(B·F·Q·U는 기본값)

### 피벗집계 (Excel MCP로 진짜 PivotTable 7개)

| 이름 | 위치 | 행 | 열 | 값 |
|---|---|---|---|---|
| PT_법원 | A3 | 법원 | 용도대분류 | 건수 |
| PT_법원요약 | I3 | 법원 | — | 건수, 평균 감정가(원), 감정가 합계(원), 평균 건물면적(㎡) |
| PT_감정가규모 | P3 | 감정가 규모대 | 용도대분류 | 건수 |
| PT_잔여구간 | P20 | 잔여 구간 | 시도 | 건수 |
| PT_용도대분류 | P42 | 용도대분류 | 시도 | 건수 |
| PT_조회수구간 | Y3 | 조회수 구간 | 용도대분류 | 건수 |
| PT_시군구 | Y20 | 시·군·구 | 용도대분류 | 건수 |

건수 값 필드는 `연번`을 `Count`로 집계하고 `custom_name`을 `건수`로 준다.

### 대시보드 — 확정 서식

| 위치 | 내용 | 서식 |
|---|---|---|
| B2 | 제목 `지지옥션 신건 레이더 — 서울·경기 업무·상업 (YYYY-MM-DD)` | **16pt** 굵게 `1F4E79`, 행높이 25.5 |
| B3 | `수집조건: 신건(유찰 0회)·매각기일 미래·업무/상업 13개 용도 \| 출처: 지지옥션(ggi.co.kr) 경매종합검색 \| 수집일 YYYY-MM-DD` | **9pt** `666666` |
| B5:M5 | KPI 헤더 12칸 | **9pt** 굵게 흰글씨, 채움 `1F4E79`, 흰 테두리, 가운데·줄바꿈, **행높이 44** |
| B6:M6 | KPI 값 | **12pt 굵게 검정**(파랑 아님), 채움 `EAF1F8`, `#,##0`, 행높이 26 |

KPI 12칸 (`TBL_GGI` 구조적 참조):
총 물건수 · 서울 · 경기 · 이번 주 신규 · 집합상가 · 오피스텔 · 근린상가 · 근린주택 ·
매각기일 7일 이내 · 감정가 300,000,000원 미만 · 평균 감정가(원) · 감정가 합계(원)

**열 너비: B 13.58 / L 22.58 / M 22.58.** M을 빼먹으면 감정가 합계가 `######`이 된다.
나머지 열은 기본값을 유지한다 — 전체를 넓히면 지난 회차와 달라 보인다.

피벗차트 5개 (`create-from-pivottable`). **제목에 "누적"을 반드시 넣는다.**

| 차트 | 원본 피벗 | 종류 | 위치 | 제목 |
|---|---|---|---|---|
| CH_법원 | PT_법원 | BarStacked | B8:L34 | 법원별 신건 건수 (용도대분류 누적) |
| CH_용도대분류 | PT_용도대분류 | ColumnStacked | M8:W21 | 용도대분류별 신건 건수 (시도 누적) |
| CH_감정가규모 | PT_감정가규모 | BarStacked | M22:W34 | 감정가 규모대별 신건 건수 (용도대분류 누적) |
| CH_조회수구간 | PT_조회수구간 | ColumnStacked | X8:AH21 | 조회수 구간별 신건 건수 (용도대분류 누적) |
| CH_잔여구간 | PT_잔여구간 | ColumnStacked | X22:AH34 | 매각기일 잔여 구간별 신건 건수 (시도 누적) |

차트 생성 시 "OVERLAP WARNING"이 떠도 서로 맞닿을 뿐이면 무시한다 — 스크린샷으로 확인한다.

- 피벗 슬라이서 2개를 PT_법원에 연결: `용도대분류`(B36), `시도`(F36)
  이름은 탐색 시트 슬라이서와 겹치지 않게 `SLD_` 접두어를 쓴다
- 시트 눈금선 끄기

**대시보드 슬라이서는 차트만 움직인다.** 목록 드릴다운은 탐색 시트가 담당한다.
사용자가 "슬라이서를 눌러도 목록이 안 줄어든다"고 하면 탐색 시트를 안내한다.

---

## STEP 8 — XML 패치 (Excel MCP로는 불가)

세 가지를 한 번에 처리한다. **Excel 세션을 닫은 뒤에** 실행한다.

1. 차트 경계선 (`chart_config`에 옵션이 없다)
2. 탐색 시트 슬라이서 pt 정밀 배치 (`twoCellAnchor` → `absoluteAnchor`)
3. 대시보드 눈금선 (`showGridLines="0"`, 1단계에서 걸었으면 생략)

**xlsx 압축 해제 → 해당 XML만 수정 → 재압축**이 유일하게 안전한 방법이다.
다른 부품은 원본 바이트 그대로 복사되므로 피벗·슬라이서가 보존된다.

```python
import zipfile, re
SPPR=('<c:spPr>'
      '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
      '<a:ln w="12700" cap="flat" cmpd="sng" algn="ctr">'
      '<a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill><a:round/>'
      '</a:ln></c:spPr>')
zin=zipfile.ZipFile(SRC); zout=zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d=zin.read(it.filename)
    if re.match(r'xl/charts/chart\d+\.xml$', it.filename):
        x=d.decode('utf-8')
        if '</c:chart><c:spPr>' not in x:          # 이미 있으면 건드리지 않는다
            x=x.replace('</c:chart>','</c:chart>'+SPPR,1)
        d=x.encode('utf-8')
    zout.writestr(it,d)
zout.close(); zin.close()
```

`c:spPr`는 스키마상 **`</c:chart>` 바로 뒤**에 와야 한다. 다른 자리에 넣으면 파일이 손상된다.

시트 파트 번호는 고정이 아니다. `xl/workbook.xml`의 `<sheet name="...">` r:id를
`xl/_rels/workbook.xml.rels`로 풀어 실제 경로를 찾는다. 탐색 시트의 drawing 파트는
그 시트 XML의 `<drawing r:id="...">`를 시트 rels로 풀어 얻는다.

검증: 원본과 패치본의 **부품 수·목록이 같고**, 달라진 부품이 의도한 것뿐이며,
`xl/slicers/`·`xl/slicerCaches/`가 그대로 남아 있어야 한다. 아니면 교체하지 않는다.

### 파일 교체가 막힐 때 ★ (2026-09-08 개정)

OneDrive 동기화 폴더에서는 기존 파일 덮어쓰기·삭제가 일시적으로 거부된다
(`Operation not permitted` / `Permission denied`). 20초쯤 기다렸다 다시 시도하면 대개 풀린다.

**`~$파일명.xlsx` 잠금 파일이 있으면 Excel이 잡고 있는 것이다.**
Excel MCP 세션이 타임아웃되면 고아 프로세스가 남아 파일을 계속 잡을 수 있다.

종전 문구 「사용자에게 파일을 닫아달라고 요청한다」는 **무인 회차에서 회차를 세운다.**
아래로 대체한다.

- **요청하고 기다리지 않는다. 승인 도구도 부르지 않는다**
- `_v2` 파일명으로 저장하고 보고에 「원본 잠김 — 다음 회차 재시도」를 적는다
- 백업(`_backup_대시보드_YYYYMMDD_XML패치전.xlsx`)은 교체 전에 남기되,
  백업·삭제가 막혀도 그냥 넘어가고 보고에 적는다
- 대화형으로 사람이 함께 있을 때만 닫아달라고 요청해도 된다

---

## STEP 9 — 저장 전 검증 (건너뛰지 않는다)

`number-format-guard` 스킬을 함께 적용한다. 특히:

### ★ 피벗 값 필드의 number_format 인자는 조용히 무시된다

`add-value-field`에 `number_format`을 넘겨도 `success: true`가 오면서
셀 서식은 `G/표준`으로 남는다. **값 필드마다 별도로** 다시 건다.

```
pivottable_field(action:"set-field-format", pivot_table_name:"PT_xxx",
                 field_name:"<custom_name으로 붙인 이름>", number_format:"#,##0")
```

### ★ 피벗 총합계 행은 그래도 G/표준으로 남는다

`set-field-format` 후에도 총합계 행 서식이 안 붙는다.
그 행만 `range(set-number-format)`으로 따로 건다. (새로고침하면 지워지므로 매 회차 다시 건다.)

### 체크리스트

- [ ] **직전 회차 파일과 서식을 대조**했는가 (글자 크기·색·행 높이·열 너비·컬럼 순서·차트 제목)
- [ ] 탐색: 슬라이서 하나를 실제로 눌러 `C4` = 스필 행 수인지 확인했는가
- [ ] 탐색: 확인 뒤 **슬라이서 8개를 전부 전체 선택으로 되돌렸는가** (`list-table-slicers`로 읽어서)
- [ ] 탐색: 슬라이서가 13·14행을 덮지 않는가, 요약 패널을 가리지 않는가
- [ ] `range(get-number-formats)`로 **읽어서** 확인했는가 (원자료 금액열, 피벗 값 영역, KPI 행)
- [ ] `screenshot(capture)`로 콤마가 눈에 보이는가, `######`이 없는가
- [ ] 억/만/조 축약 문자열이 없는가 (셀·헤더·차트 제목·구간 라벨 전부)
- [ ] 연번·사건번호에 콤마가 없는가
- [ ] 피벗 `sourceData`가 `TBL_GGI`인가 (외부 파일 경로면 실패)
- [ ] 피벗 총합계 = 원자료 행 수 = 탐색 원본 행 수 = 서버 "총 N 건"
- [ ] `#REF! #VALUE! #SPILL! #NAME?` 스캔 0건
- [ ] XML 패치 후 파일을 다시 열어 **피벗 7개·슬라이서 10개**(탐색 8 + 대시보드 2)가 살아 있는가

---

## 실패했을 때 ★ (2026-09-08 신설)

**부분 산출물을 남기지 않는다** 는 원칙은 맞다. 다만 **마스터를 먼저 되돌린 뒤에** 지운다.

마스터 갱신(STEP 6)이 엑셀 생성(STEP 7~8)보다 앞서 실행됐다면, 엑셀만 지울 경우
그 물건들이 마스터에 `기존`으로 남아 **다음 주에 신규로 잡히지 않고 영영 보고되지 않는다.**

1. **마스터에서 이번 회차 추가분을 먼저 되돌린다**
2. 되돌리기가 안 되면 **엑셀도 지우지 말고** 그대로 두고, 보고에
   「마스터에 N건이 들어갔으나 산출물 미완성 — 다음 회차에 신규로 안 잡힘」 을 명시한다
3. 삭제가 `Operation not permitted` 로 막히면 그냥 두고 보고한다. 승인 도구를 부르지 않는다

**어느 경우에도 마스터와 산출물이 어긋난 사실을 침묵하지 않는다.**

---

## 보고 형식

```
수집일: YYYY-MM-DD
서울 N건 (서버 총 N건) / 경기 M건 (서버 총 M건) → 합계 X건
이번 주 신규: K건 (마스터 대비)
용도대분류: 집합상가 a / 오피스텔 b / 근린상가 c / 근린주택 d / 업무시설 e
비고 보유(대항력임차인·유치권·지분·입찰외 등): F건
매각기일 7일 이내: G건
감정가 합계: 0,000,000,000원
탐색 드릴다운 실측: <조건> → N건 (C4와 결과 행 수 일치)
파일 잠금·다운로드 차단 항목과 다음 회차 재시도 예정
마스터·산출물 정합 여부 (어긋났으면 반드시 명시)
실패·누락: (없으면 "없음")
```

검증하지 않은 항목을 "확인했다"고 쓰지 않는다. 못 한 검증은 그대로 밝힌다.
신규 중 눈여겨볼 물건이 있으면 3건 이내로 감정가·소재지·용도만 짚는다.
투자 판단은 하지 않는다.

---

## 변경 이력

- **2026-09-08 (무인실행 중단 사고 반영)**: 맨 앞에 **「무인 실행 원칙」** 절 신설 —
  승인 팝업 도구 호출 금지, 사용자 응답 대기 금지, 「이어서 진행」 빈 응답 금지.
  / STEP 8 「파일 교체가 막힐 때」의 「사용자에게 파일을 닫아달라고 요청한다」를
  **`_v2` 저장 + 보고**로 대체(대화형은 예외). / STEP 1 재로그인 요청도 "기다리지 않는다"로 명시.
  / **「실패했을 때」 절 신설** — 마스터 갱신이 엑셀 생성보다 앞서므로, 엑셀만 지우면
  그 물건이 `기존`으로 묻혀 영영 보고되지 않는다. 마스터를 먼저 되돌리는 순서를 명문화했다.
  / STEP 6 마스터 대조에 「엑셀 완성 뒤 추가가 안전」 주석 추가.

