# -*- coding: utf-8 -*-
#  EJCP: 그림은 본문에 넣지 않고 TIFF 따로, Arial/Helvetica, 폭 166 mm(두 단), 선화 ≥1200 dpi → 1200 dpi RGB TIFF LZW. 그림 안 설명문 없음, 한글 없음.
#  Fig 1 (a) 전 기간 잔차 공간 RR 지도 (b) 조율·연령표준화율 추이 · Fig 2 강건 4개 변수의 모형별 RR · SDC 그림 (a) EHSA (b) 세 창 핫·콜드스팟 횟수
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_htnd import load, ROB, SHP
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 166 * MM; DPI = 600; LW = 0.3
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 7.5, "legend.title_fontsize": 8, "axes.linewidth": 1.0, "xtick.major.width": 1.0, "ytick.major.width": 1.0, "lines.linewidth": 1.0, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")   # 결합은 시군구 코드(cd)로만, 이름 결합 금지
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
rd = lambda f: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", dtype={"sigungu_cd": str})
def letter(ax, ch, dx=0.0, dy=1.03, fs=28):   # AJPM 11/14: 패널 문자 대문자·모든 패널 같은 크기(28pt)
    ch = ch.upper()   # 패널 문자: 지도는 30pt 볼드(11/8 저자 지시: 3~4배), 선 그림은 14pt
    ax.text(dx, dy, ch, transform=ax.transAxes, fontsize=fs, fontweight="bold", va="bottom", ha="left", clip_on=False)
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=1.0); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0   # 방위표·축척(좌표 단위 m)
    bx, by = x0 + 0.62 * W_, y0 + 0.04 * H_
    from matplotlib.patches import Rectangle as _Rc   # 06 지도 규칙: 0-50-100 km 흑백 2단 축척
    hh = 0.012 * H_
    ax.add_patch(_Rc((bx, by), 50000, hh, facecolor="black", edgecolor="black", linewidth=1.0)); ax.add_patch(_Rc((bx + 50000, by), 50000, hh, facecolor="white", edgecolor="black", linewidth=1.0))
    for xx, lab in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + xx, by + hh + 0.008 * H_, lab, ha="center", va="bottom", fontsize=7)
    ax.text(bx + 108000, by + 0.5 * hh, "km", ha="left", va="center", fontsize=7)
    from matplotlib.patches import Polygon as _Pg   # 06 지도 규칙: annotate(arrowstyle) 금지 → 슬림 채움 삼각형 + "N"
    nx, ny = x0 + 0.90 * W_, y0 + 0.70 * H_   # 11/8 저자 지시: 방위표 3배, 삽입 지도와 겹치지 않게
    ax.add_patch(_Pg([[nx - 0.036 * W_, ny], [nx + 0.036 * W_, ny], [nx, ny + 0.21 * H_]], closed=True, facecolor="black", edgecolor="none"))
    ax.text(nx, ny + 0.225 * H_, "N", ha="center", va="bottom", fontsize=24)
def save(fig, k, dpi=None):
    DPI = dpi or globals()["DPI"]
    p = os.path.join(FIG, f"AJPM_Fig{k}.png"); fig.savefig(p, dpi=DPI, facecolor="white"); plt.close(fig)   # 폭 166 mm 고정(bbox tight 쓰지 않음)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(DPI, DPI))
    if not str(k).startswith("S"): im.save(os.path.join(OUTF, f"Figure_{k}.tif"), dpi=(DPI, DPI), compression="tiff_lzw")
    return im.size

# Fig 1 — 전국 추세: (a) 고혈압성·순환계 ASR 지수(2011=100) (b) 순환계 중 고혈압성 비율
yrs = sorted(N["asr"]); A = N["asr"]; AC = N["asr_circ"]; CS = N["circ_share"]
fig, (a0, a1) = plt.subplots(1, 2, figsize=(W, 2.9)); fig.subplots_adjust(left=0.08, right=0.98, top=0.82, bottom=0.17, wspace=0.32)
a0.plot(yrs, [100 * A[t] / A[2011] for t in yrs], color="#b2182b", marker="s", ms=2.5, lw=1.2, label="Hypertensive diseases (I10-I13)")
a0.plot(yrs, [100 * AC[t] / AC[2011] for t in yrs], color="#404040", marker="o", ms=2.5, lw=1.2, label="All circulatory diseases (I00-I99)")
a0.set_ylim(0, 110); a0.set_xticks([2011, 2014, 2017, 2020, 2024]); a0.set_ylabel("Age-standardized rate (2011 = 100)"); a0.set_xlabel("Year")
a0.spines[["top", "right"]].set_visible(False); a0.legend(frameon=False, loc="lower left", fontsize=7); letter(a0, "a", dx=-0.20, dy=1.07)
a1.plot(yrs, [100 * CS[t] for t in yrs], color="#b2182b", marker="s", ms=2.5, lw=1.2)
a1.set_ylim(0, 14); a1.set_xticks([2011, 2014, 2017, 2020, 2024]); a1.set_ylabel("Hypertensive share of circulatory deaths, %"); a1.set_xlabel("Year")
a1.spines[["top", "right"]].set_visible(False); letter(a1, "b", dx=-0.20, dy=1.07)
s1 = save(fig, 1, 1000)

# Fig 2 — 잔차 공간 RR 지도: (a) 고혈압성 (b) 순환계 전체, 부산·울산 확대
S6 = rd("S6_spatial_RR.csv"); assert len(S6) == 229
AR = pd.read_csv(os.path.join(RS, "S45_coding_area.csv")); AR["fbd_region"] = AR.fbd_region.map(NFC)
s6r = S6.assign(r=S6.fbd_region.map(NFC)).set_index("r"); AR["cd"] = AR.fbd_region.map(s6r.sigungu_cd.astype(str)); assert AR.cd.notna().all()
BR = [0, 0.8, 0.9, 0.95, 1, 1.05, 1.1, 1.2, 99]; LB = ["<0.80", "0.80-0.89", "0.90-0.94", "0.95-0.99", "1.00-1.04", "1.05-1.09", "1.10-1.19", "\u22651.20"]
PAL = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
fig = plt.figure(figsize=(W, 4.6))
panels = [("a", S6.set_index("sigungu_cd").RR, S6.set_index("sigungu_cd")["class"]),
          ("b", AR.set_index("cd").RR_broad, AR.set_index("cd").P_gt1_broad.map(lambda p: "hotspot" if p > 0.95 else ("coldspot" if p < 0.05 else "neutral")))]
for i, (ch, rr, cl) in enumerate(panels):
    ax = fig.add_axes([0.005 + 0.5 * i, 0.20, 0.47, 0.76]); gg = G.copy(); gg["v"] = gg.cd.map(rr); gg["c"] = gg.cd.map(cl); assert gg.v.notna().all() and gg.c.notna().all()
    gg.plot(ax=ax, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); mapax(ax)
    gg[gg.c == "coldspot"].boundary.plot(ax=ax, color="#2171B5", linewidth=1.0, linestyle=(0, (2.0, 1.2))); gg[gg.c == "hotspot"].boundary.plot(ax=ax, color="black", linewidth=1.0); letter(ax, ch, dy=0.97)
    ins = fig.add_axes([0.005 + 0.5 * i + 0.335, 0.46, 0.13, 0.20]); sub = gg[gg.sido.isin(["21", "26"])]   # 부산 21·울산 26
    sub.plot(ax=ins, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW)
    sub[sub.c == "hotspot"].boundary.plot(ax=ins, color="black", linewidth=1.0); sub[sub.c == "coldspot"].boundary.plot(ax=ins, color="#2171B5", linewidth=1.0, linestyle=(0, (2.0, 1.2)))
    ins.set_xticks([]); ins.set_yticks([]); [sp.set_linewidth(1.0) for sp in ins.spines.values()]
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=0.5, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=1.0, label="Hot spot"), Patch(facecolor="none", edgecolor="#2171B5", linewidth=1.0, linestyle="--", label="Cold spot")]
fig.legend(handles=h, title="Residual spatial rate ratio", loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=5, frameon=False, columnspacing=0.8, handlelength=1.3)
assert set(G[G.sido == "21"].cd) <= set(S6[S6.fbd_region.str.startswith("부산")].sigungu_cd.astype(str)) and (G.sido == "21").sum() == 16
s2 = save(fig, 2)

# SDC 그림
EH = rd("S11_ehsa.csv")
CATS = [f"{a} {b}" for b in ("hot", "cold") for a in ("New", "Consecutive", "Intensifying", "Persistent", "Diminishing", "Sporadic", "Oscillating", "Historical")] + ["No pattern"]
EPAL = {"New hot": "#fdd0a2", "Consecutive hot": "#fdae6b", "Intensifying hot": "#a50f15", "Persistent hot": "#de2d26", "Diminishing hot": "#fc9272", "Sporadic hot": "#fee0d2", "Oscillating hot": "#d6a5c9", "Historical hot": "#bcbddc",
        "New cold": "#c6dbef", "Consecutive cold": "#9ecae1", "Intensifying cold": "#08519c", "Persistent cold": "#3182bd", "Diminishing cold": "#6baed6", "Sporadic cold": "#deebf7", "Oscillating cold": "#a1d99b", "Historical cold": "#c7e9c0", "No pattern": "#f7f7f7"}
WM = rd("S4b_window_spatialRR.csv")
nh = WM[WM["class"] == "hotspot"].groupby("sigungu_cd").size(); nc = WM[WM["class"] == "coldspot"].groupby("sigungu_cd").size()
assert int((nh == 3).sum()) == N["hot_all_windows"] and int((nc == 3).sum()) == N["cold_all_windows"]
fig, (a0, a1) = plt.subplots(1, 2, figsize=(W, 4.4)); fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.31, wspace=0.04)
gg = G.copy(); gg["c"] = gg.cd.map(EH.set_index("sigungu_cd").EHSA); assert gg.c.notna().all()
gg.plot(ax=a0, color=[EPAL[c] for c in gg.c], edgecolor="#a0a0a0", linewidth=LW); mapax(a0); letter(a0, "a", dy=0.97)
cnt = EH.EHSA.value_counts(); pres = [c for c in CATS if c in cnt.index]
a0.legend(handles=[Patch(facecolor=EPAL[c], edgecolor="#777777", linewidth=0.5, label=f"{c} ({cnt[c]})") for c in pres], title="Category (districts)", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
hh = gg.cd.map(nh).fillna(0).astype(int); cc = gg.cd.map(nc).fillna(0).astype(int)
gg["k"] = np.where((hh > 0) & (cc > 0), 9, hh - cc)
KP = {-3: "#2166AC", -2: "#67A9CF", -1: "#D1E5F0", 0: "#f7f7f7", 1: "#FDDBC7", 2: "#EF8A62", 3: "#B2182B", 9: "#c2a5cf"}
KL = {-3: "Cold spot in 3 windows", -2: "Cold spot in 2", -1: "Cold spot in 1", 0: "Neither", 1: "Hot spot in 1", 2: "Hot spot in 2", 3: "Hot spot in 3 windows", 9: "Hot or cold by window"}
gg.plot(ax=a1, color=[KP[k] for k in gg.k], edgecolor="#a0a0a0", linewidth=LW); mapax(a1); letter(a1, "b", dy=0.97)
kc = gg.k.value_counts()
a1.legend(handles=[Patch(facecolor=KP[k], edgecolor="#777777", linewidth=0.5, label=f"{KL[k]} ({kc.get(k, 0)})") for k in (3, 2, 1, 0, -1, -2, -3, 9) if kc.get(k, 0)], title="Windows 2011-2015, 2016-2019, 2020-2024", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
sS = save(fig, "S1")

# Fig 3 — 주요 3개 변수의 모형별 MRR
LAB = {"im_specialists_per_100k": "Internal medicine\nspecialists", "moderate_pa_rate": "Moderate-or-higher\nphysical activity", "basic_livelihood_rate": "Basic livelihood\nrecipients"}
ORD = list(LAB)
MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "#000000", "o"),
       ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)][:3], "#E08214", "P"),
       ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3], "#B2182B", "D"),
       ("Province-by-year effects", lambda v: N["s41"][("C4_sido_year_iid", v)][:3], "#7f7f7f", "^"),
       ("With ill-defined cause share", lambda v: N["s45"][("Z1_illdefined", v)][:3], "#6a3d9a", "X"),
       ("All circulatory deaths", lambda v: N["s45"][("Z2_broad_outcome", v)][:3], "#2166AC", "s"),
       ("Within-district component", lambda v: N["bw"][v + "__within"][:3] if v + "__within" in N["bw"] else None, "#67A9CF", "v")]
vals = [(v, l, f(v), c, m) for v in ORD for l, f, c, m in MOD if f(v) is not None]
lo_all = min(t[2][1] for t in vals); hi_all = max(t[2][2] for t in vals)
fig, ax = plt.subplots(figsize=(W, 4.0)); fig.subplots_adjust(left=0.22, right=0.98, top=0.98, bottom=0.26)
off = np.linspace(-0.34, 0.34, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, col, mk), o in zip(MOD, off):
        r = f(v)
        if r is None: continue
        e, lo, hi = r; ax.plot([lo, hi], [i + o] * 2, color=col, lw=1.0); ax.plot(e, i + o, marker=mk, color=col, ms=3.4, mew=0, ls="none")
ax.axvline(1, color="#404040", lw=1.0, ls=":"); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
xt = [0.85, 0.90, 0.95, 1.00, 1.05, 1.10]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Mortality rate ratio per 1 standard deviation (95% credible interval)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=c, marker=m, lw=1.0, ms=3.4, mew=0, label=l) for l, _, c, m in MOD], loc="upper center", bbox_to_anchor=(0.36, -0.17), ncol=3, frameon=False)
s3 = save(fig, "S2", 1000)   # AJPM 표+그림 ≤4 → 그림 3을 Appendix Figure 2로
for k, s, dd in zip((1, 2, "S2", "S1"), (s1, s2, s3, sS), (1000, 600, 1000, 600)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/dd*25.4:.0f} x {s[1]/dd*25.4:.0f} mm @ {dd} dpi")
