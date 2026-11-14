#  사용: from numbers_htnd import load; N = load()
import os, re, glob, numpy as np, pandas as pd
_UNK = 9   # 39m 로그: 연령미상 사망 14년 9건
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")   # 17호 std3(고혈압성질환 사망 역학 세트, 처음부터)
ROOT = os.path.dirname(os.path.dirname(B)); PAN = os.path.join(ROOT, "02_패널")
WIN = [("W1_2011-15", 2011, 2015), ("W2_2016-19", 2016, 2019), ("W3_2020-24", 2020, 2024)]
rd = lambda f, **k: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", **k)
ROB = ["moderate_pa_rate"]
REV = ["moderate_pa_rate"]   # 사전지정 방향과 반대로 credible
CAP = ("서울", "경기", "인천")
SHP = os.environ.get("ST_SHP", os.path.join(HERE, "..", "..", "..", "..", "data", "boundary", "final.shp"))

def load():
    N = {}
    P = pd.read_csv(os.path.join(B, "panel_HTND_std3.csv")); N["n_rows"] = len(P); N["n_districts"] = P.fbd_region.nunique()
    assert (N["n_rows"], N["n_districts"]) == (3206, 229)
    N["cases_total"] = int(P.cases.sum()); N["py"] = float(P.offset.sum())
    y = P.groupby("year")[["cases", "offset"]].sum(); N["cases_2011"], N["cases_2024"] = int(y.cases[2011]), int(y.cases[2024])
    N["crude_2011"], N["crude_2024"] = 1e5 * y.cases[2011] / y.offset[2011], 1e5 * y.cases[2024] / y.offset[2024]
    # 직접 연령표준화율(2015 전국 인구 5세 18구간 구조; 39m 산출 전국 사인별 사망률·분모). 사망은 전국 합 = 시군구 합이라 재척도 불필요(assert)
    A = pd.read_csv(os.path.join(PAN, "HTND_national_agerates_mort.csv"))
    _d = {yr: y.cases[yr] - A[A.year == yr].deaths.sum() for yr in y.index}; assert all(0 <= v <= 4 for v in _d.values()) and sum(_d.values()) == _UNK, _d   # 차이 = 연령미상 사망(14년 9건, 39m 로그)
    w = A[A.year == 2015].set_index("age").denom_nat; w = w / w.sum(); asr = {}
    for yr, g in A.groupby("year"): asr[yr] = 1e5 * float((g.set_index("age").rate * w).sum())
    N["asr"] = asr; N["asr_2011"], N["asr_2024"] = asr[2011], asr[2024]; N["asr_ratio"] = asr[2024] / asr[2011]
    N["asr_min_year"] = min(asr, key=asr.get)
    g24 = A[A.year == 2024].set_index("age"); N["share85_2024"] = float(g24.deaths["85+"] / g24.deaths.sum()); N["share75_2024"] = float(g24.deaths[["75-79", "80-84", "85+"]].sum() / g24.deaths.sum())
    g11 = A[A.year == 2011].set_index("age"); N["share85_2011"] = float(g11.deaths["85+"] / g11.deaths.sum())
    T1 = {}
    for wn, a, b in WIN + [("2011-2024", 2011, 2024)]:
        q = P[(P.year >= a) & (P.year <= b)]; sir = q.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), py=float(q.offset.sum()), crude=1e5 * q.cases.sum() / q.offset.sum(),
                      asr=np.mean([asr[t] for t in range(a, b + 1)]), sir_p10=sir.quantile(.1), sir_p90=sir.quantile(.9), sir_med=sir.median(),
                      cov={v: (q[f"{v}_raw"].mean(), q[f"{v}_raw"].std()) for v in ["pop80_share", "urban_population_share", "physicians_per_1000",
                           "sex_ratio", "fiscal_independence", "screening_suspected_hypertension_share", "hypertension_treatment_rate", "bp_awareness_rate", "screening_abdominal_obesity_share", "screening_suspected_diabetes_share", "high_risk_drinking_rate", "walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k", "basic_livelihood_rate", "im_specialists_per_100k", "older_single_household_share"]})
    N["T1"] = T1
    # 공간
    s6m = rd("S6_moran_year.csv"); N["moran_year_min"], N["moran_year_max"] = s6m.moran_I.min(), s6m.moran_I.max()
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]
    N["moran_resid"] = r8.loc["pearson_residual_area_mean", "moran_I"]; N["moran_resid_p"] = r8.loc["pearson_residual_area_mean", "p_perm"]
    N["moran_y"] = s6m.set_index("year").moran_I.to_dict()
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum())
    N["hot_strict"] = {t: (int((s6.P_gt1 > t).sum()), int((s6.P_gt1 < 1 - t).sum())) for t in (0.975, 0.99)}   # review(11/6): 느슨한 기준 우려 → 엄격 기준 병기
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["hot_capital"] = int(((s6["class"] == "hotspot") & s6.fbd_region.str.startswith(CAP)).sum())
    N["cold_capital"] = int(((s6["class"] == "coldspot") & s6.fbd_region.str.startswith(CAP)).sum())
    typ = s6.fbd_region.map(lambda r: "county" if r.endswith("군") else ("ward" if r.endswith("구") else "city"))
    N["type_class"] = pd.crosstab(typ, s6["class"]).to_dict(); N["n_type"] = typ.value_counts().to_dict()
    wm = rd("S4b_window_spatialRR.csv"); N["win_hot"] = wm[wm["class"] == "hotspot"].groupby("window").size().to_dict()
    N["win_cold"] = wm[wm["class"] == "coldspot"].groupby("window").size().to_dict()
    hs = {w: set(wm[(wm.window == w) & (wm["class"] == "hotspot")].fbd_region) for w in wm.window.unique()}; N["hot_all_windows"] = len(set.intersection(*hs.values()))
    _pv = wm.pivot_table(index="fbd_region", columns="window", values="RR").corr(method="spearman"); N["win_rr_rho"] = (float(_pv.loc["W1_2011-15", "W3_2020-24"]), float(_pv.loc["W1_2011-15", "W2_2016-19"]), float(_pv.loc["W2_2016-19", "W3_2020-24"]))
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall_W"] = pe.loc["2011-2024", "kendall_W"]
    N["kendall_W_1119"], N["kendall_W_2024"] = pe.loc["2011-2019", "kendall_W"], pe.loc["2020-2024", "kendall_W"]
    eh = rd("S11_ehsa_summary.csv").set_index("category").n.to_dict(); N["ehsa"] = eh
    # 주모형·다중우주
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role", "label_en", "P_gt1"]].to_dict("index")
    N["n_hyp"] = int((m3.role == "hypothesis").sum()); N["n_cred_hyp"] = int(((m3.role == "hypothesis") & m3.cred).sum())
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index")
    N["n_robust"] = int(s7.robust.sum()); assert set(s7.index[s7.robust]) == set(ROB), s7.index[s7.robust].tolist()
    hb = open(os.path.join(B, "HM_best_HTND_std3.txt")).read(); N["waic_forced"] = float(hb.split("ref_forced_only_WAIC=")[1].split()[0])
    N["waic_main"] = float(hb.split("S1_narrative_full(")[1].split(",")[0])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = nc[["IRR", "lo", "hi", "cred"]].to_dict("index")
    wi = rd("S4_window_IRR.csv"); N["win_irr"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, r.cred) for r in wi.itertuples()}
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv"))]); N["s43"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S43.itertuples()}
    N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S41.itertuples()}
    N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict()
    ALT = sorted({a for a in S41.analysis.unique() if not a.startswith(("F1_", "F2_", "G2_", "H1_", "bw_"))}); N["alt14"] = ALT
    N["ret14"] = {}
    for v in ROB:
        sg = N["main"][v]["IRR"] > 1; rr = [N["s41"][(a, v)] for a in ALT if (a, v) in N["s41"]]
        N["ret14"][v] = (sum(1 for t in rr if t[3] and (t[0] > 1) == sg), len(rr))
    N["c1_robust_kept"] = int(S41[S41.analysis == "C1_poisson_lognormal"].robust_kept.iloc[0])
    N["bw"] = {(r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["retention"] = rd("S41_retention_by_cov.csv").set_index("cov").to_dict("index"); N["rubin"] = rd("S41_noise_rubin.csv").set_index("cov").to_dict("index")
    N["evalue"] = rd("S41_evalues.csv").set_index("cov").to_dict("index"); N["oos"] = rd("S41_oos2024.csv").iloc[0].to_dict()
    N["ppc"] = rd("S42_ppc.csv").iloc[0].to_dict(); N["varpart"] = rd("S42_variance_partition.csv").set_index("component").to_dict("index")
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in rd("S41_nco_detail.csv").itertuples()}
    # 사전지정 E·그래프 민감도(주모형만)
    # 남북 기울기 검정: 시군구 중심점 북쪽 좌표와 잔차 RR·보정 없는 EB 평활 STR의 Spearman 상관, 잔차 RR과 EB STR의 상관
    import geopandas as gpd; from scipy.stats import spearmanr
    G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["y"] = G.centroid.y; G["x"] = G.centroid.x
    s6i = s6.set_index(s6.sigungu_cd.astype(str)); ehi = rd("S11_ehsa.csv"); ehi = ehi.set_index(ehi.sigungu_cd.astype(str))
    G["rr"] = G.cd.map(s6i.RR); G["eb"] = G.cd.map(ehi.ebSIR_mean); assert G[["rr", "eb"]].notna().all().all()
    N["lat_rr"] = spearmanr(G.y, G.rr).correlation; N["lon_rr"] = spearmanr(G.x, G.rr).correlation; N["lon_eb"] = spearmanr(G.x, G.eb).correlation; N["lat_eb"] = spearmanr(G.y, G.eb).correlation; N["rr_eb"] = spearmanr(G.rr, G.eb).correlation
    # 부유도 기울기(5호 /결과 요약): 보정 없는 EB STR·잔차 RR과 시군구 평균 의료급여 1종 진료율·재정자주도의 Spearman 상관
    Pm = P.groupby(P.key.astype(str) if "key" in P else P.fbd_region)[["basic_livelihood_rate_raw", "fiscal_independence_raw"]].mean()
    s6r = s6.set_index("fbd_region"); ehr = rd("S11_ehsa.csv").set_index("fbd_region"); Pm2 = P.groupby("fbd_region")[["basic_livelihood_rate_raw", "fiscal_independence_raw"]].mean()
    N["eb_bls"] = spearmanr(Pm2.basic_livelihood_rate_raw, ehr.ebSIR_mean.reindex(Pm2.index)).correlation
    N["eb_fis"] = spearmanr(Pm2.fiscal_independence_raw, ehr.ebSIR_mean.reindex(Pm2.index)).correlation
    N["rr_bls"] = spearmanr(Pm2.basic_livelihood_rate_raw, s6r.RR.reindex(Pm2.index)).correlation
    cv = rd("S5_covid.csv"); N["covid_main"] = tuple(cv[cv.term == "post_main"][["IRR", "lo", "hi", "cred"]].iloc[0]); N["covid_nint"] = int(cv[(cv.term == "var_x_post") & cv.cred].shape[0]); N["covid_int_cov"] = cv[(cv.term == "var_x_post") & cv.cred]["cov"].tolist()
    import unicodedata as _u
    _wm = wm.assign(r=wm.fbd_region.map(lambda x: _u.normalize("NFC", x))); _sd = lambda x: re.match(r"^(\S+?(?:도|시))", x).group(1)
    for cls, key in (("hotspot", "persist_hot_by_sido"), ("coldspot", "persist_cold_by_sido")):
        k3 = _wm[_wm["class"] == cls].groupby("r").size(); idx = k3[k3 == 3].index
        N[key] = pd.Series([_sd(x) for x in idx]).value_counts().to_dict()
    nc3 = {w: set(wm[(wm.window == w) & (wm["class"] == "coldspot")].fbd_region) for w in wm.window.unique()}; N["cold_all_windows"] = len(set.intersection(*nc3.values()))
    N["sens_main"] = {}
    for v in ["s577", "s2", "s8", "ssx"]:
        m = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")).set_index("cov"); N["sens_main"][v] = {c: (m.loc[c, "IRR"], m.loc[c, "lo"], m.loc[c, "hi"], bool(m.loc[c, "cred"])) for c in m.index}
    # 심사 선제(88k review, 2026-11-06)
    N["s50_moran"] = rd("S50_resid_moran_by_spec.csv").set_index("spec").to_dict("index")
    N["s50_pars"] = rd("S50_parsimonious.csv").set_index("cov").to_dict("index")
    rs = rd("S50_region_slopes.csv"); N["s50_region"] = {(r.covariate, r.region): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in rs.itertuples()}
    N["s50_region_dwaic"] = rs.groupby("covariate").dWAIC_vs_common.first().to_dict()
    ac = rd("S50_access_sensitivity.csv").set_index("cov"); N["s50_access"] = {c: (ac.loc[c, "IRR"], ac.loc[c, "lo"], ac.loc[c, "hi"], bool(ac.loc[c, "cred"])) for c in ac.index}
    # 사후 역방향 검정(88r, post hoc)
    R = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S44_reverse_*.csv"))]); N["s44"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in R.itertuples()}
    N["s44_waic"] = R.groupby("analysis").WAIC.first().to_dict()
    # 14호: 사망진단·접근성 민감도(88z S45), 핫스팟 군·시·구, 불명확 사인 추세, 선별 φ
    N["s45"] = {}; N["s45_waic"] = {}
    for f in glob.glob(os.path.join(RS, "S45_coding_Z*.csv")):
        d = pd.read_csv(f); N["s45"].update({(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in d.itertuples()}); N["s45_waic"][d.analysis.iloc[0]] = float(d.WAIC.iloc[0])
    X = pd.read_csv(os.path.join(PAN, "HTND_mort_extra_261108.csv")); N["illdef_med"] = X.groupby("year").ill_defined_share.median().to_dict()
    _g = X.groupby("year")[["HTND_deaths", "CIRC_deaths", "IHD_deaths", "STRK_deaths", "OTHHEART_deaths", "전체_deaths"]].sum(); N["circ_share"] = (_g.HTND_deaths / _g.CIRC_deaths).to_dict()
    assert (_g.HTND_deaths.values == y.cases.values).all()
    # 순환계 전체(I00-I99) 직접 연령표준화율(같은 2015 가중치, 39m_circb 산출)
    Ac = pd.read_csv(os.path.join(PAN, "CIRCB_national_agerates_mort.csv")); N["asr_circ"] = {yr: 1e5 * float((g.set_index("age").rate * w).sum()) for yr, g in Ac.groupby("year")}
    # 부산(16개 구·군)·울산 요약: 주모형 핫스팟, 순환계 결과(Z2) 공간 RR
    AR = pd.read_csv(os.path.join(RS, "S45_coding_area.csv")); AR["fbd_region"] = AR.fbd_region.map(lambda x: __import__("unicodedata").normalize("NFC", x))
    bs = AR[AR.fbd_region.str.startswith("부산시")]; assert len(bs) == 16
    N["busan_n"] = 16; N["busan_hot"] = int(s6[s6.fbd_region.str.startswith("부산시")]["class"].eq("hotspot").sum())
    N["busan_rr_main"] = (bs.RR_main.min(), bs.RR_main.max()); N["busan_rr_broad"] = (bs.RR_broad.min(), bs.RR_broad.max()); N["busan_broad_p"] = bs.P_gt1_broad.min()
    from scipy.stats import spearmanr as _sp; N["rr_main_broad_rho"] = _sp(AR.RR_main, AR.RR_broad).correlation
    N["broad_hot"] = int((AR.P_gt1_broad > 0.95).sum()); N["broad_hot_busan"] = int((bs.P_gt1_broad > 0.95).sum())
    _o = P.assign(s=P.fbd_region.str[:3]).groupby("s")[["cases", "E"]].sum(); N["sido_smr"] = (_o.cases / _o.E).to_dict()
    _p3 = {w: set(wm[(wm.window == w) & (wm["class"] == "hotspot")].fbd_region) for w in wm.window.unique()}; _ps = set.intersection(*_p3.values())
    N["persist_hot_list"] = sorted(_ps)
    # review 1회차 사후(88z2, 결과를 본 뒤 추가): 비고혈압성 순환계 결과 공간 RR, 강제통제만 모형 공간 RR, 부산 사인 구성
    PA = pd.read_csv(os.path.join(RS, "S46_post_area.csv")); PA["fbd_region"] = PA.fbd_region.map(lambda x: __import__("unicodedata").normalize("NFC", x)); pb = PA[PA.fbd_region.str.startswith("부산시")]; assert len(pb) == 16
    N["busan_rr_nonhtn"] = (pb.RR_nonhtn.min(), pb.RR_nonhtn.max()); N["busan_nonhtn_hot"] = int((pb.P_gt1_nonhtn > 0.95).sum()); N["nonhtn_hot"] = int((PA.P_gt1_nonhtn > 0.95).sum())
    N["busan_rr_forced"] = (pb.RR_forced.min(), pb.RR_forced.max()); N["busan_mean_rr"] = {k: float(pb[k].mean()) for k in ("RR_main", "RR_forced", "RR_nonhtn")}
    N["rr_main_nonhtn_rho"] = _sp(PA.RR_main, PA.RR_nonhtn).correlation
    _ip = os.path.join(RS, "S46_post_P1_nonhtn_circ.csv")
    N["s46"] = {}
    for _f in glob.glob(os.path.join(RS, "S45_coding_P*.csv")):
        if _f.endswith("_area.csv"): continue
        _d = pd.read_csv(_f); N["s46"].update({(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in _d.itertuples()})
    _xb = X.assign(bs=X.fbd_region.str.startswith("부산시")).groupby("bs")[["HTND_deaths", "CIRC_deaths", "불명확_deaths", "전체_deaths"]].sum()
    N["busan_htn_share"] = float(_xb.HTND_deaths[True] / _xb.CIRC_deaths[True]); N["rest_htn_share"] = float(_xb.HTND_deaths[False] / _xb.CIRC_deaths[False])
    I7 = pd.read_csv(os.path.join(RS, "S47_post_area_illdef.csv")); I7["fbd_region"] = I7.fbd_region.map(lambda x: __import__("unicodedata").normalize("NFC", x)); ib = I7[I7.fbd_region.str.startswith("부산시")]; assert len(ib) == 16
    N["busan_ill"] = dict(htnd=(ib.RR_htnd_ill.min(), ib.RR_htnd_ill.max(), float(ib.RR_htnd_ill.mean()), int((ib.P_htnd_ill > 0.95).sum())), circ=(ib.RR_circ_ill.min(), ib.RR_circ_ill.max(), float(ib.RR_circ_ill.mean()), int((ib.P_circ_ill > 0.95).sum())))
    N["busan_broad_mean"] = float(bs.RR_broad.mean())
    # 연령 보정 비교: 고혈압성 SMR ÷ 순환계 SMR(부산 대 그 외), 순환계 대비 고혈압성 연령표준화율 비
    _C = pd.read_csv(os.path.join(ROOT, "04_분석", "CIRCB", "panel_CIRCB.csv"), usecols=["year", "fbd_region", "cases"]).merge(pd.read_csv(os.path.join(PAN, "CIRCB_Estd2.csv"), usecols=["year", "fbd_region", "E_std2"]), on=["year", "fbd_region"])
    _h = P.assign(bs=P.fbd_region.str.startswith("부산시")).groupby("bs")[["cases", "E"]].sum(); _c = _C.assign(bs=_C.fbd_region.str.startswith("부산시")).groupby("bs")[["cases", "E_std2"]].sum()
    N["smr_ratio"] = {k: float((_h.cases[k] / _h.E[k]) / (_c.cases[k] / _c.E_std2[k])) for k in (True, False)}
    N["smr_busan"] = (float(_h.cases[True] / _h.E[True]), float(_c.cases[True] / _c.E_std2[True]))
    N["asr_share"] = {yr: asr[yr] / N["asr_circ"][yr] for yr in asr}
    N["busan_illdef"] = float(_xb["불명확_deaths"][True] / _xb["전체_deaths"][True]); N["rest_illdef"] = float(_xb["불명확_deaths"][False] / _xb["전체_deaths"][False])
    _hs = pd.read_csv(os.path.join(B, "results_screen", "forced_std_hyper.csv")).set_index("hyperpar").loc["Phi for area"]; N["phi_screen"] = (float(_hs["mean"]), float(_hs["X0.025quant"]), float(_hs["X0.975quant"]))
    N["vif"] = pd.read_csv(os.path.join(B, "panel_META_HTND_std3.csv")).set_index("variable").vif_final.to_dict()
    # review 1회차(11/8): 연도별 Moran 상승이 사망 수 증가에 따른 잡음 감소 인공물인지 — 전역 경험적 베이즈(Marshall) 평활 SMR의 연도별 Moran(593 그래프, 행 표준화)
    import unicodedata as _un, geopandas as _gpd
    _G = _gpd.read_file(SHP); _reg = [_un.normalize("NFC", r) for r in _G.region]; _n = len(_reg)
    _L = [l.split() for l in open(os.path.join(B, "graph_593.graph")).read().strip().split("\n")]; _Wm = np.zeros((_n, _n))
    for _p in _L[1:]:
        for _j in _p[2:2 + int(_p[1])]: _Wm[int(_p[0]) - 1, int(_j) - 1] = 1
    assert _Wm.sum() / 2 == 593; _Wm = _Wm / _Wm.sum(1, keepdims=True)
    _I = lambda x: float(np.errstate(all="ignore").__enter__() and 0 or (x - x.mean()) @ _Wm @ (x - x.mean()) / ((x - x.mean()) @ (x - x.mean())))
    _P = P.assign(r=P.fbd_region.map(lambda s: _un.normalize("NFC", s))); N["moran_eb"] = {}
    for _y, _d in _P.groupby("year"):
        _d = _d.set_index("r").reindex(_reg); O = _d.cases.values; E = _d.E.values; m = O.sum() / E.sum(); rr = O / E
        s2 = max((E * (rr - m) ** 2).sum() / E.sum() - m / E.mean(), 1e-9); w = s2 / (s2 + m / E); N["moran_eb"][_y] = _I(np.log(w * rr + (1 - w) * m))
    assert abs(_I(np.log((_P[_P.year == 2011].set_index("r").reindex(_reg).cases.values + 0.5) / _P[_P.year == 2011].set_index("r").reindex(_reg).E.values)) - N["moran_y"][2011]) < 0.01   # 81 S6과 같은 값 재현
    _t = wm.fbd_region.map(lambda r: "county" if r.endswith("군") else ("ward" if r.endswith("구") else "city"))
    N["win_hot_type"] = wm[wm["class"] == "hotspot"].groupby([wm.window, _t]).size().unstack().fillna(0).astype(int).to_dict("index")
    return N

if __name__ == "__main__":
    N = load()
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items() if not isinstance(v, (dict, list, pd.DataFrame))})
    print("hot_by_sido", N["hot_by_sido"]); print("cold_by_sido", N["cold_by_sido"]); print("ehsa", N["ehsa"]); print("win_hot", N["win_hot"])
    print("T1", {k: {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "cov"} for k, v in N["T1"].items()})
    print("KH WAIC", {k: v for k, v in N["s43_waic"].items() if "KH" in k}, "ppc", {k: N["ppc"][k] for k in ["coverage95", "coverage50", "pit_ks_p"]})
