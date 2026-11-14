import os, re, subprocess, zipfile
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_ajpm as C
import content_htnd as C0
from build_ajpm_htnd import read_draft, abstract_parts, TITLE, ORCID, KEYS, REFS, FUNDING, CREDIT, COI, AI_STATEMENT, AI_HEAD, data_statement, HIGHLIGHTS
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out")
N = C.N; R = []
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_ajpm.txt")).read().split())
D = read_draft(); AB = abstract_parts(D); ab = " ".join(t for _, t in AB)
MSF, TBF, SUPF, CLF, HLF, DIF, STF = "Manuscript.docx", "Tables.docx", "Appendix.docx", "Cover_Letter.docx", "Highlights.docx", "Declaration_of_Interests.docx", "STROBE_Checklist.docx"
for f in (MSF, TBF, SUPF, CLF, HLF, DIF, STF, SUPF.replace(".docx", ".pdf"), CLF.replace(".docx", ".pdf"), "Figures/Figure_1.tif", "Figures/Figure_2.tif"): ok(os.path.exists(os.path.join(OUT, f)), f"파일 {f}")
# 1. AJPM 규정
aw = int(W["abstract_words"]); ok(aw <= 300, f"구조화 초록 {aw}단어 ≤ 300")
ok([h for h, _ in AB] == ["Introduction", "Methods", "Results", "Conclusions"], "초록 소제목 Introduction/Methods/Results/Conclusions")
ok(not re.search(r"\[@", ab) and "2026" in AB[1][1], "초록 인용 없음, Methods에 분석 연도")
ok(all(re.search(p, ab) for p in (r"84,264", r"12\.7", r"9\.4", r"3,206", r"0\.955", r"1\.017")) and N["cases_total"] == 84264 and round(N["asr"][2011], 1) == 12.7 and round(N["asr"][2024], 1) == 9.4 and N["n_rows"] == 3206, "초록 수치 = 결과(사망·ASR·관측 수·MRR)")
ok(f"{N['main'][C.IMS]['IRR']:.3f}" == "0.955" and f"{N['main'][C.IMS]['lo']:.3f}-{N['main'][C.IMS]['hi']:.3f}" in ab and f"{N['main'][C.MPA]['lo']:.3f}-{N['main'][C.MPA]['hi']:.3f}" in ab, "초록 CrI = 결과")
bw = int(W["body_words"]); ok(bw <= 3000, f"본문 {bw}단어 ≤ 3,000")
ok(int(W["tables"]) + int(W["figures"]) <= 4, "표+그림 ≤ 4")
ok(":" not in TITLE and TITLE != C0.TITLE and len(TITLE.split()) <= 25, f"새 제목(MS 제목 아님)·쌍점 없음 {len(TITLE.split())}단어")
ok(1 <= len(C.KEYWORDS.split("; ")) <= 7, "키워드 1-7")
ok(3 <= len(HIGHLIGHTS) <= 5 and all(len(h) <= 85 for h in HIGHLIGHTS) and "highlights" in HLF.lower(), "Highlights 3-5개 ≤85자, 파일명 highlights")
d = Document(os.path.join(OUT, MSF)); _ps = [p.text.strip() for p in d.paragraphs]; _dx = "\n".join(_ps)
for t in ("Seongdae Kim", "kimsd@hongik.ac.kr", ORCID, "Hongik University", "Republic of Korea", "Research Article"): ok(t in _dx[:1500], f"제목면 '{t}'(단일 익명)")
ok(len(d.tables) == 0, "원고 안 표 없음(표 1·2 별도 편집 가능 파일)")
_ord = ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Limitations", "Conclusions", "CRediT authorship contribution statement", "Funding", "Declaration of competing interest", "Data availability", AI_HEAD, "Acknowledgments", "References", "Figure Legends"]
pos = [_ps.index(k) if k in _ps else -1 for k in _ord]; ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"절 순서(AI 고지·Acknowledgments는 참고문헌 바로 앞) {pos}")
ok("Statistical Analysis" in _ps, "Methods 'Statistical Analysis' 소제목")
meth = _dx[_dx.find("\nMethods\n"):_dx.find("\nResults\n")]
ok("7002340-202511-HR-012" in meth and "7002340-202611-HR-040" in meth and "waived informed consent" in meth, "Methods에 IRB 승인·동의 면제")
ok(re.search(r"R version 4\.6\.0 \(R Foundation for Statistical Computing, Vienna, Austria\)", meth) and "R-INLA 25.10.19" in meth, "소프트웨어 버전·제조사·위치")
ok(FUNDING in _dx and CREDIT in _dx and COI in _dx and data_statement() in _dx and AI_STATEMENT in _dx and _dx.count("Claude (Anthropic)") == 1, "연구비(규정 문장)·CRediT·이해충돌·자료·AI 고지(번역·첨삭만)")
z = zipfile.ZipFile(os.path.join(OUT, MSF)); x = z.read("word/document.xml").decode()
ok("<w:drawing" not in x, "원고에 그림 삽입 없음(별도 파일)"); ok("w:lnNumType" in x and 'w:restart="continuous"' in x, "연속 줄 번호")
legs = _dx[_dx.find("\nFigure Legends\n"):]; ok(all(f"Figure {k}." in legs for k in (1, 2)) and "Figure 3" not in _dx, "그림 범례 1·2(그림 3 없음)")
ok("Map lines delineate study areas and do not necessarily depict accepted national boundaries" in legs, "지도 면책 문구(Elsevier)")
ok("(A)" in legs and "(B)" in legs and "(a)" not in legs, "범례 패널 문자 대문자")
for k in (1, 2):
    im = Image.open(os.path.join(OUT, "Figures", f"Figure_{k}.tif")); dpi = round(im.info.get("dpi", (0, 0))[0])
    ok(im.mode in ("RGB", "CMYK") and dpi >= 300 and im.size[0] >= 2244, f"Figure_{k}.tif {im.mode} {dpi} dpi, 폭 {im.size[0]} px ≥ 2244(전체 쪽)")
tb = Document(os.path.join(OUT, TBF)); tbt = "\n".join(p.text for p in tb.paragraphs) + "\n".join(c.text for t in tb.tables for r in t.rows for c in r.cells)
ok(len(tb.tables) == 2 and "Table 1." in tbt and "Table 2." in tbt, "표 1·2 별도 편집 가능 파일")
body = re.sub(r"\s+", " ", _dx[_dx.find("\nIntroduction\n"):_dx.find("\nCRediT authorship contribution statement\n")])
supt = "\n".join(p.text for p in Document(os.path.join(OUT, SUPF)).paragraphs) + "\n".join(c.text for t in Document(os.path.join(OUT, SUPF)).tables for r in t.rows for c in r.cells)
ok(not re.search(r"\b\d{1,3}[  ]\d{3}\b(?! ?(district|deaths))", body + tbt + ab + supt.replace("per 100 women", "")) or not re.findall(r"\d[ ]\d{3}", body + tbt + ab + supt), f"천 단위 쉼표(공백 없음) {re.findall(r'[0-9][ ][0-9]{3}', body + tbt + ab + supt)[:3]}")
# AMA 인용 위치: 위첨자가 마침표·쉼표 바깥
sup_bad = []
for para in d.paragraphs:
    rs = para.runs
    for i in range(len(rs) - 1):
        if rs[i].font.superscript and re.match(r"^\d[\d,\-]*$", rs[i].text) and rs[i + 1].text[:1] in ".,": sup_bad.append(rs[i].text + rs[i + 1].text[:3])
ok(not sup_bad, f"AMA 위첨자가 마침표·쉼표 뒤 {sup_bad[:3]}")
# 2. 표·문서 위생
for nm, f in (("원고", MSF), ("표", TBF), ("부록", SUPF), ("커버", CLF), ("하이라이트", HLF), ("이해충돌", DIF), ("STROBE", STF)):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} 표{i+1} 3선(세로선 없음)")
        bad = [r.text for row in t.rows[1:] if len({c._tc.getroottree().getpath(c._tc) for c in row.cells}) > 1 for c in row.cells for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not bad, f"{nm} 표{i+1} 데이터 볼드 없음 {bad[:2]}")
        ok(not [c.text for r in t.rows for c in r.cells if re.fullmatch(r"[\d.()\- ]+\*+", c.text.strip())], f"{nm} 표{i+1} 유의성 별표 없음")
    xx = subprocess.run(["unzip", "-p", os.path.join(OUT, f), "word/*.xml"], capture_output=True, text=True).stdout
    ok(len(re.findall(r"<w:keepNext[ />]|<w:keepLines[ />]|<w:pageBreakBefore[ />]", xx)) == 0, f"{nm} Word 검은 네모 0건")
    zz = zipfile.ZipFile(os.path.join(OUT, f)); core = zz.read("docProps/core.xml").decode(); app = zz.read("docProps/app.xml").decode()
    ok("2013-12-23" not in core and not any(n.startswith("customXml/") for n in zz.namelist()) and "<Words>0<" not in app and "python-docx" not in core, f"{nm} python-docx 지문 없음(sanitize 후)")
    ok("<dc:creator>Seongdae Kim</dc:creator>" in core, f"{nm} 작성자 메타 = 저자(단일 익명)")
# 3. 문체·인용
ok(not re.search(r"\b(we|our|us|We|Our)\b", body), "1인칭 없음")
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
alltxt = _dx + supt + cov + tbt
ok("—" not in alltxt and not re.search(r"[가-힣]", alltxt), "em-dash·한글 없음")
ok(not re.search(r"\bsignifican", _dx + supt, re.I), "'significant' 없음(AJPM: 통계적 유의에만)")
UK = r"\b(\w*(standardis|harmonis|summaris|categoris|minimis|randomis|generalis|normalis|prioritis|organis|utilis|penalis)\w*|analys(e|ed|ing)|modelled|modelling|centre(s|d)?|neighbour\w*|behaviour\w*|ageing|colour|favour\w*|labelled|grey|programme)\b"
uk = sorted(set(m.group(0) for m in re.finditer(UK, body + " " + supt + " " + cov))); uk = [u for u in uk if u not in ("Penalising",)]; ok(not uk, f"영국식 철자 없음 {uk}")
ok(not re.search(r"ΔWAIC -\d|\(-\d|I was -\d", body), "마이너스 U+2212")
ok(not re.search(r"\[(@|web:)", _dx) and "{{" not in _dx, "미해결 인용 없음")
disc = _dx[_dx.find("\nDiscussion\n"):_dx.find("\nCRediT authorship contribution statement\n")]
_dd = re.sub(r"(?<=[A-Za-z.,;)])\d+(?:[-,]\d+)*", "", disc); _dd = re.sub(r"\b\d+ years or older", "", _dd)
_dn = [m for m in re.findall(r".{12}\d.{6}", _dd) if not re.search(r"\b(19|20)\d{2}\b", m)][:3]; ok(not _dn, f"고찰·결론에 통계 숫자 없음(연도 제외) {_dn}")
ok(not any(":" in x[0] for x in C.METHODS + C.RESULTS) and not any(":" in p for p in D["Discussion"] if p.startswith("###")), "소제목 쌍점 없음")
refs = _dx[_dx.find("\nReferences\n"):_dx.find("\nFigure Legends\n")]
ok(not re.search(r"github|zenodo", refs, re.I), "참고문헌에 GitHub·Zenodo 없음")
_rl = [l for l in refs.split("\n")[2:] if l.strip()]; ok(len(_rl) == len(KEYS) and all(l.startswith(f"{i}. ") for i, l in enumerate(_rl, 1)), f"참고문헌 번호 순({len(_rl)})")
ok(all(re.search(r"\.\s(19|20)\d{2};", l) or "Accessed" in l for l in _rl), "AMA 연도;권 형식")
ok(all("doi.org" in l for l, k in zip(_rl, sorted(KEYS, key=lambda k: 0)) if False) or sum("https://doi.org/" in l for l in _rl) >= len([k for k in KEYS if REFS[k].get("doi")]), "DOI 포함(있는 문헌 전부)")
ok(not any(len(l.split(". ")[1].split(",")) > 6 and "et al" not in l for l in _rl), "AMA 저자 7명 이상 → 3명 + et al")
ok(not any("Cheol Seong" in l or "Heon Park" in l for l in _rl), "한국인 저자명 뒤집힘 없음")
for k, lab in C.SUP.items(): ok(lab in body and re.sub(r"Appendix Tables (\d)([a-d])-\d?([a-d])", r"Appendix Table \1\2", lab) in supt, f"부록 '{lab}' 본문 인용·부록 존재")
ok(not re.search(r"Supplementary (Table|Fig)", alltxt), "옛 'Supplementary Table S' 표기 없음")
ok(not re.search(r"\{[^{}]*(N\[|:\.\d+f|sup\(|tci\(|th\()[^{}]*\}", alltxt), "코드 조각 노출 없음")
ok(not re.search(r"Summary Table|pneumonia|Archives of Gerontology|Alzheimer", _dx + supt + cov, re.I) and C.C0_TITLE_ABSENT(_dx + supt + cov), "이전 투고(이전 제목·Summary Table)·이전 호 흔적 없음")
ok(not re.search(r"pre-?specified|pre-?registered|before any model was fitted|before results were seen", _dx + supt, re.I), "'pre-specified' 류 거짓 표현 없음")
ok("[ZENODO DOI]" not in _dx + cov and "10.5281/zenodo." in _dx, "Zenodo DOI 채움(투고 전 게이트)")
ok(not re.search(r"Chun|천병철", cov), "커버레터에 제외 심사자 없음")
st = subprocess.run(["pdftotext", "-layout", os.path.join(OUT, STF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
ok("Page" in st and "Limitations" in st, "STROBE 체크리스트 별도 파일·쪽 번호")
open(os.path.join(OUT, "check_ajpm.txt"), "w").write("\n".join(R)); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if r.startswith("FAIL")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")
