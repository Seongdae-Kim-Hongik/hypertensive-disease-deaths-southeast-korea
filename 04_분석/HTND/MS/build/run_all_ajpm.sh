#!/bin/bash
# run_all_ajpm.sh — 17호 고혈압성질환 사망 AJPM 전체 빌드(2026-11-14). 결과 표(공개 안 함)가 있어야 돈다. 네트워크 접근 없음.
set -e; cd "$(dirname "$0")"
python3 figs_htnd.py 2>&1 | grep -v Warning
python3 build_ajpm_htnd.py
python3 esm_ajpm.py
python3 strobe_ajpm.py
python3 cover_ajpm.py
python3 sanitize_docx.py --no-anon ../out/Manuscript.docx ../out/Tables.docx ../out/Appendix.docx ../out/Cover_Letter.docx ../out/Highlights.docx ../out/Declaration_of_Interests.docx ../out/STROBE_Checklist.docx
python3 check_ajpm_htnd.py
