# esm_ajpm.py — 17호 AJPM 부록(Appendix Methods·Appendix Table 1-6·Appendix Figure 1-2), esm_htnd.py 변환(2026-11-14). STROBE는 별도 파일(strobe_ajpm.py).
import os, re, json, subprocess, pandas as pd
from docx.shared import Cm
from docx.oxml.ns import qn
import content_htnd as C
from numbers_htnd import _UNK
from build_ajpm_htnd import LABEL, GROUPS, TX, TITLE as DTITLE, foot_row, read_draft
import content_ajpm as CA
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
N = C.N; th = CA.th
st = lambda t: f"{t[0]:.3f} ({t[1]:.3f}-{t[2]:.3f})"
J = TX(cite="sup")
for _s in J.doc.sections:   # 06 §9-F: 보충자료는 줄번호 없음
    _ln = _s._sectPr.find(qn("w:lnNumType"))
    if _ln is not None: _s._sectPr.remove(_ln)
def TF(title, header, rows, foot="", fs=8):
    J.page_break(); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=False)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Appendix (Supplemental Material)</b>"); J.para(f"Manuscript: {DTITLE}")
J.para("Contents: Appendix Methods and additional results; Appendix Tables 1-6; Appendix Figures 1-2.")
_LK = C._LK; _MT = pd.read_csv(os.path.join(B, "panel_META_HTND_std3.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
assert int(_MT.loc["older_single_household_share", "obs_year_min"]) == 2015 and int(_MT.loc["screening_abdominal_obesity_share", "obs_year_min"]) == 2013 and int(_MT.loc["low_salt_preference_rate", "obs_year_max"]) == 2019
gate = open(os.path.join(B, "data_gate_HTND_std3_261108.txt"), encoding="utf-8").read(); nwarn = int(re.search(r"경고 (\d+)건", gate).group(1))
assert "전 연도 0인 지역" not in gate
CS = N["circ_share"]
J.page_break(); J.head("Appendix Methods and additional results", 2)
SM = [("Outcome.", "Annual deaths with a hypertensive disease as the underlying cause (International Classification of Diseases, 10th revision, I10 essential hypertension, I11 hypertensive heart disease, I12 hypertensive kidney disease, I13 hypertensive heart and kidney disease) by district of residence came from the cause-of-death statistics of Statistics Korea (deaths by cause, sex, and district). Deaths are attributed to the district of the registered address at death. The circulatory outcome comprised all deaths with an underlying cause in I00-I99 from the same tables."),
      ("Expected deaths.", f"National deaths from hypertensive diseases (and, for the circulatory outcome, from all circulatory diseases) by 5-year age group (0-4 to 80-84 years and 85 years or older, both sexes combined) came from the national cause-of-death table by cause, sex, and age. Deaths with unknown age ({_UNK} in 14 years) were excluded from the age-specific rates. District age structures came from resident registration statistics. Expected deaths summed nationally to observed deaths each year. Districts were harmonized to 229 units with 2024 boundaries; the 2023 population of Changwon, which duplicated the 2022 age block in the source file, was replaced with the official total. The sex-and-age sensitivity analysis used national death rates by sex and age group and district populations by sex."),
      ("Covariates.", "Community Health Survey indicators are district age-standardized estimates from adults aged 19 years or older (treatment among diagnosed hypertension and diagnosis among adults aged 30 years or older). Suspected hypertension and suspected diabetes are the shares of adults attending the National Health Insurance Service general health screening with measured blood pressure or fasting glucose in the suspected-disease range, among those not already classified as under treatment; abdominal obesity is the screening share with high waist circumference (reported from 2013). Internal medicine specialists and basic livelihood recipients came from a harmonized public district panel built from official statistics; three implausible recipient values for Changwon in 2021-2023 were set to missing and interpolated. Low-salt preference, the share of adults who prefer less salty food, was surveyed only until 2019 and was therefore used only in a sensitivity analysis restricted to 2011-2019. Missing years were filled by interpolation within districts and then by district means."),
      ("Panel checks before modeling.", f"An automated gate run on the analytic panel reported {nwarn} flags (Appendix Table 2). Most flagged standardized columns whose yearly means were near 0 (a ratio artifact) or the post-2020 indicator (constant by design); the sex ratio exceeds 100 by definition (men per 100 women). No covariate was zero in every year in any district or needed filling with national yearly means."),
      ("Models.", f"Software: R 4.6.0 with R-INLA; Python 3.9 for data preparation and figures. The negative binomial likelihood was chosen because its widely applicable information criterion (WAIC) for the forced-controls model was lower than that of a Poisson likelihood ({th(_LK['nbinomial'],1)} vs {th(_LK['poisson'],1)}). The Besag-York-Mollié 2 district effect used penalized-complexity priors (standard deviation above 0.5 with probability 0.01; mixing parameter below 0.5 with probability 2/3) on a contact graph of 593 district pairs with island links. Year effects were a first-order random walk plus an independent term. Covariate subsets (200) were drawn at random with the forced controls in every fit. E-values were computed for the subset-stable characteristic; for moderate-or-higher physical activity the E-value was {N['evalue']['moderate_pa_rate']['E_point']:.2f} for the point estimate and {N['evalue']['moderate_pa_rate']['E_limit']:.2f} for the credible interval limit. Variance partitioning used posterior means of each component's contribution to the linear predictor; shares of the summed variances do not add to the total variance because components covary."),
      ("Death certification checks.", "The principal model was refitted (i) with the share of deaths from ill-defined causes (R00-R99) among all deaths added, (ii) with all circulatory deaths (I00-I99) as the outcome and expected deaths from national circulatory death rates in the same age groups, (iii) with the circulatory outcome and the ill-defined cause share, and (iv) with the out-of-district outpatient share added. District residual spatial rate ratios from the principal and circulatory models were compared by Spearman correlation and by hot spot classification."),
      ("Post hoc checks of the association opposite to the expected direction.", "After the principal results were seen, moderate-or-higher physical activity was fitted with the forced controls alone and without the other physical activity characteristics (walking practice and sports facilities), and all three physical activity characteristics were removed together for comparison.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
_ALT14_EARLY = [{"B3_smooth_forced": "smoothed forced controls", "C1_poisson_lognormal": "Poisson with an observation-level effect", "C2_rw2_year": "second-order random-walk year effect", "C3_ar1_year": "first-order autoregressive year effect", "C4_sido_year_iid": "province-by-year effect", "D1_spatial_plus": "Spatial+-type adjustment", "E0_nolag_from2012": "no lag with years from 2012", "E0_nolag_from2013": "no lag with years from 2013", "E1_lag1": "1-year lag", "E2_lag2": "2-year lag", "F3_extreme_R7": "extreme values refilled", "G1_kchs_ma3": "3-year survey averages", "H4_odd_years": "odd years", "H4_even_years": "even years"}[a] for a in N["alt14"]]
_tc = N["type_class"]; _eh = N["ehsa"]
J.para("<b>Alternative specifications.</b> The fourteen alternative specifications counted in the main text were: " + ", ".join(_ALT14_EARLY) + ".")
J.para("<b>Additional results.</b> " + f"Hypertensive diseases accounted for {100*CS[2011]:.1f}% of circulatory deaths in 2011 and {100*CS[2024]:.1f}% in 2024. Residual spatial rate ratios correlated with northing (Spearman's ρ {N['lat_rr']:.2f}) and easting (ρ {N['lon_rr']:.2f}) and with unadjusted smoothed ratios (ρ {N['rr_eb']:.2f}); unadjusted smoothed ratios correlated weakly with basic livelihood recipients (ρ {N['eb_bls']:.2f}). "
       f"Hot spots comprised {_tc['hotspot']['ward']} urban wards, {_tc['hotspot']['city']} cities, and {_tc['hotspot']['county']} counties; cold spots {_tc['coldspot']['ward']}, {_tc['coldspot']['city']}, and {_tc['coldspot']['county']}. With stricter thresholds (posterior probability above 0.975 or 0.99), {N['hot_strict'][0.975][0]} and {N['hot_strict'][0.99][0]} districts were hot spots. "
       f"Emerging hot spot analysis classified {_eh['Consecutive hot']} districts as consecutive and {_eh['Sporadic hot']} as sporadic hot spots and {_eh['No pattern']} as showing no pattern. Window-specific hot spots numbered {N['win_hot']['W1_2011-15']}, {N['win_hot']['W2_2016-19']}, and {N['win_hot']['W3_2020-24']}; the {N['hot_all_windows']} districts that were hot spots in all three windows are described in the note to Appendix Figure 1. "
       f"The post-2020 period was not associated with a change in mortality (MRR {N['covid_main'][0]:.3f}; 95% credible interval {N['covid_main'][1]:.3f} to {N['covid_main'][2]:.3f}). Leaving out one province at a time, moderate-or-higher physical activity was credible in " + f"{sum(1 for k,t in N['s41'].items() if k[0].startswith('F1_') and k[1]=='moderate_pa_rate' and t[3])} of {sum(1 for k in N['s41'] if k[0].startswith('F1_') and k[1]=='moderate_pa_rate')} fits and internal medicine specialists in {sum(1 for k,t in N['s41'].items() if k[0].startswith('F1_') and k[1]=='im_specialists_per_100k' and t[3])}; leaving out one year, in {sum(1 for k,t in N['s41'].items() if k[0].startswith('F2_') and k[1]=='moderate_pa_rate' and t[3])} and {sum(1 for k,t in N['s41'].items() if k[0].startswith('F2_') and k[1]=='im_specialists_per_100k' and t[3])} of {sum(1 for k in N['s41'] if k[0].startswith('F2_') and k[1]=='moderate_pa_rate')} fits. With filled values perturbed 20 times, physical activity was credible in {int(N['rubin']['moderate_pa_rate']['n_cred'])} fits (pooled MRR {N['rubin']['moderate_pa_rate']['IRR_pooled']:.3f}; 95% credible interval {N['rubin']['moderate_pa_rate']['lo']:.3f} to {N['rubin']['moderate_pa_rate']['hi']:.3f}). " + f"Posterior predictive 50% and 95% intervals covered {100*N['ppc']['coverage50']:.1f}% and {100*N['ppc']['coverage95']:.1f}% of district-years; the probability integral transform departed from uniformity (Kolmogorov-Smirnov P < 0.001), so tail calibration should be interpreted cautiously.")
# ── Table S1 ──
DIR = {"screening_suspected_hypertension_share": "+", "hypertension_treatment_rate": "−", "bp_awareness_rate": "−", "screening_abdominal_obesity_share": "+", "screening_suspected_diabetes_share": "+",
       "high_risk_drinking_rate": "+", "walking_practice_rate": "−", "moderate_pa_rate": "−", "public_sports_facilities_per_100k": "−", "basic_livelihood_rate": "+", "im_specialists_per_100k": "−", "older_single_household_share": "+"}   # sets_HTND_std3.json
SRC = {"kchs": "Survey", "chk": "Screening", "eloc": "KOSIS", "fac": "Registry"}
EXT = {"ext__pop80_share": "Registry", "ext__basic_livelihood_rate": "Panel", "ext__im_specialists_per100k": "Panel"}
UNIT = {"screening_suspected_hypertension_share": "% screened", "hypertension_treatment_rate": "% diagnosed", "bp_awareness_rate": "%", "screening_abdominal_obesity_share": "% screened", "screening_suspected_diabetes_share": "% screened",
        "high_risk_drinking_rate": "%", "walking_practice_rate": "%", "moderate_pa_rate": "%", "public_sports_facilities_per_100k": "per 100,000", "basic_livelihood_rate": "%", "im_specialists_per_100k": "per 100,000",
        "older_single_household_share": "% households", "urban_population_share": "%", "physicians_per_1000": "per 1,000", "sex_ratio": "ratio", "fiscal_independence": "%", "pop80_share": "%"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; sc = str(m.source_column); src = EXT.get(sc, SRC.get(sc.split("__")[0], sc.split("__")[0]))
        rows.append([f"  {LABEL[v]}", UNIT[v], src, f"{int(m.obs_year_min)}-{int(m.obs_year_max)}", ("Forced" if m.role == "forced" else DIR[v]), th(_imp(v))])
m = _MT.loc["low_salt_preference_rate"]; rows += [["__H__", "Sensitivity analysis only"], ["  Low-salt preference", "%", "Survey", f"{int(m.obs_year_min)}-{int(m.obs_year_max)}", "−", th(_imp("low_salt_preference_rate"))]]
TF("Appendix Table 1. Source, unit, observed years, expected direction, and filled cells for each district characteristic, Korea, 2011-2024", ["Characteristic", "Unit", "Source", "Years", "Direction", "Filled cells"], rows,
   "Survey, Community Health Survey (district age-standardized rates); screening, National Health Insurance Service general health screening; KOSIS, Korean Statistical Information Service; registry, resident registration or public sports facility registry; panel, harmonized public district panel; ratio, men per 100 women. Direction, expected direction of the association with hypertensive disease mortality from the epidemiological literature. Filled cells, district-years filled by interpolation within districts or district means (of 3 206); the three corrected basic livelihood values (Changwon 2021-2023) are not counted. Internal medicine specialists and physician density had variance inflation factors below 3.")
# ── Table S2 ──
two = re.findall(r"\[연도 간 평균 2배 이상 차이\] (\S+):", gate); cnt = lambda tag: len(re.findall(r"\[" + re.escape(tag) + r"\]", gate))
ext = json.load(open(os.path.join(RS, "S41_extreme_flags.json"))); impc = json.load(open(os.path.join(RS, "S41_imputed_cells.json")))
rows = [["Year with all districts zero or missing", "≥98% of districts", "1 (post-2020 indicator)", "None (by design)"],
        ["Constant within a year", "One value in a year", "1 (same indicator)", "None (by design)"],
        ["Year explains most variance", "Year R² ≥0.80", "1 (same indicator)", "None (by design)"],
        ["Districts zero in every year", "5 to 60% of districts", "0", "None needed"],
        ["Yearly means differ twofold or more", "Max/min yearly mean ≥2", f"{len(two)} (means near 0)", "Checked; retained"],
        ["Ratio-type column above 100", "Maximum >100", f"{cnt('비율형인데 100 초과')} (sex ratio)", "Retained (definition)"],
        ["Extreme district-years", ">5 IQR from yearly quartiles", f"{sum(ext.values())} cells, {sum(1 for v in ext.values() if v)} covariates", "Refilled in one alternative"],
        ["Missing district-years", "No observation", f"{th(sum(impc.values()))} cells", f"Filled ({len(impc)} covariates); perturbed"],
        ["Survey series discontinued", "No data after a year", "1 (low-salt preference)", "Sensitivity only (2011-2019)"],
        ["Implausible values", "Inconsistent with neighbors", "3 (basic livelihood recipients)", "Set to missing and interpolated"],
        ["Duplicated population block", "Same as previous year", "1 (Changwon, 2023)", "Replaced with official total"],
        ["Yearly-mean filling", "≥100 cells, national means", "0 covariates", "None needed"]]
assert nwarn == 3 + len(two) + cnt("비율형인데 100 초과"), nwarn
rows = [[f"{r[0]} ({r[1]})", r[2], r[3]] for r in rows]
TF("Appendix Table 2. Panel checks before modeling, with rules, thresholds, flags, and actions, Korea, 2011-2024", ["Check (threshold)", "Flags in this panel", "Action"], rows,
   f"Checks were run on the analytic panel of {th(N['n_rows'])} district-years before any covariate model was fitted. The sex ratio is men per 100 women. IQR, interquartile range.")
# ── Table S3 ──
MPA, IMS, BLS, SHT = C.MPA, C.IMS, C.BLS, C.SHT
NAMES = [("principal", "Principal model"), ("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"),
         ("icar_besag", "Intrinsic autoregressive district effect"), ("iid_only", "Independent district effect"), ("no_spatial", "No district effect"), ("knn3", "3 nearest neighbors"), ("knn4", "4 nearest neighbors"), ("knn5", "5 nearest neighbors"), ("pc_phi_flat", "Flat prior on mixing parameter"), ("pc_relaxA", "Relaxed precision prior A"), ("pc_relaxB", "Relaxed precision prior B"),
         ("C1_poisson_lognormal", "Poisson, observation-level effect"), ("C2_rw2_year", "Second-order random-walk year effect"), ("C3_ar1_year", "First-order autoregressive year effect"), ("C4_sido_year_iid", "Province-by-year effect"), ("D1_spatial_plus", "Spatial+-type adjustment"), ("B3_smooth_forced", "Smoothed forced controls"), ("F3_extreme_R7", "Extreme values refilled"),
         ("E0_nolag_from2012", "No lag, years from 2012"), ("E0_nolag_from2013", "No lag, years from 2013"), ("E1_lag1", "Covariates lagged 1 year"), ("E2_lag2", "Covariates lagged 2 years"), ("G1_kchs_ma3", "Survey covariates, 3-year averages"), ("H4_odd_years", "Odd years only"), ("H4_even_years", "Even years only"),
         ("ssx", "Sex-and-age standardized expected deaths"), ("s8", "Ten age groups in expected deaths"), ("s2", "Share aged 80+ omitted"), ("s577", "Queen contiguity graph"), ("parsimonious", "Parsimonious model"),
         ("W1", "Window 2011-2015"), ("W2", "Window 2016-2019"), ("W3", "Window 2020-2024"), ("H1_nco_TRANS", "Transport accident deaths (comparison)"), ("H1_nco_INFECT", "Infectious disease care (comparison)")]
SS = {**N["s43"], **N["s41"], **N["s45"]}; WA = {**N["s43_waic"], **N["s41_waic"], **N["s45_waic"]}
for v in ("s577", "s2", "s8", "ssx"): SS.update({(v, c): t for c, t in N["sens_main"][v].items()}); WA[v] = float(pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_fit.csv")).WAIC.iloc[0])
SS.update({("parsimonious", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["s50_pars"].items()}); WA["parsimonious"] = N["s50_moran"]["parsimonious"]["WAIC"]; WA["principal"] = N["waic_main"]
SS.update({("principal", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["main"].items()})
for _w, _wn in zip(("W1", "W2", "W3"), C.WN): SS.update({(_w, v): C.wt(v, _wn) for v in N["main"] if (v, _wn) in C._W.index})
missing = [a for a, _ in NAMES if not any((a, v) in SS for v in (MPA, IMS, BLS, SHT))]; assert not missing, missing
def cell(a, v): t = SS.get((a, v)); return "-" if t is None else st(t)
HN = {MPA: "Moderate-or-higher physical activity", IMS: "Internal medicine specialists", BLS: "Basic livelihood recipients", SHT: "Suspected hypertension"}
_ALTN = {"B3_smooth_forced": "smoothed forced controls", "C1_poisson_lognormal": "Poisson with observation-level effect", "C2_rw2_year": "second-order random-walk year effect", "C3_ar1_year": "first-order autoregressive year effect", "C4_sido_year_iid": "province-by-year effect", "D1_spatial_plus": "Spatial+-type adjustment", "E0_nolag_from2012": "no lag, from 2012", "E0_nolag_from2013": "no lag, from 2013", "E1_lag1": "1-year lag", "E2_lag2": "2-year lag", "F3_extreme_R7": "extreme values refilled", "G1_kchs_ma3": "3-year survey averages", "H4_odd_years": "odd years", "H4_even_years": "even years"}
_ALT14 = [_ALTN[a] for a in N["alt14"]]; assert len(_ALT14) == 14
MOR = {"principal": "principal", "parsimonious": "parsimonious", "no_spatial": "no_spatial", "iid_only": "iid_district", "icar_besag": "icar_district", "KH_typeI": "typeI_interaction"}
FOOT3 = ("Mortality rate ratios per 1 standard deviation (95% credible intervals); '-', not in the model or not reported. WAIC, widely applicable information criterion, not comparable across outcomes, years, or likelihoods. "
         "Alternative specifications are listed in the Appendix Methods; the parsimonious model kept the forced controls and the subset-stable characteristic. Bounds shown as 1.000 were classified from unrounded values.")
_half = (len(NAMES) + 1) // 2
for part, cols, rng in (("a", [MPA, IMS], NAMES[:_half]), ("b", [MPA, IMS], NAMES[_half:]), ("c", [BLS, SHT], NAMES[:_half]), ("d", [BLS, SHT], NAMES[_half:])):
    rows = [[lab, f"{th(WA[a])}" if a in WA and not a.startswith("H1_") else "-", f"{N['s50_moran'][MOR[a]]['resid_moran_I']:.2f}".replace("-", "\u2212") if a in MOR else "-"] + [cell(a, v) for v in cols] for a, lab in rng]
    TF(f"Appendix Table 3{part}. Mortality rate ratios across alternative specifications and comparison outcomes, Korea, 2011-2024 (part {part.upper()})", ["Specification", "WAIC", "Residual Moran's I"] + [HN[v] for v in cols], rows,
       (FOOT3 + " Residual Moran's I, district-mean Pearson residuals of each specification.") if part == "a" else "See the note to Appendix Table 3a.")
# ── Table S4: 사망진단 점검 ──
ZN = [("Z0_main_refit", "Principal model (refit)"), ("Z1_illdefined", "Plus ill-defined cause share"), ("Z4_outside_care", "Plus out-of-district outpatient share"), ("P2_forced_only", "Forced controls only<sup>a</sup>"),
      ("Z2_broad_outcome", "Circulatory outcome (I00-I99)"), ("Z3_broad_illdefined", "Circulatory outcome plus ill-defined cause share"), ("P1_nonhtn_circ", "Circulatory excluding hypertensive<sup>a</sup>"), ("Z5a_main_2011_2019", "Principal model, 2011-2019"), ("Z5_low_salt_2011_2019", "Plus low-salt preference, 2011-2019")]
ZV = [C.SHT, C.TRT, C.AWR, C.OBE, C.MDM, C.ALC, C.WALK, C.MPA, C.FAC, C.BLS, C.IMS, C.OLD, "ill_defined_death_share", "outside_care_share", "low_salt_preference_rate"]
ZL = dict(LABEL, ill_defined_death_share="Ill-defined cause share", outside_care_share="Out-of-district outpatient share", low_salt_preference_rate="Low-salt preference")
for part, zs in (("a", ZN[:4]), ("b", ZN[4:7]), ("c", ZN[7:])):
    SZ = {**N["s45"], **N["s46"]}; WZ = dict(N["s45_waic"]); WZ.update({k[0]: None for k in N["s46"]})
    zs = [(a, l) for a, l in zs if any((a, v) in SZ for v in ZV)]
    rows = [[ZL[v]] + [st(SZ[(a, v)]) if (a, v) in SZ else "-" for a, _ in zs] for v in ZV]
    rows = [r for r in rows if any(x != "-" for x in r[1:])]
    rows.append(["WAIC"] + [th(N["s45_waic"][a]) if a in N["s45_waic"] else "-" for a, _ in zs])
    TF(f"Appendix Table 4{part}. Death certification, access, and sodium checks, Korea, 2011-2024 (part {part.upper()})", ["Characteristic"] + [l for _, l in zs], rows,
       "Values are mortality rate ratios per 1 standard deviation (95% credible intervals); forced controls are included but not shown; '-', not in the model. WAIC is not comparable between outcomes or between periods. " + ("<sup>a</sup>Added after results were seen. Residual spatial rate ratios of the 16 Busan districts: principal model " + f"{N['busan_rr_main'][0]:.2f}-{N['busan_rr_main'][1]:.2f}; forced controls only {N['busan_rr_forced'][0]:.2f}-{N['busan_rr_forced'][1]:.2f}; circulatory outcome {N['busan_rr_broad'][0]:.2f}-{N['busan_rr_broad'][1]:.2f}; circulatory excluding hypertensive {N['busan_rr_nonhtn'][0]:.2f}-{N['busan_rr_nonhtn'][1]:.2f}; principal model plus ill-defined cause share {N['busan_ill']['htnd'][0]:.2f}-{N['busan_ill']['htnd'][1]:.2f} (mean {N['busan_ill']['htnd'][2]:.2f}, {N['busan_ill']['htnd'][3]} hot spots); circulatory outcome plus ill-defined cause share {N['busan_ill']['circ'][0]:.2f}-{N['busan_ill']['circ'][1]:.2f} (mean {N['busan_ill']['circ'][2]:.2f}, {N['busan_ill']['circ'][3]} hot spots). Ratio of the hypertensive disease standardized mortality ratio to the all-circulatory standardized mortality ratio: Busan {N['smr_ratio'][True]:.3f}, elsewhere {N['smr_ratio'][False]:.3f}. " if part == "b" else "") + "Intervals with a bound shown as 1.000 were classified from unrounded values.")
# ── Table S5: 역방향 사후 검정 ──
S44 = N["s44"]
R = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"])),
     ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)]), ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)]), ("Province-by-year effect", lambda v: N["s41"][("C4_sido_year_iid", v)]),
     ("Covariates lagged 1 year", lambda v: N["s41"][("E1_lag1", v)]), ("Covariates lagged 2 years", lambda v: N["s41"][("E2_lag2", v)]),
     ("Window 2011-2015", lambda v: C.wt(v, C.WN[0])), ("Window 2016-2019", lambda v: C.wt(v, C.WN[1])), ("Window 2020-2024", lambda v: C.wt(v, C.WN[2])),
     ("Between-district component", lambda v: N["bw"][v + "__between"]), ("Within-district component", lambda v: N["bw"][v + "__within"]),
     ("Fitted alone with forced controls", lambda v: S44[(f"R4_single_{v}", v)]), ("Walking and sports facilities removed", lambda v: S44[("R5_drop_other_activity", v)]),
     ("Transport accident deaths (comparison)", lambda v: N["s41"][("H1_nco_TRANS", v)]), ("Infectious disease care (comparison)", lambda v: N["s41"][("H1_nco_INFECT", v)])]
rows = [[lab, st(f(MPA))] for lab, f in R]
TF("Appendix Table 5. Checks of the moderate-or-higher physical activity association, opposite to the expected direction, Korea, 2011-2024", ["Analysis", "Moderate-or-higher physical activity"], rows,
   "Mortality rate ratios per 1 standard deviation (95% credible intervals). Physical activity was expected to lower mortality. The rows 'Fitted alone with forced controls' and 'Walking and sports facilities removed' were added after the principal results were seen; the other rows are standard sensitivity analyses. Intervals with a bound shown as 1.000 were classified from unrounded values.")
# ── Table S6: 권역 ──
REG = [("Capital", "Capital region"), ("Chungcheong", "Chungcheong"), ("Honam", "Honam"), ("Yeongnam", "Yeongnam"), ("Gangwon_Jeju", "Gangwon-Jeju")]
_rs = pd.read_csv(os.path.join(RS, "S50_region_slopes.csv")); _nd = _rs.groupby("region").n_district_years.first().to_dict()
rows = [[lab, th(_nd[r]), st(N["s50_region"][(MPA, r)])] for r, lab in REG] + [["Difference in WAIC vs common slope", "", f"{N['s50_region_dwaic'][MPA]:+.1f}".replace("-", "−")]]
TF("Appendix Table 6. Region-specific mortality rate ratios for moderate-or-higher physical activity, Korea, 2011-2024", ["Region", "District-years", "Moderate-or-higher physical activity"], rows,
   "Principal model with the characteristic interacted with five regions (capital region: Seoul, Incheon, Gyeonggi; Chungcheong: Daejeon, Sejong, North and South Chungcheong; Honam: Gwangju, North and South Jeolla; Yeongnam: Busan, Daegu, Ulsan, North and South Gyeongsang; Gangwon-Jeju). Negative WAIC differences favor region-specific slopes. WAIC, widely applicable information criterion.")
# ── Fig. S1 ──
EN = C.EN
def en(r):
    for k, v in EN.items():
        if r.startswith(k): return f"{r[len(k):]} ({v})"
    return r
J.page_break(); _pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "AJPM_FigS1.png"), width=Cm(16))
J.para("<b>Appendix Figure 1. Persistence of the district pattern of hypertensive disease mortality, Korea, 2011-2024.</b> (A) Emerging hot spot analysis (Getis-Ord Gi* with Mann-Kendall trend) of empirical Bayes-smoothed standardized mortality ratios; numbers of districts in parentheses. (B) Number of calendar windows (2011-2015, 2016-2019, 2020-2024) in which each district was a residual hot or cold spot in window-specific models. "
       f"Districts that were hot spots in all three windows ({len(N['persist_hot_list'])}) were in Ulsan, Busan, North and South Gyeongsang, Daegu, and Gyeonggi.")
import build_ajpm_htnd as _BA
J.page_break(); _pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "AJPM_FigS2.png"), width=Cm(16))
J.para("<b>Appendix Figure 2. Mortality rate ratios for three district characteristics across model specifications, Korea, 2011-2024.</b> Mortality rate ratios per 1 standard deviation with 95% credible intervals for internal medicine specialists, moderate-or-higher physical activity, and basic livelihood recipients: principal model; Knorr-Held type II and type IV space-time interactions, which allow district-specific trends; province-by-year effects; principal model with the ill-defined cause share; all circulatory deaths as the outcome; and the within-district (two-way-centered) component for physical activity. The dotted vertical line marks a ratio of 1.")
ps = os.path.join(OUT, "Appendix.docx"); J.doc_title = "Appendix"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_htnd_esm_ajpm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
