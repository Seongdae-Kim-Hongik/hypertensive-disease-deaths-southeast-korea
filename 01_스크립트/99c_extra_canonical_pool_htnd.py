#!/usr/bin/env python3
# 99c — 17호 고혈압성질환 사망(HTND, I10-I13) 가설 풀용 추가 열(2026-11-08). 99c_pneu를 복제해 결합 규칙(코드표, 이름 결합 금지, 군위군 37310 별칭)은 그대로 쓴다.
#  (아래 ①②③ 설명 중 요양병원·응급의학·공장용지는 HTND에서 쓰지 않고, 내과 전문의(12호 IHD 정의)와 순환계 사인을 더한다)
#  ① 정본 통합자료: basic_livelihood_rate(국민기초생활보장 수급자 비율 %, 창원 2021-23 입력 오류 3칸 보간) — 박탈
#  ② (HTND) 내과 전문의 ÷ 정본 인구 × 10만 — 고혈압 진단·치료·합병증 관리 역량(12호 IHD 정의)
#  ③ 사망원인 추가 사인(성=계): 고혈압성 I10-I13(검산: 패널 cases와 3,206칸 일치 assert), 순환계 전체 I00-I99, IHD I20-I25, 기타 심장 I26-I51, 뇌혈관 I60-I69, R00-R99, 전체
#       → ill_defined_share = R00-R99 ÷ 전체 사망 × 100 (사망진단 품질 대리, 민감도 전용)
#  산출: 02_패널/EXT_canonical_pool_HTND_261108.csv, 02_패널/HTND_mort_extra_261108.csv
import os, sys, unicodedata, importlib.util
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, ".."))
ZD = os.environ.get("ST_CANON", os.path.join(os.path.expandvars("$ST_DATA_ROOT"), "기타/R_Studio/FBD_DATA_ZIP/통합자료_261030"))
PAN = os.path.join(ROOT, "02_패널")

# ① 정본
C = pd.read_csv(os.path.join(ZD, "01_공변량_229x2011_2024.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str})
K = pd.read_csv(os.path.join(ZD, "00_시군구_229_대응표.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); assert K.sigungu_cd.is_unique and len(K) == 229
K.loc[K.sigungu_cd == "37310", "region"] = "대구시군위군"
C = C.drop(columns=["region"]).merge(K[["sigungu_cd", "region"]], on="sigungu_cd", how="left", validate="many_to_one"); assert C.region.notna().all()
out = pd.DataFrame({"year": C.year, "fbd_region": C.region.map(NFC),
                    "im_specialists_per100k": C.internal_medicine_specialists.astype(float) / C["pop"].astype(float) * 1e5,
                    "basic_livelihood_rate": C.basic_livelihood_recipient_rate.astype(float)})
out = out[(out.year >= 2011) & (out.year <= 2024)].copy()
bad = (out.fbd_region == NFC("경상남도창원시")) & out.year.isin([2021, 2022, 2023])
assert bad.sum() == 3; print("[99c-htnd] 창원 2021-23 수급률 원값", out.loc[bad, "basic_livelihood_rate"].round(2).tolist(), "→ 결측 후 보간")
out.loc[bad, "basic_livelihood_rate"] = np.nan
out = out.sort_values(["fbd_region", "year"])
out["basic_livelihood_rate"] = out.groupby("fbd_region").basic_livelihood_rate.transform(lambda s: s.interpolate(method="linear", limit_area="inside"))
assert out.groupby("fbd_region").year.nunique().eq(14).all() and out.fbd_region.nunique() == 229 and not out.duplicated(["year", "fbd_region"]).any()

# ② 패널(검산용)
MA = pd.read_parquet(os.path.join(PAN, "MASTER_시군구_연도_wide.parquet"), columns=["year", "fbd_region", "mort__고혈압성질환_deaths", "mort__전체사망_deaths"])
MA["fbd_region"] = MA.fbd_region.map(NFC); MA = MA[MA.year.between(2011, 2024)]
P = pd.read_csv(os.path.join(ROOT, "04_분석", "HTND", "panel_HTND.csv"), encoding="utf-8-sig", usecols=["year", "fbd_region", "population", "cases"]); P["fbd_region"] = P.fbd_region.map(NFC)
X = P.merge(MA, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert len(X) == 3206 and (X.cases == X["mort__고혈압성질환_deaths"]).all()

# ③ 사망원인 추가 사인 → 50.load_source 집계
spec = importlib.util.spec_from_file_location("m50", os.path.join(HERE, "50_build_master_panel.py")); m50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m50)
L = pd.read_parquet(os.path.join(PAN, "사망원인_시군구_연도_사인_성_long.parquet"), columns=["year", "sido", "sigungu", "sgg_code", "sgg_code_std", "level", "parent_code", "code_note", "cause_code", "sex", "deaths"],
                    filters=[("sex", "==", "계"), ("year", ">=", 2011), ("year", "<=", 2024), ("cause_code", "in", ["0", "91", "9", "93", "94", "95", "I"])])
L = L[(L.sex == "계") & L.year.between(2011, 2024) & L.cause_code.isin(["0", "91", "9", "93", "94", "95", "I"])]
L["v"] = L.cause_code.map({"0": "전체_deaths", "91": "HTND_deaths", "9": "CIRC_deaths", "93": "IHD_deaths", "94": "OTHHEART_deaths", "95": "STRK_deaths", "I": "불명확_deaths"})
IDX = ["year", "sido", "sigungu", "sgg_code", "sgg_code_std", "level", "parent_code", "code_note"]
for c in IDX[1:]: L[c] = L[c].fillna("").astype(str)
W = L.pivot_table(index=IDX, columns="v", values="deaths", aggfunc="sum").reset_index().replace({"": np.nan})
W = W[W.level.notna()]
tmpf = "_tmp_HTND_mort_extra_wide.csv"; W.to_csv(os.path.join(PAN, tmpf), index=False, encoding="utf-8-sig")
mk = pd.read_csv(os.path.join(PAN, "시군구_마스터키.csv"), dtype=str); mk = mk[mk.fbd_sido.notna()].drop_duplicates("key")
log = dict(missing_files=[], level_filter={}, unmatched=[], special=[], overlap=[], sources={})
src = dict(name="mortx", prefix="", files=[tmpf], sido="sido", sgg="sigungu", merge_counts=True, level="시군구", ratio=lambda c: False, label="사망원인통계")
agg, meta = m50.load_source(src, set(mk.key), log)
os.remove(os.path.join(PAN, tmpf))
agg = agg.merge(mk[["key", "fbd_region"]], on="key", how="left"); agg["fbd_region"] = agg.fbd_region.map(NFC); agg["year"] = agg.year.astype(int)
M = P[["year", "fbd_region", "cases"]].merge(agg[["year", "fbd_region", "전체_deaths", "HTND_deaths", "CIRC_deaths", "IHD_deaths", "OTHHEART_deaths", "STRK_deaths", "불명확_deaths"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
assert M[["전체_deaths", "HTND_deaths", "CIRC_deaths"]].notna().all().all(), M[M.HTND_deaths.isna()].head()
mm = (M.HTND_deaths != M.cases).sum(); print(f"[99c-htnd] I10-I13 검산: 마스터·패널 cases와 불일치 {mm}칸 / {len(M)}"); assert mm == 0
tot_chk = M.merge(MA[["year", "fbd_region", "mort__전체사망_deaths"]], on=["year", "fbd_region"]); assert (tot_chk["전체_deaths"] == tot_chk["mort__전체사망_deaths"]).all()
for c in ["불명확_deaths", "IHD_deaths", "OTHHEART_deaths", "STRK_deaths"]: print(f"[99c-htnd] {c} 결측 {int(M[c].isna().sum())}, 14년 합 {int(M[c].sum()):,}"); M[c] = M[c].fillna(0)
M["ill_defined_share"] = M["불명확_deaths"] / M["전체_deaths"] * 100
assert (M.CIRC_deaths >= M.HTND_deaths).all()
M["htnd_share_of_circ"] = M.HTND_deaths / M.CIRC_deaths.where(M.CIRC_deaths > 0) * 100
print("[99c-htnd] 순환계 사망 중 고혈압성 비율(%) 연도별 전국", (M.groupby("year").HTND_deaths.sum() / M.groupby("year").CIRC_deaths.sum() * 100).round(2).to_dict())
print("[99c-htnd] 불명확 사인 비율(%) 연도 중앙값", M.groupby("year").ill_defined_share.median().round(2).to_dict())
out = out.merge(M[["year", "fbd_region", "ill_defined_share"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
assert out.notna().all().all(), out.isna().sum()
fp = os.path.join(PAN, "EXT_canonical_pool_HTND_261108.csv"); out.to_csv(fp, index=False, encoding="utf-8-sig")
M.to_csv(os.path.join(PAN, "HTND_mort_extra_261108.csv"), index=False, encoding="utf-8-sig")
print(f"[99c-htnd] 저장 {fp} {out.shape}; 02_패널/HTND_mort_extra_261108.csv {M.shape}")
