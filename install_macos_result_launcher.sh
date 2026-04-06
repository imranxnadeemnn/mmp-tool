#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_ROOT="$HOME/.mmp-result-viewer"
APP_DIR="$INSTALL_ROOT/app"
VENV_DIR="$INSTALL_ROOT/venv"
LAUNCHER_APP="$HOME/Applications/MMP Result Viewer Launcher.app"
RUNNER_SCRIPT="$INSTALL_ROOT/run_result_viewer.sh"
ENV_FILE="$INSTALL_ROOT/viewer.env"
APPLE_SCRIPT="$INSTALL_ROOT/launcher.applescript"

mkdir -p "$APP_DIR" "$HOME/Applications"

for file in local_result_viewer.py result_view.py clickhouse_client.py config.py; do
  cp "$SCRIPT_DIR/$file" "$APP_DIR/$file"
done

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install streamlit requests pandas >/dev/null

if [ ! -f "$ENV_FILE" ]; then
  REDASH_API_KEY="$(osascript <<'APPLESCRIPT'
text returned of (display dialog "Enter your Redash API key for the local result viewer:" default answer "" with hidden answer buttons {"Save"} default button "Save")
APPLESCRIPT
)"

  cat > "$ENV_FILE" <<EOF
export REDASH_API_KEY="$REDASH_API_KEY"
export REDASH_URL="https://redash.aarki.org"
export REDASH_QUERY_ID="28702"
export RESULT_VIEWER_PORT="8501"
EOF
fi

cat > "$RUNNER_SCRIPT" <<EOF
#!/bin/zsh
set -euo pipefail
source "$ENV_FILE"
PORT="\${RESULT_VIEWER_PORT:-8501}"
URL="http://localhost:\${PORT}"
LOG_FILE="\${TMPDIR:-/tmp}/mmp_result_viewer.log"
APP_DIR="$APP_DIR"
PYTHON_BIN="$VENV_DIR/bin/python"

if ! curl -fsS "\$URL" >/dev/null 2>&1; then
  cd "\$APP_DIR"
  nohup "\$PYTHON_BIN" -m streamlit run local_result_viewer.py --server.address 127.0.0.1 --server.port "\$PORT" >"\$LOG_FILE" 2>&1 &

  for _ in {1..20}; do
    if curl -fsS "\$URL" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if ! curl -fsS "\$URL" >/dev/null 2>&1; then
  osascript -e 'display alert "MMP Result Viewer could not be started. Please check /tmp/mmp_result_viewer.log"'
  exit 1
fi

open "\$URL"
EOF

chmod +x "$RUNNER_SCRIPT"

cat > "$APPLE_SCRIPT" <<EOF
on run
    do shell script quoted form of "$RUNNER_SCRIPT" & " >/dev/null 2>&1 &"
end run

on open location this_URL
    do shell script quoted form of "$RUNNER_SCRIPT" & " >/dev/null 2>&1 &"
end open location
EOF

rm -rf "$LAUNCHER_APP"
osacompile -o "$LAUNCHER_APP" "$APPLE_SCRIPT" >/dev/null

/usr/libexec/PlistBuddy -c "Delete :CFBundleURLTypes" "$LAUNCHER_APP/Contents/Info.plist" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes array" "$LAUNCHER_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0 dict" "$LAUNCHER_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLName string com.aarki.mmptool.resultviewer" "$LAUNCHER_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$LAUNCHER_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string mmptool" "$LAUNCHER_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleName MMP Result Viewer Launcher" "$LAUNCHER_APP/Contents/Info.plist"

osascript -e 'display notification "MMP Result Viewer Launcher installed in Applications." with title "MMP Tool"'
open "$LAUNCHER_APP"
