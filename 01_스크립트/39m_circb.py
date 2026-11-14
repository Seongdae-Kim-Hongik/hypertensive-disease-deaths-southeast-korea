#!/usr/bin/env python3
# 39m_circb — 17호 HTND 사망진단 코딩 민감도용 넓은 결과(순환계통 질환 전체 I00-I99)의 세분 간접표준화 E (2026-11-08, 39m_alz_broad 복제).
#  39m_build_Estd_mort.py 원본은 건드리지 않고, 원문을 읽어 사인 필터만 두 사인 합으로 바꿔 실행한다(연령 구간·분모·재척도 규칙 동일).
#  입력: 04_분석/CIRCB/panel_CIRCB.csv (= panel_HTND_std3.csv, cases = 99c-htnd CIRC_deaths) — 이 스크립트가 먼저 만든다.
#  산출: 02_패널/CIRCB_Estd2.csv, 02_패널/CIRCB_national_agerates_mort.csv
#  사용: ST_FBDZIP=<창원 교정 인구> python3 39m_circb.py
import os, sys, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
NFC = lambda s: unicodedata.normalize("NFC", str(s))
P = pd.read_csv(os.path.join(ROOT, "04_분석", "HTND", "panel_HTND_std3.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)
X = pd.read_csv(os.path.join(ROOT, "02_패널", "HTND_mort_extra_261108.csv"), encoding="utf-8-sig"); X["fbd_region"] = X.fbd_region.map(NFC)
P = P.drop(columns=["cases"]).merge(X[["year", "fbd_region", "CIRC_deaths"]].rename(columns={"CIRC_deaths": "cases"}), on=["year", "fbd_region"], validate="one_to_one")
assert len(P) == 3206 and P.cases.notna().all()
os.makedirs(os.path.join(ROOT, "04_분석", "CIRCB"), exist_ok=True)
P.to_csv(os.path.join(ROOT, "04_분석", "CIRCB", "panel_CIRCB.csv"), index=False, encoding="utf-8-sig")
print(f"[39m-circb] panel_CIRCB: 14년 I00-I99 {int(P.cases.sum()):,}")
src = open(os.path.join(HERE, "39m_build_Estd_mort.py"), encoding="utf-8").read()
rep = [('TAG = sys.argv[1]; assert TAG in CAUSES, TAG; NC = CAUSES[TAG]', 'TAG = "CIRCB"; NC = ["순환계통 질환 (I00-I99)"]'),
       ('& (N.cause == NC)]', '& N.cause.isin(NC)]'),
       ('tot = N[N.age == "계"].set_index("year").value; unk = N[N.age == "연령미상"].set_index("year").value.reindex(tot.index).fillna(0)',
        'tot = N[N.age == "계"].groupby("year").value.sum(); unk = N[N.age == "연령미상"].groupby("year").value.sum().reindex(tot.index).fillna(0)')]
for a, b in rep:
    assert src.count(a) == 1, a; src = src.replace(a, b)
i = src.index('old = pd.read_csv(os.path.join(ROOT, "02_패널", f"{TAG}_Estd.csv")')
j = src.index("\n", src.index("\n", i) + 1)   # 선별 E_std 대조 두 줄은 ALZB에 해당 없음
k = src.index("Gs = OUT.groupby")
src = src[:i] + src[k:]
sys.argv = ["39m_build_Estd_mort.py", "CIRCB"]
exec(compile(src, os.path.join(HERE, "39m_build_Estd_mort.py"), "exec"), {"__file__": os.path.join(HERE, "39m_build_Estd_mort.py"), "__name__": "__main__"})
