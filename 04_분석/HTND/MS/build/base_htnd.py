#   본문 ≤4,000(초록·표·그림·참고문헌 제외), 표+그림 ≤8, 참고문헌 ≤35(Vancouver, 저자 6명 초과 시 6명 + et al.), Summary Table(What is known about topic / What this study adds),
#   2줄 간격·넓은 여백, 모든 쪽·줄 번호, 천 단위 공백, 표는 편집 가능한 별도 파일, 그림 별도 파일, 그림 범례는 참고문헌 뒤 별도 쪽,
#   필수 절: Data Availability Statement·References·Acknowledgments·Author Contributions·Funding·Ethical Approval·Competing Interests, LLM 사용은 Methods에 기재.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Cm
from jkms_engine import JKMS
import content_htnd as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_htnd.json"), encoding="utf-8")); th = C.th; NB = C.NB
DRAFT = os.path.join(MS, "draft", "01_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."
CONTRIB = "SK conceived and designed the study, acquired and analyzed the data, interpreted the results, wrote the manuscript, and is the sole author."
COI = "Conflict of interest statement. The author declares no competing interests."
ETHICS = "The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012) and its continuing review on November 3, 2026 (7002340-202611-HR-040), and waived informed consent because only published aggregate statistics were used."
def data_statement(): return f"All source data are publicly available from the statistics cited in the Methods. The analysis code and the scripts that generate every number, table, and figure are archived on Zenodo (https://doi.org/{ZENODO}); the files are restricted during peer review, are accessible to editors and reviewers through a private link provided with the submission, and will be made public on acceptance. The processed district-year analytic data are available from the author on reasonable request."

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)   # 위첨자 번호(앞 공백 없음)
def strip(t): return re.sub(r"\{\{[^}]+\}\}|<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))
def all_keys():
    src = open(os.path.join(HERE, "content_htnd.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys(); assert len(KEYS) <= 35, len(KEYS)

KEEP = {"Korea", "Korean", "South", "United", "States", "US", "USA", "UK", "Busan", "Seoul", "Bayesian", "Laplace", "Gaussian", "Besag", "Knorr-Held", "INLA", "BYM2", "COVID-19", "STROBE", "GBD",
        "ICD-10", "Australia", "Spain", "Murcia", "REGARDS", "Spatial+", "Republic"}
def sent(t):   # 참고문헌 제목 문장형 통일(build_agg_pneu.sent 복제)
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for i, x in enumerate(w[1:], 1):
        core = x.strip("(),:;.?[]")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?")) or (core.split("-")[0] in KEEP)
        if not keep: x = x[:1].lower() + x[1:]
        x = "-".join([x.split("-")[0]] + [y if (y in KEEP or y.isupper()) else y[:1].lower() + y[1:] for y in x.split("-")[1:]])
        out.append(x)
    t2 = " ".join(out)
    for ph in ("Atherosclerosis Risk in Communities Study", "Reasons for Geographic and Racial Differences in Stroke", "Global Burden of Disease Study"): t2 = re.sub(ph, ph, t2, flags=re.I)
    t2 = re.sub(r"\bGarbage Code\b", "garbage code", t2)
    return t2
def vref(k):
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. {r['year']}. {r['url']}. Accessed {r['accessed']}."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:6]) + ", et al"
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!", "]")) else ".")
    if t.endswith("]"): t += "."
    s_ = f"{a}. {t} {r['journal']}. {r['year']}"
    if r.get("vol"): s_ += f"; {r['vol']}" + (f":{r['pages']}" if r.get("pages") else "")
    s_ = s_.replace("-", "\u2013") if False else s_
    return s_ + "." + ("" if r.get("pages") else f" https://doi.org/{r['doi']}.")

class TX(JKMS):
    raw = False; table_bold = True   # 머리행·카테고리 행 볼드, 데이터 칸 무볼드(시리즈 규칙)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for s_ in self.doc.sections:   # 머리·바닥글 줄번호 억제(10호 교훈: LibreOffice가 빈 바닥글에 번호)
            for p in s_.footer.paragraphs + s_.header.paragraphs:
                pPr = p._p.get_or_add_pPr(); e = OxmlElement("w:suppressLineNumbers"); pPr.append(e)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        text = re.sub(r"(?<=\d) (?=\d{3}\b)", "\u00a0", text)
        return super()._emit(p, text, sz, bold, italic)

TAB1_COV = [("pop80_share", "Population aged 80 years or older, %"), ("urban_population_share", "Urban population share, %"),
            ("screening_suspected_hypertension_share", "Suspected hypertension on screening, %"), ("hypertension_treatment_rate", "Treatment among diagnosed hypertension, %"),
            ("bp_awareness_rate", "Blood pressure awareness, %"), ("screening_abdominal_obesity_share", "Abdominal obesity on screening, %"),
            ("moderate_pa_rate", "Moderate-or-higher physical activity, %"), ("basic_livelihood_rate", "Basic livelihood recipients, %"), ("im_specialists_per_100k", "Internal medicine specialists per 100 000")]
def table1():
    T = N["T1"]; cols = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "2011-2024"]
    rows = [["__H__", "Deaths"],
            ["  District-years, n"] + [th(T[c]['n']) for c in cols],
            ["  Deaths, n"] + [th(T[c]['cases']) for c in cols],
            ["  Person-years, million"] + [f"{T[c]['py']/1e6:.1f}" for c in cols],
            ["  Crude rate per 100 000"] + [f"{T[c]['crude']:.1f}" for c in cols],
            ["  Age-standardized rate per 100 000<sup>a</sup>"] + [f"{T[c]['asr']:.1f}" for c in cols],
            ["  District SMR, median<sup>b</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  District SMR, 10th-90th percentile<sup>b</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols],
            ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{th(T[c]['cov'][v][0], dp)} ({th(T[c]['cov'][v][1], dp)})" for c in cols])
    foot = (f"<sup>a</sup>Direct standardization to the 2015 national population in eighteen 5-year age groups; window values are means of annual rates ({N['asr_2011']:.1f} in 2011 and {N['asr_2024']:.1f} in 2024). "
            "<sup>b</sup>Observed over indirectly age-standardized expected deaths summed over the window. Hypertensive diseases, International Classification of Diseases, 10th revision, I10-I13. Characteristics not shown are in Supplementary Table S1. SD, standard deviation; SMR, standardized mortality ratio.")
    return ("Table 1. Deaths from hypertensive diseases and selected district characteristics by calendar window, Korea, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024", "2011-2024"], rows, foot)

GROUPS = [("Blood pressure care", ["screening_suspected_hypertension_share", "hypertension_treatment_rate", "bp_awareness_rate"]),
          ("Cardiometabolic risk", ["screening_abdominal_obesity_share", "screening_suspected_diabetes_share", "high_risk_drinking_rate"]),
          ("Physical activity", ["walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k"]),
          ("Structure and access", ["basic_livelihood_rate", "im_specialists_per_100k", "older_single_household_share"]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {"screening_suspected_hypertension_share": "Suspected hypertension (screening)", "hypertension_treatment_rate": "Treatment among diagnosed", "bp_awareness_rate": "Blood pressure awareness",
         "screening_abdominal_obesity_share": "Abdominal obesity (screening)", "screening_suspected_diabetes_share": "Suspected diabetes (screening)", "high_risk_drinking_rate": "High-risk drinking",
         "walking_practice_rate": "Walking practice", "moderate_pa_rate": "Moderate-or-higher physical activity", "public_sports_facilities_per_100k": "Public sports facilities",
         "basic_livelihood_rate": "Basic livelihood recipients", "im_specialists_per_100k": "Internal medicine specialists", "older_single_household_share": "Older adults living alone",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1 000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged 80 years or older"}
SHORT = dict(LABEL, screening_suspected_hypertension_share="Suspected hypertension", hypertension_treatment_rate="Treatment, diagnosed", screening_abdominal_obesity_share="Abdominal obesity",
             screening_suspected_diabetes_share="Suspected diabetes", moderate_pa_rate="Moderate activity", public_sports_facilities_per_100k="Sports facilities",
             basic_livelihood_rate="Livelihood recipients", im_specialists_per_100k="Internist density", older_single_household_share="Older adults alone",
             pop80_share="Aged 80 years or older")
from decimal import Decimal, ROUND_HALF_UP
_pct = lambda f: str(int(Decimal(str(round(100 * f, 6))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][("KH_typeII", v)]; z = N["s45"][("Z2_broad_outcome", v)]
            rows.append([f"  {SHORT[v]}", f"{m['IRR']:.3f} ({m['lo']:.3f}-{m['hi']:.3f})", _pct(mv["cred_frac"]) if mv else "\u2013", f"{k[0]:.3f} ({k[1]:.3f}-{k[2]:.3f})", f"{z[0]:.3f} ({z[1]:.3f}-{z[2]:.3f})"])
    foot = (f"MRR, mortality rate ratio per 1 standard deviation; CrI, credible interval. Suspected hypertension, suspected diabetes, and abdominal obesity are shares of screening attendees; moderate activity, moderate-or-higher-intensity physical activity; treatment is among adults with diagnosed hypertension; internist density, internal medicine specialists per 100 000; livelihood recipients, basic livelihood security recipients; older adults alone, households of older adults living alone. Principal model, negative binomial with a Besag-York-Molli\u00e9 2 district effect and random-walk and independent year effects ({th(N['n_rows'])} district-years). Bounds shown as 1.000 were classified from unrounded values. "
            f"<sup>a</sup>Share of the 200 covariate-subset fits containing the characteristic in which the CrI excluded 1; \u2013, forced into every fit. "
            f"<sup>b</sup>Principal model plus a Knorr-Held type II space-time interaction allowing district-specific trends, the best-fitting interaction model. "
            f"<sup>c</sup>Principal model refitted with all circulatory deaths (I00-I99) as the outcome. "
            f"Moderate activity was credible opposite to the expected direction; post hoc checks are in Supplementary Table S5.")
    return ("Table 2. District characteristics and hypertensive disease mortality, Korea, 2011-2024",
            ["Characteristic", "Principal MRR\n(95% CrI)", "Subsets\ncredible, %<sup>a</sup>", "Type II MRR\n(95% CrI)<sup>b</sup>", "Circulatory MRR\n(95% CrI)<sup>c</sup>"], rows, foot)

FIGCAP = {
 1: "National trends in hypertensive disease mortality in Korea, 2011-2024. (a) Directly age-standardized (2015 population) death rates from hypertensive diseases (I10-I13) and from all circulatory diseases (I00-I99), each indexed to 2011 = 100. (b) Share of circulatory deaths certified with a hypertensive disease as the underlying cause.",
 2: "Residual geography of hypertensive disease mortality and of all circulatory mortality across 229 Korean districts, 2011-2024. Residual spatial rate ratio by district, the posterior mean of the exponentiated Besag-York-Molli\u00e9 2 district effect, that is, the district mortality ratio not explained by the covariates, for (a) hypertensive diseases (principal model) and (b) all circulatory deaths (principal model refitted with the circulatory outcome). Solid outlines, hot spots (posterior probability of a residual spatial rate ratio above 1 greater than 0.95); dashed outlines, cold spots (less than 0.05); thick lines, province boundaries; inset, Busan and Ulsan. Map lines delineate study areas and do not necessarily depict accepted national boundaries.",
 3: "Mortality rate ratios per 1 standard deviation with 95% credible intervals for internal medicine specialists, moderate-or-higher physical activity, and basic livelihood recipients: principal model; Knorr-Held type II and type IV space-time interactions, which allow district-specific trends; province-by-year effects; principal model with the ill-defined cause share; all circulatory deaths as the outcome; and the within-district (two-way-centered) component for physical activity. The dotted vertical line marks a ratio of 1.",
}
def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=False); foot_row(J, t[3], 8); J.counting = c

def summary_table(J):
    D = read_draft()["Summary Table"]; blocks = []; cur = None
    for p in D:
        for line in p.split("\n"):
            line = line.strip()
            if not line: continue
            if line.startswith("- "): blocks[-1][1].append(line[2:])
            else: blocks.append((line, []))
    assert [b[0] for b in blocks] == ["What is known about the topic", "What this study adds"] and all(2 <= len(b[1]) <= 3 for b in blocks)
    rows = []
    for i, (h, items) in enumerate(blocks):
        if i: rows.append(["__H__", h])
        rows += [[f"\u2022 {x}"] for x in items]
    c = J.counting; J.counting = False; J.table("", [blocks[0][0]], rows, [15.9], "", fs=11, title_bold=False); J.counting = c

def build(bw=0, aw=0):
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim", before=6)
    J.para(ADDRESS)
    J.para(f"<b>Correspondence:</b> Seongdae Kim, {ADDRESS}. E-mail: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para(f"<b>Word counts:</b> abstract {aw} words; main text {th(bw)} words. <b>References:</b> {len(KEYS)}. <b>Tables and figures:</b> 2 tables and 3 figures.", before=6)
    J.page_break(); J.head("Abstract", 1)
    for p in D["Abstract"]: J.para(p)
    J.page_break(); J.head("Summary Table", 1); summary_table(J)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(cites(p), indent=True)
    J.head("Materials and Methods", 1)
    for h, p in C.METHODS: J.head(h, 2); J.para(cites(p), indent=True)
    J.head("Results", 1)
    for h, p in C.RESULTS: J.head(h, 2); J.para(cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(cites(p), indent=True)
    J.counting = False
    J.head("Data Availability Statement", 1); J.para(data_statement())
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); rl = []
    for n, k in enumerate(J.cites, 1): s_ = f"{n}. {vref(k)}"; rl.append(s_); J.para(s_)
    for h, t in (("Competing Interests", COI), ("Acknowledgments", "None."), ("Author Contributions", CONTRIB), ("Funding", FUNDING), ("Ethical Approval", ETHICS)):
        J.head(h, 1); J.para(t)
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Fig. {k}</b> {FIGCAP[k]}")
    return J, rl, D

def build_tables():
    T = TX(cite="sup"); put_table(T, table1()); T.page_break(); put_table(T, table2()); return T

def docx_bw(path):   # 본문 단어 수: Introduction ~ Discussion 끝(Data Availability 직전), 표 제외
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\nIntroduction\n"):t.find("\nData Availability Statement\n")].split())
def fix_orphans(path, heads, max_iter=20):
    from docx import Document
    for _ in range(max_iter):
        pdf = path.replace(".docx", ".pdf")
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_ms", "--convert-to", "pdf", "--outdir", os.path.dirname(path), path], check=True, capture_output=True)
        pages = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\f"); orphan = None
        for pg in pages:
            ls = [re.sub(r"^\d+\s+", "", l.strip()) for l in pg.split("\n") if l.strip()]; ls = [l for l in ls if not re.fullmatch(r"\d+", l)]
            if ls and ls[-1] in heads:
                orphan = ls[-2] if len(ls) >= 2 and ls[-2] in heads else ls[-1]   # 제목 두 개가 연달아 쪽 끝이면 위 제목 앞에서 나눔
                break
        if orphan is None: return
        d = Document(path)
        for p in d.paragraphs:
            if p.text.strip() == orphan:
                r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); p._p.insert(1 if p._p.pPr is not None else 0, r); break
        d.save(path); print("orphan fixed:", orphan)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_MS_HTND.docx"); D = read_draft()
    aw = sum(len(strip(x).split()) for x in D["Abstract"]); assert aw <= 250, aw
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl, D = build(bw, aw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw and bw <= 3950, bw
    heads = {"Abstract", "Summary Table", "References", "Figure Legends", "Acknowledgments", "Author Contributions", "Funding", "Ethical Approval", "Competing Interests", "Data Availability Statement", "Introduction", "Materials and Methods", "Results", "Discussion"}
    heads |= {x[4:].strip() for x in D["Discussion"] if x.startswith("### ")} | {h for h, _ in C.METHODS} | {h for h, _ in C.RESULTS}
    fix_orphans(p, heads)
    T = build_tables(); T.doc_title = "Tables"; tp = os.path.join(OUT, "Tables_MS_HTND.docx"); T.save(tp)
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_ms", "--convert-to", "pdf", "--outdir", OUT, tp], check=True, capture_output=True)
    open(os.path.join(OUT, "wordcount_ms.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=3\ntitle_chars={len(TITLE)}\n")
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)} | title chars {len(TITLE)}")
