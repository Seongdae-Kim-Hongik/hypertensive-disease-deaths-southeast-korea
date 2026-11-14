# cover_ajpm.py — 17호 고혈압성질환 사망 American Journal of Preventive Medicine 커버레터(2026-11-14, cover_htnd.py 개조). 단독 저자 비인칭, 미국식, 1쪽, 서명 = 김성대(체육 시리즈 단독·교신).
#  자료 중복 고지·이전 투고 언급 금지, 제외 심사자는 포털 칸에만(커버레터 금지), IRB 번호 포함, Zenodo 공개(open) DOI.
import os, re, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_ajpm as C
from build_ajpm_htnd import TITLE as DTITLE, ZENODO, ADDRESS
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out")
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_ajpm.txt")).read().split()); th = C.th
assert ZENODO.startswith("10.5281/zenodo."), "Zenodo DOI 없음(투고 전 게이트)"
assert N["busan_hot"] == 16 and N["broad_hot_busan"] == 16 and N["asr_ratio"] < 1 and not any(N["s43"][("KH_typeII", v)][3] for v in (C.MPA, C.IMS))
_d = datetime.date.today(); cl = [f"{_d:%B} {_d.day}, {_d.year}", "The Editor-in-Chief", "American Journal of Preventive Medicine", "",
      "Dear Editor,",
      f"Please find enclosed the manuscript entitled \"{DTITLE}\" by Seongdae Kim, for consideration as a Research Article in the American Journal of Preventive Medicine.",
      f"Hypertensive disease mortality is often read as a marker of how well blood pressure is detected and controlled. Using complete national death registration for all {N['n_districts']} Korean districts in 2011-2024 ({th(N['cases_total'])} deaths from hypertensive diseases), indirect standardization in eighteen age groups, and Bayesian spatiotemporal models, this study shows that age-standardized hypertensive disease mortality fell less than circulatory mortality as a whole, that all 16 districts of Busan had excess mortality after adjustment, and that adding district averages of screening blood pressure, treatment, awareness, cardiometabolic risk, physical activity, and public assistance did not reduce this excess. Refits to circulatory deaths showed that every Busan district remained a hot spot for circulatory deaths excluding hypertensive diseases, whereas adjustment for the lower share of ill-defined causes of death in Busan attenuated the excess.",
      "The work fits the journal's emphasis on the primary and secondary prevention of chronic disease, including physical activity: it identifies districts where blood pressure control among older adults and the certification of circulatory deaths warrant closer examination, and the findings suggest that hypertensive disease mortality should be interpreted alongside broader circulatory mortality and information on cause-of-death recording when prevention priorities are set. The study used only published aggregate statistics with approval of the Institutional Review Board of Hongik University (7002340-202611-HR-040, continuing review of 7002340-202511-HR-012).",
      "The manuscript is original research, has not been published previously, and is not under consideration for publication elsewhere; the author has approved its submission. The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript.",
      f"The text contains {th(int(W['body_words']))} words, with a structured abstract of {int(W['abstract_words'])} words, two tables, two figures, and {W['refs']} references. Highlights, an Appendix, and the STROBE checklist are provided. The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}).",
      "Thank you for considering this manuscript.", "", "Sincerely,", "",
      "Seongdae Kim, PhD (corresponding author)", ADDRESS, "Email: kimsd@hongik.ac.kr"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
gap = False
for t in cl:
    if t == "": gap = True; continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_cl_ajpm", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and re.search(r"7002340-202611-?\s*HR-040", txt) and not re.search(r"(?i)funding|competing|overlap|previously submitted|Chun", txt) and C.C0_TITLE_ABSENT(txt), "문체·IRB·금지 항목"
pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout).group(1)); assert pages == 1, pages
print("saved", fp)
