#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_FILE="$SCRIPT_DIR/local_result_viewer.py"
PORT="${RESULT_VIEWER_PORT:-8501}"
URL="http://127.0.0.1:${PORT}"
LOG_FILE="${TMPDIR:-/tmp}/mmp_result_viewer.log"

if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display alert "Python 3 is not installed on this Mac."'
  exit 1
fi

if ! command -v streamlit >/dev/null 2>&1; then
  osascript -e 'display alert "Streamlit is not installed. Run: pip3 install streamlit"'
  exit 1
fi

if ! curl -fsS "$URL" >/dev/null 2>&1; then
  nohup streamlit run "$APP_FILE" --server.port "$PORT" >"$LOG_FILE" 2>&1 &
  sleep 3
fi

open "$URL"
