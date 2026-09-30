// court-newlist-collect / collect.js
// 법원경매정보(courtauction.go.kr) 신건 목록 수집 — 브라우저 콘솔(Claude in Chrome javascript 도구)용
//
// [확정 — 2026-09-29 실측] 물건상세검색 화면을 한 번 연 탭에서 실행한다 (같은 출처 fetch, 쿠키 사용).
// 사용 순서 (각 단계를 따로 실행한다 — JS 도구는 한 번에 약 45초 제한):
//   1) 이 파일의 [A] 블록을 실행 → window.__req 준비
//   2) [B] 블록에서 날짜 두 개를 바꿔 실행 → 수집이 뒤에서 돈다 (await 하지 않는다)
//   3) [C] 블록을 60~150초 간격으로 실행해 진행 상황을 본다
//   4) done===true, 모든 법원 got===tot, fail 빈 배열이면 [D] 블록으로 JSON 다운로드
//
// 요청 사이 300ms 대기는 서버 부담을 줄이려는 것이다. 줄이지 않는다.
// 이용약관 제15조(입찰참가 외 영리목적 이용 금지)와 「비정상적 다량 조회 시 IP 차단」 안내를 지킨다.
// 개인 검토 목적, 주 1회, 서울·경기 15개 법원 범위 안에서만 쓴다.

// ─────────────────────────────────────────────────────────────
// [A] 요청 함수 준비 — [확정 — 2026-09-29 실측] 이대로 동작
// ─────────────────────────────────────────────────────────────
window.__COURTS = {
  B000210: "중앙", B000211: "동부", B000215: "서부", B000212: "남부", B000213: "북부",
  B000214: "의정부", B214807: "고양", B214804: "남양주", B000241: "부천",
  B000250: "수원", B000251: "성남", B000252: "여주", B000253: "평택", B250826: "안산", B000254: "안양"
};
// 전국 법원 코드 61개 [확정 — 2026-09-30 물건상세검색 sbx_rletCortOfc 실측]. 필요한 것만 위 __COURTS 에 옮겨 쓴다.
//   B000210:서울중앙지방법원  B000211:서울동부지방법원  B000215:서울서부지방법원  B000212:서울남부지방법원
//   B000213:서울북부지방법원  B000214:의정부지방법원  B214807:고양지원  B214804:남양주지원
//   B000240:인천지방법원  B000241:부천지원  B000250:수원지방법원  B000251:성남지원
//   B000252:여주지원  B000253:평택지원  B250826:안산지원  B000254:안양지원
//   B000260:춘천지방법원  B000261:강릉지원  B000262:원주지원  B000263:속초지원
//   B000264:영월지원  B000270:청주지방법원  B000271:충주지원  B000272:제천지원
//   B000273:영동지원  B000280:대전지방법원  B000281:홍성지원  B000282:논산지원
//   B000283:천안지원  B000284:공주지원  B000285:서산지원  B000310:대구지방법원
//   B000311:안동지원  B000312:경주지원  B000313:김천지원  B000314:상주지원
//   B000315:의성지원  B000316:영덕지원  B000317:포항지원  B000320:대구서부지원
//   B000410:부산지방법원  B000412:부산동부지원  B000414:부산서부지원  B000411:울산지방법원
//   B000420:창원지방법원  B000431:마산지원  B000421:진주지원  B000422:통영지원
//   B000423:밀양지원  B000424:거창지원  B000510:광주지방법원  B000511:목포지원
//   B000512:장흥지원  B000513:순천지원  B000514:해남지원  B000520:전주지방법원
//   B000521:군산지원  B000522:정읍지원  B000523:남원지원  B000530:제주지방법원

const K = "aeeEvlAmtMax aeeEvlAmtMin carMdlNm carMdyrMax carMdyrMin cortAuctnMbrsId csNo dspslDxdyYmd dspslPlcNm execrOfcDvsCd flbdNcntMax flbdNcntMin fothDspslHm fstDspslHm fuelKndCd gdsVendNm grbxTypCd jdbnCd lafjOrderBy lclDspslGdsLstUsgCd lwsDspslPrcMax lwsDspslPrcMin lwsDspslPrcRateMax lwsDspslPrcRateMin mclDspslGdsLstUsgCd mvprpArtclKndCd mvprpArtclNm mvprpAtchmPlcTypCd mvprpDspslPlcAdongEmdCd mvprpDspslPlcAdongSdCd mvprpDspslPlcAdongSggCd objctArDtsMax objctArDtsMin rdDspslPlcAdongEmdCd rdDspslPlcAdongSdCd rdDspslPlcAdongSggCd rdnmNo rdnmSdCd rdnmSggCd rletDspslSpcCondCd rprsAdongEmdCd rprsAdongSdCd rprsAdongSggCd sclDspslGdsLstUsgCd scndDspslHm sideDvsCd thrdDspslHm".split(' ');
const info = {}; K.forEach(k => info[k] = "");
Object.assign(info, {
  bidDvsCd: "000331",          // 기일입찰
  mvprpRletDvsCd: "00031R",    // 부동산
  cortAuctnSrchCondCd: "0004601", // 법원 기준 검색
  notifyLoc: "off", pgmId: "PGJ151F01", cortStDvs: "1", statNum: 1
});
window.__base = { dma_pageInfo: {}, dma_srchGdsDtlSrchInfo: info };

window.__req = async function (cd, page, size, from, to) {
  const b = JSON.parse(JSON.stringify(window.__base));
  b.dma_pageInfo = { pageNo: page, pageSize: size, bfPageNo: page > 1 ? page - 1 : 1,
                     startRowNo: (page - 1) * size + 1, totalCnt: "", totalYn: "Y", groupTotalCount: "" };
  Object.assign(b.dma_srchGdsDtlSrchInfo, { cortOfcCd: cd, bidBgngYmd: from, bidEndYmd: to });
  for (let a = 0; a < 3; a++) {
    try {
      const r = await fetch('/pgj/pgjsearch/searchControllerMain.on', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json;charset=UTF-8', 'Accept': 'application/json' },
        body: JSON.stringify(b), credentials: 'include'
      });
      const j = await r.json();
      if (j.data && j.data.dlt_srchResult) return j;
      window.__lastErr = j;
    } catch (e) { window.__lastErr = e.message; }
    await new Promise(r => setTimeout(r, 1500));
  }
  return null;
};
"ready: __req / __COURTS(" + Object.keys(window.__COURTS).length + ")";

// ─────────────────────────────────────────────────────────────
// [B] 수집 루프 — 띄워 놓고 폴링한다. await 로 기다리면 45초 제한에 끊긴다.
//     날짜 두 개를 바꾼다: FROM = 오늘, TO = 오늘 + 3개월 (YYYYMMDD)
//     [확정 — 2026-09-29 실측] pageSize 50 정상 · 100 오류. 50 고정.
// ─────────────────────────────────────────────────────────────
/*
const FROM = "20260929", TO = "20261231";   // ← 바꾼다
window.__R = { rows: [], prog: {}, fail: [], done: false, started: Date.now() };
(async () => {
  for (const [cd, nm] of Object.entries(window.__COURTS)) {
    let p = 1, got = 0;
    while (true) {
      const j = await window.__req(cd, p, 50, FROM, TO);
      if (!j) { window.__R.fail.push(nm + ':' + p); break; }
      const tot = +j.data.dma_pageInfo.totalCnt, L = j.data.dlt_srchResult;
      L.forEach(x => x.__court = nm);
      window.__R.rows.push(...L); got += L.length;
      window.__R.prog[nm] = { tot, got };
      if (L.length === 0 || got >= tot) break;
      p++; await new Promise(r => setTimeout(r, 300));   // 서버 예의. 줄이지 않는다
    }
  }
  window.__R.done = true;
})();
"started";
*/

// ─────────────────────────────────────────────────────────────
// [C] 진행 확인 — 60~150초 간격으로 실행
// ─────────────────────────────────────────────────────────────
/*
({ done: window.__R.done, rows: window.__R.rows.length, fail: window.__R.fail,
   sec: Math.round((Date.now() - window.__R.started) / 1000), prog: window.__R.prog })
*/

// ─────────────────────────────────────────────────────────────
// [D] 완료 후 — 필요한 필드만 추려 JSON 1개로 다운로드
//     완료 조건: done===true 이고 모든 법원 got===tot 이고 fail 이 빈 배열
//     [확정 — 2026-09-29 실측] 15개 법원 14,465행 → 약 16.8MB
// ─────────────────────────────────────────────────────────────
/*
const F = ["__court","jiwonNm","jpDeptNm","srnSaNo","saNo","maemulSer","printSt","convAddr","pjbBuldList",
           "dspslUsgNm","lclsUtilCd","mclsUtilCd","sclsUtilCd","mokGbncd","gamevalAmt","minmaePrice",
           "yuchalCnt","maeGiil","mulBigo","inqCnt"];
const slim = window.__R.rows.map(x => { const o = {}; F.forEach(k => o[k] = x[k]); return o; });
const blob = new Blob([JSON.stringify({ meta: { from: FROM, to: TO, prog: window.__R.prog, fail: window.__R.fail,
  savedAt: new Date().toISOString() }, rows: slim })], { type: 'application/json' });
const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
a.download = 'court_newlist_raw_' + FROM + '.json'; document.body.appendChild(a); a.click(); a.remove();
"downloaded " + slim.length + " rows";
*/
