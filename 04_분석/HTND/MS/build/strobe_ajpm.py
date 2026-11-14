# strobe_ajpm.py — 17호 AJPM STROBE 체크리스트(별도 파일, 쪽 번호 포함; AJPM: 관찰연구 STROBE 필수·현행 양식처럼 쪽 번호 칸). 원고 PDF에서 절 제목의 쪽을 찾아 넣는다(2026-11-14).
import os, re, subprocess
from build_ajpm_htnd import TX, foot_row, TITLE
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out")
pages = subprocess.run(["pdftotext", "-layout", os.path.join(OUT, "Manuscript.pdf"), "-"], capture_output=True, text=True).stdout.split("\f")
def pg(head, nth=0):
    hits = [i + 1 for i, p in enumerate(pages) for l in p.split("\n") if re.sub(r"^\s*\d+\s+", "", l).strip() == head]
    assert hits, head; return str(hits[nth])
def pgs(*hs): return ", ".join(sorted({pg(h) for h in hs}, key=int))
T1 = "Tables file (Table 1)"; T2 = "Tables file (Table 2)"
CK = [
 ("Title and abstract", "1", "(a) Study design indicated in the abstract; (b) informative and balanced summary", f"{pg('Abstract')}"),
 ("Background/rationale", "2", "Scientific background and rationale", pg("Introduction")),
 ("Objectives", "3", "Specific objectives", pg("Introduction")),
 ("Study design", "4", "Key elements of study design (ecological study of 229 districts)", pg("Study Design and Data Sources")),
 ("Setting", "5", "Setting, locations, periods of data collection", pg("Study Design and Data Sources")),
 ("Participants", "6", "Eligibility (all registered deaths; resident populations of all districts)", pg("Study Design and Data Sources")),
 ("Variables", "7", "Outcome, exposures, confounders, and effect modifiers defined", pgs("Measures") + "; Appendix Table 1"),
 ("Data sources/measurement", "8", "Sources and methods of measurement", pgs("Study Design and Data Sources", "Measures") + "; Appendix Methods"),
 ("Bias", "9", "Efforts to address potential sources of bias", pgs("Statistical Analysis") + "; Appendix Tables 3-5"),
 ("Study size", "10", "Study size (all 229 districts, 3,206 district-years)", pg("Study Design and Data Sources")),
 ("Quantitative variables", "11", "Handling of quantitative variables (per 1 SD)", pg("Measures")),
 ("Statistical methods", "12", "(a) Statistical methods; (b) subgroups and interactions; (c) missing data; (e) sensitivity analyses", pg("Statistical Analysis") + "; Appendix Methods"),
 ("Participants", "13", "Not applicable (aggregate district data; no exclusions)", "-"),
 ("Descriptive data", "14", "Characteristics of the study population", pg("Deaths, Trends, and Certification") + "; " + T1),
 ("Outcome data", "15", "Numbers of outcome events", pg("Deaths, Trends, and Certification") + "; " + T1),
 ("Main results", "16", "Estimates with 95% credible intervals; confounders adjusted for", pgs("District Characteristics", "Robustness") + "; " + T2 + "; Figures 1-2"),
 ("Other analyses", "17", "Sensitivity analyses", pgs("Robustness", "Certification Checks") + "; Appendix Tables 3-6; Appendix Figure 2"),
 ("Key results", "18", "Key results with reference to objectives", pg("Discussion")),
 ("Limitations", "19", "Limitations, sources of bias and imprecision", pg("Limitations")),
 ("Interpretation", "20", "Cautious overall interpretation", pgs("Discussion", "Conclusions")),
 ("Generalizability", "21", "External validity", pg("Limitations")),
 ("Funding", "22", "Source of funding", pg("Funding")),
]
J = TX(cite="sup"); J.para("<b>STROBE Statement checklist (observational studies)</b>"); J.para(f"Manuscript: {TITLE}")
J.table_fit("Page numbers refer to the manuscript file", ["Section/topic", "Item", "Recommendation", "Page"], [list(x) for x in CK], "", fs_max=8, title_bold=False)
foot_row(J, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology. Ecological design: the units of analysis are districts, not individuals.", 8, 12)
p = os.path.join(OUT, "STROBE_Checklist.docx"); J.doc_title = "STROBE checklist"; J.save(p)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_strobe", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
print("saved", p, [x[3] for x in CK])
