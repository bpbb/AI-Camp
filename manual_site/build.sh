#!/usr/bin/env bash
# build คู่มือนักเรียนจาก docs/*.md เป็น public/index.html
#   bash build.sh   -> เปิด public/index.html ในเบราว์เซอร์เพื่อดูก่อน push
# Vercel รันขั้นตอนเดียวกันนี้เองทุกครั้งที่ push ขึ้น main
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1   # Windows: ให้ Python พิมพ์ภาษาไทยออกจอได้
PY="$(command -v python3 || command -v python)"
"$PY" -c "import markdown, pygments" 2>/dev/null || "$PY" -m pip install --quiet -r requirements.txt
"$PY" tools/build_docs.py public
