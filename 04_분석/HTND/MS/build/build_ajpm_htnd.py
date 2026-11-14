# build_ajpm_htnd.py — 17호 고혈압성질환 사망 American Journal of Preventive Medicine(Elsevier, EM AJPM) Research Article 원고 조립(2026-11-14, base_htnd.py 개조).
#   Research Article = 구조화 초록 ≤300(Introduction/Methods/Results/Conclusions), 본문 ≤3,000, 표+그림 ≤4, 단일 익명(제목면 포함), 연속 줄 번호, 키워드 1-7, Highlights 3-5(≤85자, 별도 파일),
#   AMA 11판 위첨자 등장순(마침표·쉼표 바깥, 쌍점·세미콜론 안쪽), 저널명 LTWA 약어, DOI 포함, Methods에 IRB·"Statistical Analysis" 소제목·소프트웨어 버전,
#   Acknowledgments는 참고문헌 바로 앞 별도 절, AI 고지 절은 참고문헌 앞, STROBE 체크리스트 필수(별도 파일), 지도 면책 문구, 그림 별도 파일, 표는 편집 가능(별도 파일).
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Cm
from jkms_engine import JKMS
import content_htnd as C0
import content_ajpm as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_htnd.json"), encoding="utf-8")); th = C.th
DRAFT = os.path.join(MS, "draft", "01_manuscript_ajpm.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
CREDIT = "Seongdae Kim: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft, Writing - review and editing."
COI = "The author declares that there are no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper."
AI_STATEMENT = "During the preparation of this work the author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article."
AI_HEAD = "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"
def data_statement(): return f"All source data are publicly available aggregate statistics cited in the Methods. The analysis code and the scripts that generate every number, table, and figure are openly available on Zenodo (https://doi.org/{ZENODO}). The processed district-year analytic data are available from the author on reasonable request."

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def cites(t):   # AMA: 위첨자 번호는 마침표·쉼표 바깥, 쌍점·세미콜론 안쪽
    t = re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
    return re.sub(r"(\{\{[^}]+\}\})([.,])", r"\2\1", t)
def strip(t): return re.sub(r"\{\{[^}]+\}\}|<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))
def all_keys():
    src = open(os.path.join(HERE, "content_ajpm.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

sent = __import__("base_htnd").sent
def vref(k):   # AMA 11판(AJPM 예시): Surname AB, Surname CD. Title. J Abbrev. Year;vol(issue):pages. https://doi.org/...  저자 7명 이상 → 3명 + et al
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Accessed {r['accessed']}. {r['url']}; {r['year']}."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s_ = f"{a}. {t} {r['journal']}. {r['year']}"
    if r.get("vol"): s_ += f";{r['vol']}" + (f"({r['issue']})" if r.get("issue") else "") + (f":{r['pages']}" if r.get("pages") else "")
    return s_ + "." + (f" https://doi.org/{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = True   # 머리행·카테고리 행 볼드, 데이터 칸 무볼드(시리즈 규칙)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for s_ in self.doc.sections:
            for p in s_.footer.paragraphs + s_.header.paragraphs:
                pPr = p._p.get_or_add_pPr(); e = OxmlElement("w:suppressLineNumbers"); pPr.append(e)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

B = __import__("base_htnd")
TAB1_COV = [(v, l.replace("100 000", "100,000")) for v, l in B.TAB1_COV]
GROUPS = B.GROUPS; LABEL = dict(B.LABEL, physicians_per_1000="Physicians per 1,000"); SHORT = dict(B.SHORT, physicians_per_1000="Physicians per 1,000", im_specialists_per_100k="Internal medicine specialists", basic_livelihood_rate="Basic livelihood recipients", moderate_pa_rate="Moderate-or-higher physical activity"); _pct = B._pct
def table1():
    T = N["T1"]; cols = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "2011-2024"]
    rows = [["__H__", "Deaths"],
            ["  District-years, n"] + [th(T[c]['n']) for c in cols],
            ["  Deaths, n"] + [th(T[c]['cases']) for c in cols],
            ["  Person-years, million"] + [f"{T[c]['py']/1e6:.1f}" for c in cols],
            ["  Crude rate per 100,000"] + [f"{T[c]['crude']:.1f}" for c in cols],
            ["  Age-standardized rate per 100,000<sup>a</sup>"] + [f"{T[c]['asr']:.1f}" for c in cols],
            ["  District SMR, median<sup>b</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  District SMR, 10th-90th percentile<sup>b</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols],
            ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{th(T[c]['cov'][v][0], dp)} ({th(T[c]['cov'][v][1], dp)})" for c in cols])
    foot = (f"<sup>a</sup>Direct standardization to the 2015 national population in eighteen 5-year age groups; window values are means of annual rates ({N['asr_2011']:.1f} in 2011 and {N['asr_2024']:.1f} in 2024). "
            "<sup>b</sup>Observed over indirectly age-standardized expected deaths summed over the window. Hypertensive diseases, ICD-10 codes I10-I13. Characteristics not shown are in Appendix Table 1. SMR, standardized mortality ratio.")
    return ("Table 1. Deaths From Hypertensive Diseases and Selected District Characteristics by Calendar Window, Korea, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024", "2011-2024"], rows, foot)
UNITS = {"screening_suspected_hypertension_share": "%", "hypertension_treatment_rate": "%", "bp_awareness_rate": "%", "screening_abdominal_obesity_share": "%", "screening_suspected_diabetes_share": "%", "high_risk_drinking_rate": "%",
         "walking_practice_rate": "%", "moderate_pa_rate": "%", "public_sports_facilities_per_100k": " per 100,000", "basic_livelihood_rate": "%", "im_specialists_per_100k": " per 100,000", "older_single_household_share": "%",
         "urban_population_share": "%", "physicians_per_1000": " per 1,000", "sex_ratio": "", "fiscal_independence": "%", "pop80_share": "%"}
def sdlist():   # 1 SD 실제 값(AJPM: 의미 있는 단위), Table 1과 같은 2011-2024 district-year SD
    T = N["T1"]["2011-2024"]["cov"]; out = []
    for g, vs in GROUPS:
        for v in vs:
            sd = T[v][1]; dp = 1 if sd >= 1 else 2; nm = SHORT[v].lower() if v not in ("im_specialists_per_100k",) else "internal medicine specialists"
            nm = nm.replace("suspected hypertension", "suspected hypertension").replace("physicians per 1,000", "physicians")
            out.append(f"{nm} {sd:.{dp}f}{UNITS[v]}")
    return "; ".join(out)
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][("KH_typeII", v)]; z = N["s45"][("Z2_broad_outcome", v)]
            rows.append([f"  {SHORT[v]}", f"{m['IRR']:.3f} ({m['lo']:.3f}-{m['hi']:.3f})", _pct(mv["cred_frac"]) if mv else "\u2013", f"{k[0]:.3f} ({k[1]:.3f}-{k[2]:.3f})", f"{z[0]:.3f} ({z[1]:.3f}-{z[2]:.3f})"])
    SDS = sdlist()
    foot = (f"MRR, mortality rate ratio per 1 SD; CrI, credible interval. Suspected hypertension, suspected diabetes, and abdominal obesity are shares of screening attendees; treatment is among adults with diagnosed hypertension; internal medicine specialists per 100,000; older adults alone, households of older adults living alone. 1 SD (district-years, 2011-2024): {SDS}. Principal model, negative binomial with a Besag-York-Molli\u00e9 2 district effect and random-walk and independent year effects ({th(N['n_rows'])} district-years). Bounds shown as 1.000 were classified from unrounded values. "
            f"<sup>a</sup>Share of the 200 covariate-subset fits containing the characteristic in which the CrI excluded 1; \u2013, forced into every fit. "
            f"<sup>b</sup>Principal model plus a Knorr-Held type II space-time interaction allowing district-specific trends, the best-fitting interaction model. "
            f"<sup>c</sup>Principal model refitted with all circulatory deaths (I00-I99) as the outcome. "
            f"Moderate activity was credible opposite to the expected direction; post hoc checks are in Appendix Table 5.")
    return ("Table 2. District Characteristics and Hypertensive Disease Mortality, Korea, 2011-2024",
            ["Characteristic", "Principal MRR\n(95% CrI)", "Subsets\ncredible, %<sup>a</sup>", "Type II MRR\n(95% CrI)<sup>b</sup>", "Circulatory MRR\n(95% CrI)<sup>c</sup>"], rows, foot)

FIGCAP = {
 1: ("National trends in hypertensive disease mortality in Korea, 2011-2024",
     "(A) Directly age-standardized (2015 population) death rates from hypertensive diseases (I10-I13) and from all circulatory diseases (I00-I99), each indexed to 2011 = 100. (B) Share of circulatory deaths certified with a hypertensive disease as the underlying cause."),
 2: ("Residual geography of hypertensive disease mortality and of all circulatory mortality across 229 Korean districts, 2011-2024",
     "Residual spatial rate ratio by district, the posterior mean of the exponentiated Besag-York-Molli\u00e9 2 district effect, conditional on the covariates and temporal effects, for (A) hypertensive diseases (principal model) and (B) all circulatory deaths (principal model refitted with the circulatory outcome). Solid outlines, hot spots (posterior probability of a residual spatial rate ratio above 1 greater than 0.95); dashed outlines, cold spots (less than 0.05); thick lines, province boundaries; inset, Busan and Ulsan. Map lines delineate study areas and do not necessarily depict accepted national boundaries."),
}
def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=False); foot_row(J, t[3], 8); J.counting = c
ABH = ("Introduction", "Methods", "Results", "Conclusions")
def abstract_parts(D):
    P = [re.match(r"^(Introduction|Methods|Results|Conclusions):\s*(.*)$", p, re.S) for p in D["Abstract"]]
    assert [m.group(1) for m in P] == list(ABH); return [(m.group(1), m.group(2)) for m in P]

def build(bw=0, aw=0):
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim, PhD", before=6); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. E-mail: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Article type:</b> Research Article", before=6)
    J.para(f"<b>Word counts:</b> abstract {aw} words; text {th(bw)} words. <b>Tables and figures:</b> 2 tables and 2 figures. <b>References:</b> {len(KEYS)}.", before=6)
    J.page_break(); J.head("Abstract", 1)
    for h, t in abstract_parts(D): J.para(f"<b>{h}:</b> {t}")
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(cites(p), indent=True)
    J.head("Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(cites(p), indent=True)
    J.head("Conclusions", 1)
    for p in D["Conclusions"]: J.para(cites(p), indent=True)
    J.counting = False
    for h, t in (("CRediT authorship contribution statement", CREDIT), ("Funding", FUNDING), ("Declaration of competing interest", COI), ("Data availability", data_statement()),
                 (AI_HEAD, AI_STATEMENT), ("Acknowledgments", "None.")):
        J.head(h, 1); J.para(t)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for n, k in enumerate(J.cites, 1): s_ = f"{n}. {vref(k)}"; rl.append(s_); J.para(s_)
    J.raw = False
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(FIGCAP): t, c = FIGCAP[k]; J.para(f"<b>Figure {k}.</b> {t}. {c}")
    return J, rl, D

def build_tables():
    T = TX(cite="sup"); put_table(T, table1()); T.page_break(); put_table(T, table2()); return T
def docx_bw(path):   # 본문 단어 수: Introduction ~ Conclusions 끝(CRediT 직전), 표 제외
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\nIntroduction\n"):t.find("\nCRediT authorship contribution statement\n")].split())
def fix_orphans(path, heads, max_iter=10):
    from docx import Document
    fixed = set()
    for _ in range(max_iter):
        pdf = path.replace(".docx", ".pdf")
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_ajpm", "--convert-to", "pdf", "--outdir", os.path.dirname(path), path], check=True, capture_output=True)
        pages = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\f"); orphan = None
        for pg in pages:
            ls = [re.sub(r"^\d+\s+", "", l.strip()) for l in pg.split("\n") if l.strip()]; ls = [l for l in ls if not re.fullmatch(r"\d+", l)]
            if ls and ls[-1] in heads:
                k = len(ls) - 1
                while k > 0 and ls[k - 1] in heads: k -= 1
                orphan = ls[k]; break
        if orphan is None: return
        if orphan in fixed: print("orphan persists, stop:", orphan); return
        fixed.add(orphan); d = Document(path)
        for p in d.paragraphs:
            if p.text.strip() == orphan:
                np_ = OxmlElement("w:p"); r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); np_.append(r); p._p.addprevious(np_); break
        d.save(path); print("orphan fixed:", orphan)

HIGHLIGHTS = ["Age-standardized hypertensive disease mortality fell less than circulatory mortality",
              "In the principal model, all 16 Busan districts were residual hot spots",
              "Adding blood pressure care and other district indicators did not reduce the excess",
              "Busan also had excess deaths from other circulatory diseases",
              "Adjusting for ill-defined causes of death attenuated, but did not remove, the excess"]

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx"); D = read_draft()
    aw = sum(len(t.split()) for _, t in abstract_parts(D)) + 4; assert aw <= 300, aw
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl, D = build(bw, aw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw and bw <= 3000, bw
    heads = {"Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusions", "References", "Figure Legends", "Acknowledgments", "Funding", "Data availability", "CRediT authorship contribution statement", "Declaration of competing interest", AI_HEAD, "Limitations"}
    heads |= {x[0] for x in C.METHODS + C.RESULTS}
    fix_orphans(p, heads)
    T = build_tables(); T.doc_title = "Tables"; tp = os.path.join(OUT, "Tables.docx"); T.save(tp)
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_ajpm", "--convert-to", "pdf", "--outdir", OUT, tp], check=True, capture_output=True)
    assert 3 <= len(HIGHLIGHTS) <= 5 and all(len(h) <= 85 for h in HIGHLIGHTS), [len(h) for h in HIGHLIGHTS]
    K = TX(cite="sup"); K.para("<b>Highlights</b>")
    for h in HIGHLIGHTS: K.para("\u2022 " + h)
    K.doc_title = "Highlights"; K.save(os.path.join(OUT, "Highlights.docx"))
    K = TX(cite="sup"); K.para("<b>Declaration of interests</b>"); K.para(f"Manuscript: {TITLE}")
    K.para("\u2612 The author declares that there are no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.")
    K.para("Seongdae Kim, Hongik University, Seoul, Republic of Korea")
    K.doc_title = "Declaration of interests"; K.save(os.path.join(OUT, "Declaration_of_Interests.docx"))
    open(os.path.join(OUT, "wordcount_ajpm.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)} | title words {len(TITLE.split())}")
