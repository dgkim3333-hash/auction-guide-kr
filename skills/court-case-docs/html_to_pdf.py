# -*- coding: utf-8 -*-
"""
court-case-docs / html_to_pdf.py
법원경매정보 화면에서 떠낸 표 HTML → A4 PDF (weasyprint)

  pip install weasyprint --break-system-packages      # [확정 — 2026-09-29 실측] 70.0
  python html_to_pdf.py 사건내역.html 사건내역.pdf
  python html_to_pdf.py 현황조사서.html 현황조사서.pdf --images 현황조사_사진1.jpg 현황조사_사진2.jpg ...

- 폰트 Noto Sans CJK KR (LibreOffice 변환이 아니라 weasyprint — 한글 폰트 지정이 확실하다)
- A4, 여백 14mm/12mm, 표 테두리 #bbb, 머리행 #eef1f6, 하단 쪽번호 「n / N」
- --images 를 주면 본문 뒤에 사진을 base64 로 넣어 한 PDF로 합친다 (현황조사서용)
- 입력 HTML 은 SKILL.md 의 snap() 으로 떠낸 것. 제목·출처·저장일은 이 스크립트가 붙인다.
"""
import argparse, base64, datetime, mimetypes, os, sys

CSS = """
@page { size: A4; margin: 14mm 12mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #666; } }
body { font-family: 'Noto Sans CJK KR', 'NanumGothic', sans-serif; font-size: 9.5pt; color: #222; }
h1 { font-size: 14pt; margin: 0 0 4pt 0; }
.meta { font-size: 8.5pt; color: #666; margin-bottom: 8pt; }
table { border-collapse: collapse; width: 100%; margin-bottom: 8pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 3pt 4pt; vertical-align: top; word-break: break-all; }
th { background: #eef1f6; font-weight: 600; }
img.photo { max-width: 100%; max-height: 240mm; display: block; margin: 6pt auto; page-break-inside: avoid; }
.photo-cap { font-size: 8.5pt; color: #666; text-align: center; margin-bottom: 10pt; }
"""

def img_tag(path, idx):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return f'<img class="photo" src="data:{mime};base64,{b64}"><div class="photo-cap">현황조사 사진 {idx}</div>'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_in"); ap.add_argument("pdf_out")
    ap.add_argument("--title", help="문서 제목 (기본: 입력 파일명)")
    ap.add_argument("--source", default="대법원 법원경매정보 (courtauction.go.kr) 화면 표를 그대로 옮김")
    ap.add_argument("--images", nargs="*", default=[], help="뒤에 붙일 사진 파일들")
    a = ap.parse_args()

    try:
        from weasyprint import HTML, CSS as WCSS
    except ImportError:
        sys.exit("weasyprint 가 없습니다:  pip install weasyprint --break-system-packages")

    body = open(a.html_in, encoding="utf-8").read()
    title = a.title or os.path.splitext(os.path.basename(a.html_in))[0]
    saved = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    photos = "".join(img_tag(p, i + 1) for i, p in enumerate(a.images) if os.path.exists(p))
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{title}</title></head>
<body><h1>{title}</h1><div class="meta">출처: {a.source} · 저장일 {saved} · 원문과 다를 수 있으므로 입찰 전 해당 경매계에서 재확인</div>
{body}{photos}</body></html>"""
    HTML(string=doc, base_url=os.path.dirname(os.path.abspath(a.html_in))).write_pdf(a.pdf_out, stylesheets=[WCSS(string=CSS)])
    print(f"저장: {a.pdf_out} ({os.path.getsize(a.pdf_out):,} bytes)")

if __name__ == "__main__":
    main()
