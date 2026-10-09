// 물건카드 PPTX 생성기 견본 (v3.1 규격) — 가상 데이터용
// 원칙: 장마다 제목 = 결론 한 문장 · 큰 숫자 카드 · 표 8행 이하 · 셀 하나에 숫자 하나 · 하단 「한 줄로 말하면」 · 세부는 부록
// 숫자·이름은 전부 _model.json 에서 읽는다. PPTX 를 손으로 고치지 말고 이 파일을 고쳐 다시 만든다.
// 실행: node card_template.js [모델 경로]   (환경변수 CARD_CHARTS = 도표 폴더, CARD_OUT = 출력 pptx)
const pptxgen = require("pptxgenjs");
const fs = require("fs"), path = require("path");
const HERE = __dirname;
let MP = process.argv[2] || path.join(HERE, "_model.json");
if (!fs.existsSync(MP)) MP = path.join(HERE, "sample_model.json");
const M = JSON.parse(fs.readFileSync(MP, "utf8"));
const META = M.meta;
const CH = process.env.CARD_CHARTS || path.join(HERE, "charts");
const SZ = JSON.parse(fs.readFileSync(path.join(CH, "sizes.json"), "utf8"));
const OUT = process.env.CARD_OUT || path.join(HERE, "out", `물건카드_${META.case.replace(/\s+/g, "_")}.pptx`);
fs.mkdirSync(path.dirname(OUT), { recursive: true });

const won = n => (n === null || n === undefined) ? "-" : Math.round(n).toLocaleString("en-US") + "원";
const pct = (x, d = 1) => (x * 100).toFixed(d) + "%";
const F = "Malgun Gothic";
const K = { navy: "1E2761", blue: "1456F0", ink: "1F2937", sub: "4B5563", gray: "9CA3AF", line: "E5E7EB", zebra: "F7F8FA",
  tint: "EEF3FF", amber: "D97706", amberT: "FFF4E5", red: "DC2626", redT: "FDECEC", green: "059669", greenT: "E8F7F1" };
// ★ PowerPoint 는 fit:"shrink" 를 파일을 편집하기 전에는 적용하지 않아 긴 제목·KPI 값이 줄바꿈돼 겹친다(실측).
//   글자폭을 추정해 생성 시점에 폰트를 미리 줄인다. LibreOffice 렌더는 축소를 바로 적용해 이 결함이 보이지 않는다 — 검증은 PowerPoint MCP 로.
const vlen = t => { let L = 0; for (const ch of String(t)) L += /[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF\u3000-\u303F\u2014\u2015]/.test(ch) ? 1.0 : (/[0-9]/.test(ch) ? 0.58 : (/[A-Z%()\[\]]/.test(ch) ? 0.66 : (ch === " " ? 0.32 : 0.5))); return L; };
const fitFs = (t, widthIn, fs0, fsMin, lines = 1) => { const cap = widthIn * 72 * lines; let fs = fs0; while (fs > fsMin && vlen(t) * fs * 1.04 > cap) fs -= 0.5; return fs; };
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; pres.title = `물건카드 ${META.case} ${META.property}`; pres.author = META.author;
let NO = 0;
function slide(title, sub, oneLine, notes, section) {
  const s = pres.addSlide(); NO++; s.background = { color: "FFFFFF" };
  if (section) s.addText(section, { x: 0.6, y: 0.18, w: 6, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: K.blue, isTextBox: true, margin: 0 });
  s.addText(title, { x: 0.6, y: 0.45, w: 12.1, h: 0.62, fontFace: F, fontSize: fitFs(title, 12.1, 24, 15), bold: true, color: K.navy, isTextBox: true, margin: 0, valign: "middle", fit: "shrink" });
  if (sub) s.addText(sub, { x: 0.6, y: 1.08, w: 12.1, h: 0.36, fontFace: F, fontSize: fitFs(sub, 12.1, 12.5, 9), color: K.sub, isTextBox: true, margin: 0, fit: "shrink" });
  if (oneLine) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 6.3, w: 12.1, h: 0.62, fill: { color: K.tint }, line: { color: K.tint }, rectRadius: 0.08 });
    s.addText([{ text: "한 줄로 말하면   ", options: { bold: true, color: K.blue } }, { text: oneLine, options: { color: K.ink } }],
      { x: 0.8, y: 6.3, w: 11.8, h: 0.62, fontFace: F, fontSize: fitFs("한 줄로 말하면   " + oneLine, 11.8, 13, 10, 2), valign: "middle", isTextBox: true, margin: 0, fit: "shrink" });
  }
  s.addText(`${META.footer} · ${META.confidential} · ${NO}`, { x: 0.6, y: 7.1, w: 12.1, h: 0.28, fontFace: F, fontSize: 9, color: K.gray, isTextBox: true, margin: 0 });
  s.addNotes(notes || title);
  return s;
}
function table(s, rows, colW, o = {}) {
  const fs_ = o.fs || 13; const num = /^[+\-−]?[\d,.]+\s?(원|%|%p|㎡|명|호|건|점|일|m|km|배|개|회|분|년|가구|개월)?$/;
  // ★ 열 단위 정렬: 첫 열과 머리글 행은 왼쪽. 그 밖의 열은 본문 칸 가운데 하나라도 숫자(금액·비율·수량)면
  //   그 열의 본문 전체를 오른쪽 끝에 맞춘다(글자 칸 포함). 한 열 안에서 왼쪽·오른쪽이 섞이지 않게 한다. 글자만 있는 열은 왼쪽.
  //   예외가 필요하면 o.align = { 열번호: "left" | "right" } 로 지정한다.
  const rightCol = rows[0].map((_, ci) => (o.align && o.align[ci]) ? o.align[ci] === "right" : (ci > 0 && rows.slice(1).some(r => num.test(String(r[ci]).trim()))));
  const data = rows.map((r, ri) => r.map((c, ci) => {
    const t = String(c); const op = { fontFace: F, fontSize: fs_, color: K.ink, valign: "middle", margin: [3, 6, 3, 6], border: { type: "solid", pt: 0.5, color: K.line } };
    if (ri === 0) Object.assign(op, { bold: true, color: "FFFFFF", fill: { color: K.navy } });
    else if (ri % 2 === 0) op.fill = { color: K.zebra };
    if (ri > 0 && rightCol[ci]) op.align = "right";
    if (ri > 0 && o.bold && o.bold(ri, ci)) op.bold = true;
    if (ri > 0 && o.color && o.color(ri, ci, t)) op.color = o.color(ri, ci, t);
    return { text: t, options: op };
  }));
  s.addTable(data, { x: o.x || 0.6, y: o.y || 1.6, w: colW.reduce((a, b) => a + b, 0), colW, rowH: o.rowH || 0.42 });
}
function kpi(s, x, y, w, h, label, value, note, color, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill || "F8FAFC" }, line: { color: K.line, width: 0.75 }, rectRadius: 0.08 });
  s.addText(label, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.36, fontFace: F, fontSize: 13, color: K.sub, isTextBox: true, margin: 0 });
  s.addText(value, { x: x + 0.2, y: y + 0.48, w: w - 0.4, h: 0.62, fontFace: F, fontSize: fitFs(value, w - 0.4, 23, 13), bold: true, color: color || K.navy, isTextBox: true, margin: 0, fit: "shrink" });
  if (note) s.addText(note, { x: x + 0.2, y: y + 1.12, w: w - 0.4, h: h - 1.2, fontFace: F, fontSize: 11.5, color: K.sub, isTextBox: true, margin: 0, valign: "top" });
}
function text(s, x, y, w, h, t, fs_, o = {}) {
  s.addText(t, Object.assign({ x, y, w, h, fontFace: F, fontSize: fs_ || 14, color: K.ink, isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 6 }, o));
}
function bullets(s, x, y, w, h, items, fs_) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, fontFace: F, fontSize: fs_ || 14, color: K.ink, valign: "top", paraSpaceAfter: 8, isTextBox: true, margin: 0 });
}
function img(s, name, x, y, maxW, maxH) {
  const r = 1000 / SZ[name]; let w = maxW, h = w / r; if (h > maxH) { h = maxH; w = h * r; }
  s.addImage({ path: path.join(CH, name + ".png"), x, y, w, h });
}
function src(s, t) { s.addText("출처: " + t, { x: 0.6, y: 6.94, w: 12.1, h: 0.16, fontFace: F, fontSize: 8, color: K.gray, isTextBox: true, margin: 0 }); }

// ════════════════════════════════════════════════════════════════════
// 아래는 장 견본이다. 장 순서와 모양은 SKILL.md 「고정 구성」을 따르고, 내용만 물건에 맞게 바꾼다.
// ════════════════════════════════════════════════════════════════════
const TAX = M.tax_property + M.tax_comprehensive;
const PL = M.pledge, loan = M.buy_cap * PL.ltv, plInt = loan * PL.rate * PL.days / 365;
const preNo = M.our_dividend - M.buy_cap, prePl = preNo - plInt;

// ═══ 1. 표지
{ const s = pres.addSlide(); NO++; s.background = { color: K.navy };
  s.addText("물건카드 · NPL 매입(관점 1) + 직접 낙찰(관점 2)", { x: 0.8, y: 1.2, w: 11.5, h: 0.5, fontFace: F, fontSize: 18, color: "CADCFC", isTextBox: true });
  s.addText(`${META.case}\n${META.property}`, { x: 0.8, y: 1.9, w: 11.5, h: 1.6, fontFace: F, fontSize: 32, bold: true, color: "FFFFFF", isTextBox: true });
  s.addText(META.kind, { x: 0.8, y: 3.7, w: 11.5, h: 0.5, fontFace: F, fontSize: 14, color: "CADCFC", isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.8, y: 4.6, w: 4.4, h: 0.6, fill: { color: K.red }, rectRadius: 0.08 });
  s.addText(META.confidential, { x: 0.8, y: 4.6, w: 4.4, h: 0.6, fontFace: F, fontSize: 16, bold: true, color: "FFFFFF", align: "center", isTextBox: true });
  s.addText(`${META.date} · ${META.author}`, { x: 0.8, y: 6.4, w: 11.5, h: 0.4, fontFace: F, fontSize: 12, color: "CADCFC", isTextBox: true });
  s.addNotes("표지."); }

// ═══ 2. 한눈에 보기 — KPI 4장 + 핵심 3줄
{ const s = slide("한눈에 보기 — 채권은 상한 아래로 사면 이익, 직접 보유는 맞지 않는다",
    `기준: 2회 유찰 · 예상 낙찰 ${won(M.bid)}`,
    "앞 4장만 읽어도 결론이 서야 한다. 이 문장은 그 장의 결론을 한 줄로 다시 말한다.", "결론 장. 판단은 사용자가 한다.", "결론");
  const y = 1.65, w = 2.9, h = 2.0, g = 0.17;
  kpi(s, 0.6, y, w, h, "관점 1 매입 상한", won(M.buy_cap), `청구액의 ${pct(M.buy_cap / M.claim)}`, K.blue, K.tint);
  kpi(s, 0.6 + (w + g), y, w, h, "예상 배당", won(M.our_dividend), `세전 이익 ${won(preNo)}`, K.green, K.greenT);
  kpi(s, 0.6 + 2 * (w + g), y, w, h, "먼저 빠지는 최우선변제", won(M.priority), `낙찰가의 ${pct(M.priority / M.bid)}`, K.amber, K.amberT);
  kpi(s, 0.6 + 3 * (w + g), y, w, h, "관점 2 직접 보유(법인)", `CoC ${pct(M.coc_corp, 2)}`, "대출 0원 가정", K.red, K.redT);
  bullets(s, 0.6, 3.9, 12.1, 2.3, [
    "관점 1 — 판정 한 줄 + 핵심 금액.",
    "관점 2 — 판정 한 줄 + 핵심 금액.",
    "가장 큰 변수 — ① ② ③ (다음 「결정 전 닫을 3가지」 장과 같은 순서)."], 14); }

// ═══ 3. 두 관점 나란히
{ const s = slide("두 관점 나란히 — 관점 1 매입가와 관점 2 입찰 판단", "같은 기준 회차 · 판단은 사용자가 한다",
    "채권을 사서 배당으로 회수하는 것이 기본이고, 직접 낙찰은 최악의 경우를 대비한 계산이다.", "두 관점을 나란히.", "결론");
  table(s, [["구분", "관점 1 — NPL 매입 후 제3자 낙찰 · 배당 회수", "관점 2 — 최악 시 직접 낙찰(유입 · 채권 상계)"],
    ["판정", "★★★ 조건부 매입", "유입 시 NO-GO 권고"],
    ["핵심 금액", `매입 상한 ${won(M.buy_cap)}`, `총투입(법인) ${M.tax3[1][3]}`],
    ["기준 성과", `배당 ${won(M.our_dividend)}`, `Cash-on-Cash ${pct(M.coc_corp, 2)}`],
    ["질권대출 반영", `세전 ${won(preNo)} → 질권 이자 빼면 ${won(prePl)}`, "-"],
    ["먼저 닫을 것", "감정가 · 선순위 조세", "규제지역 · 명도"]],
    [2.0, 5.05, 5.05], { fs: 14, rowH: 0.58, bold: (r, c) => c === 0 }); src(s, "_model.json (가상)"); }

// ═══ 4. 결정 전 닫을 3가지 — 사실 / 금액 영향 / 어디서
{ const s = slide("결정 전에 반드시 닫을 3가지", "이것이 확인되기 전에는 매입가를 확정하지 않는다",
    "세 가지가 좋은 쪽으로 닫히면 매입 상한이 올라가고, 하나라도 나쁘면 내려간다.", "최우선 확인 사항.", "결론");
  const items = [["① 법원 감정가", "감정평가서 공개 전.", "감정가가 낮게 나오면 배당이 줄어든다.", "담당 경매계"],
    ["② 선순위 조세", "교부청구 법정기일 미확인.", "근저당보다 빠르면 그만큼 배당이 준다.", "관할 세무서"],
    ["③ 보증금 미상 임차인", "권리신고서 원본 미확인.", "소액이면 최우선변제가 늘어난다.", "현황조사서 · 권리신고서"]];
  items.forEach((it, i) => { const y = 1.55 + i * 1.55;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 12.1, h: 1.42, fill: { color: i === 1 ? K.amberT : "F8FAFC" }, line: { color: K.line }, rectRadius: 0.08 });
    text(s, 0.85, y + 0.14, 3.0, 0.5, it[0], 17, { bold: true, color: K.navy });
    text(s, 3.9, y + 0.12, 8.6, 0.42, it[1], 13);
    text(s, 3.9, y + 0.55, 8.6, 0.42, it[2], 13, { bold: true, color: K.blue });
    text(s, 3.9, y + 0.97, 8.6, 0.38, "어디서: " + it[3], 12, { color: K.sub }); }); }

// ═══ 5. 회차 시나리오 (도표)
{ const s = slide("어느 회차에 팔리느냐가 결과를 가른다", "기준 회차 = 누적 매각 확률이 50%를 처음 넘는 회차",
    "회차는 가격대를 정하고, 응찰자 수가 그 안에서의 위치를 정한다.", "회차 시나리오.", "관점 1 · NPL 매입");
  img(s, "scen", 0.6, 1.55, 12.1, 4.6); src(s, "가상 데이터"); }

// ═══ 6. 배당 순서 — 표 + 폭포
{ const s = slide(`배당은 이 순서로 나간다 — 우리 채권 몫 ${won(M.our_dividend)}`, "집행비용 → 최우선변제 → 당해세 → 1순위 근저당",
    "당해세·최우선변제는 「소멸」이 아니라 근저당보다 먼저 빠지는 돈이다(주황).", "배당 순서. 사다리·엑셀·폭포와 금액이 같아야 한다.", "관점 1 · NPL 매입");
  table(s, [["순서", "항목", "금액"], ["1", "집행비용", won(M.exec_cost)], ["2", "최우선변제", won(M.priority)],
    ["3", "당해세(재산세+종부세)", won(TAX)], ["4", "우리 채권 배당", won(M.our_dividend)]], [0.8, 2.6, 2.3],
    { y: 1.6, color: (r, c) => (r === 2 || r === 3) ? K.amber : null });
  img(s, "waterfall", 6.6, 1.55, 6.1, 4.6); src(s, "가상 데이터"); }

// ═══ 7. 권리 사다리
{ const s = slide("권리 — 인수 0원, 최우선변제·당해세가 근저당보다 먼저", "말소기준 아래는 소멸",
    "인수할 권리가 없고, 먼저 빠지는 돈은 주황으로 금액까지 적었다.", "권리 사다리.", "권리 · 문건");
  img(s, "ladder", 0.6, 1.55, 12.1, 4.6); src(s, "등기부 원문(가상)"); }

// ═══ 8. 문건 타임라인
{ const s = slide("문건 — 지연 원인은 교부청구와 미상 임차인", "법원 문건접수·송달 내역",
    "빨강·주황 점이 결론을 흔드는 문건이다.", "문건 타임라인.", "권리 · 문건");
  img(s, "timeline", 0.6, 1.55, 12.1, 4.6); src(s, "문건접수내역(가상)"); }

// ═══ 9. 당해 연도 당해세 산출 — 재산세·종부세 각각 + 합계
{ const s = slide(`당해 연도 당해세 ${won(TAX)} — 재산세와 종부세를 따로 계산해 합쳤다`, "미납 가정 · 세율·납기는 그 답변에서 조문 조회",
    "두 세목을 각각 보이고 합계를 배당표·사다리·폭포·엑셀에 같은 금액으로 넣는다.", "당해세 산출.", "권리 · 문건");
  table(s, [["항목", "금액"], ["① 재산세(+가산)", won(M.tax_property)], ["② 종부세(+가산)", won(M.tax_comprehensive)], ["①+② 당해세 합계", won(TAX)]],
    [4.0, 3.0], { y: 1.7, fs: 14, rowH: 0.55, bold: (r) => r === 3, color: (r) => r === 3 ? K.amber : null }); src(s, "가상 데이터"); }

// ═══ 10. 질권대출 반영 — 무차입 / 질권대출 나란히
{ const s = slide(`세전 ${won(preNo)} — 질권대출 이자를 빼면 ${won(prePl)}`, `질권 LTV ${pct(PL.ltv, 0)} · 연 ${pct(PL.rate, 2)} · 보유 ${PL.days}일 [가정]`,
    "무차입 값만 보면 이익이 부풀어 보인다. 질권 이자를 뺀 값을 함께 본다.", "질권대출 반영.", "관점 1 · NPL 매입");
  table(s, [["항목", "무차입", "질권대출 사용"], ["매입가", won(M.buy_cap), won(M.buy_cap)], ["질권대출금", "0원", won(loan)],
    ["질권대출 이자", "0원", won(plInt)], ["우리 채권 배당", won(M.our_dividend), won(M.our_dividend)], ["세전 손익", won(preNo), won(prePl)]],
    [3.2, 3.2, 3.2], { y: 1.7, bold: (r) => r === 5 }); src(s, "가상 데이터"); }

// ═══ 11. 세금 3열 비교
{ const s = slide("세금 — 배당 회수 / 유입(개인) / 유입(법인)", "세금 장은 최소 3장(취득세 · 재산세·종부세 · 3열 비교) — 이 견본은 3열 비교만",
    "유입하면 보유세가 임대 순수익 대부분을 가져간다.", "3열 비교.", "세금");
  table(s, M.tax3, [3.0, 3.0, 3.0, 3.0], { y: 1.7, fs: 14, rowH: 0.55 }); src(s, "가상 데이터"); }

// ═══ 12. 확인해야 할 것 — 우선 / 항목 / 어디서 / 왜
{ const s = slide("확인해야 할 것", "최우선 항목을 닫기 전에는 입찰가·매입가를 확정하지 않는다",
    "완료 항목도 지우지 않고 남긴다.", "확인 목록.", "관점 2 · 직접 낙찰");
  table(s, [["우선", "확인 항목", "어디서", "왜"], ...M.checks], [1.3, 3.4, 3.4, 4.0],
    { y: 1.7, color: (r, c, t) => c === 0 ? ({ "최우선": K.red, "높음": K.amber, "완료": K.green }[t] || null) : null }); }

// ═══ 13. 계약일 체크리스트 (채권 매입 건)
{ const s = slide("계약일 — 이 다섯 가지만 확인한다", "계약일에는 법무사가 오지 않는다 · 잔금일·법무사 요청은 다음 장에서 따로",
    "많으면 확인에 시간이 걸린다. 금액이 바뀌는 것만 남겼다.", "계약일 체크리스트.", "계약");
  table(s, [["#", "확인", "누가"], ["1", "경매 사건번호 · 접수증", "매도 금융기관"], ["2", "임차인 명단 별지 · 진술보장", "우리"],
    ["3", "전입세대확인서 재발급", "매도 금융기관"], ["4", "채권양도통지서 · 사무위임", "매도 금융기관"], ["5", "매매대금 조정 조항", "우리"]],
    [0.8, 6.5, 3.5], { y: 1.7, fs: 14, rowH: 0.55 }); }

// ═══ 14. 출처 · 면책
{ const s = slide("출처 · 면책", "라벨: [확정] 직접 조회 · [검증필요] 원본 확인 전 · [추정] 가정 · [정보부족] 자료 없음",
    "이 덱은 가상 데이터로 만든 견본이다.", "출처.", "출처");
  bullets(s, 0.6, 1.7, 12.1, 4.3, ["시세: 국토교통부 실거래가(조회 경로·조회일 표기)", "법령: 조문 번호와 조회일(그 답변에서 직접 조회한 것만 [확정])",
    "법원 서류: 매각물건명세서 · 등기부 원문 · 현황조사서 · 문건접수내역", "판단은 의사결정자가 한다. 이 자료는 투자 권유가 아니다."], 14); }

pres.writeFile({ fileName: OUT }).then(f => console.log("저장:", f, "·", NO, "장"));
