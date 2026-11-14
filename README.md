# Hypertensive disease mortality across Korean districts, 2011-2024

Analysis code for the manuscript

> Kim S. *Blood pressure care indicators do not account for the lasting excess of hypertensive disease deaths in Busan, South Korea.* Submitted to *American Journal of Preventive Medicine*.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24210468 (v1.0.0).

## Contents

This repository contains code only. The processed district-year data (master table, analytic panel, expected deaths, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/HTND/sets_HTND_std3.json`, `sets_HTND_s577.json`, `sets_HTND_s2.json`, `sets_HTND_s8.json`, `sets_HTND_ssx.json`, `config_HTND_std3.json`, `run_std3_chain.sh` | Covariates with expected directions, forced controls, comparison outcomes and model settings (principal model `std3`; sensitivity versions with the queen contiguity graph, without the share aged 80 or older, with ten-group expected deaths, and with sex-and-age standardized expected deaths) |
| `04_분석/HTND/MS/` | Scripts that read the result tables and write every number, table and figure in the manuscript and Appendix, including `content_ajpm.py`, which generates the Methods and Results text (the draft source of the abstract, Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Deaths by underlying cause (hypertensive diseases, ICD-10 I10-I13; all circulatory diseases, I00-I99; ill-defined causes, R00-R99) by district of residence: Statistics Korea, cause-of-death statistics (KOSIS DT_1B34E13), 2011-2024. Comparison outcomes are transport accident deaths (same source) and people treated for infectious diseases (National Health Insurance Service regional statistics).
- National deaths by cause and 5-year age group (to 85 years or older): Statistics Korea (KOSIS DT_1B34E01), fetched by `34_fetch_national_cause_age_deaths.py` (requires a personal KOSIS API key in `~/.kosis_key`; the key is not included).
- Population by 5-year age group: Ministry of the Interior and Safety, resident registration statistics. The 2023 age block of Changwon duplicated the 2022 block and was corrected (`population_override` in the sets files).
- District covariates: Korean Statistical Information Service (KOSIS), the Community Health Survey, National Health Insurance Service general health screening statistics, the public sports facility registry, and a harmonized public district panel (basic livelihood security recipients, internal medicine specialists).

## Pipeline

Run from the repository root (set `ST_DATA_ROOT` and `ST_FBDZIP_CORRECTED` to the local copies of the public source files). R jobs are wrapped in `rslot.sh`, which limits the number of concurrent R processes on a shared machine.

| Step | Script | Output |
|---|---|---|
| 0 | `34_fetch_national_cause_age_deaths.py`, `99m3_screen_mortality_prep.py`, `98_fit_forced.R`, `99m3_screen_mortality.py` | National cause-by-age deaths, screening panels and spatial screening of six causes of death |
| 1 | `99c_extra_canonical_pool_htnd.py` | Assistance and internal medicine indicators, ill-defined cause shares and circulatory deaths joined by district code |
| 2 | `39m_htnd.py` (runs `39m_build_Estd_mort.py` for HTND), `39ms_htnd.py` (runs `39ms_build_Esex_mort.py`), `39m_circb.py` (all circulatory deaths) | Expected deaths by indirect standardization in eighteen 5-year age groups (ten groups and sex-by-age groups for sensitivity) |
| 3 | `80_build_disease_panel_v.py HTND` (`ST_VER=std3`) | Analytic panel |
| 4 | `81_fit_inla.R HTND` (`ST_VER=std3`, `ST_GRAPH=04_분석/HTND/graph_593.graph`, `ST_THREADS=1`; see `04_분석/HTND/run_std3_chain.sh`) | Principal model, set comparison, 200-subset multiverse, window models |
| 5 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `86b_ehsa_modified_mk.py`, `87_window_grid.py` | Maps and emerging hot spot analysis |
| 6 | `88g_sens_prep.py HTND std3 TRANS,INFECT`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` (nb, struct, kh, review) with `kh_constraints.R`, `88z_htnd_coding.R`, `89g_sens_combine.py` | Sensitivity analyses, comparison outcomes, Knorr-Held models, death-certification, access and sodium checks |
| 6b | `88r_reverse_check.R` (`REV`, `AXIS`), `88z2_htnd_post.R`, `88z3_htnd_post.R` | Post hoc checks: association opposite to the expected direction; circulatory deaths excluding hypertensive diseases; forced-controls comparison; Busan estimates after the ill-defined cause share |
| 7 | `04_분석/HTND/MS/build/` (`run_all_ajpm.sh`: `figs_htnd.py`, `build_ajpm_htnd.py`, `esm_ajpm.py`, `strobe_ajpm.py`, `cover_ajpm.py`, `check_ajpm_htnd.py`; `numbers_htnd.py` reads the result tables) | Manuscript, tables, Appendix, figures, STROBE checklist and checks |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## License

Code: MIT (see `LICENSE`). The source statistics remain under the terms of their providers.
