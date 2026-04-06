#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUNDLE_DIR="$ROOT_DIR/distribution/macos-result-viewer"

mkdir -p "$BUNDLE_DIR"

cp "$ROOT_DIR/install_macos_result_launcher.sh" "$BUNDLE_DIR/Install MMP Result Viewer.command"
cp "$ROOT_DIR/local_result_viewer.py" "$BUNDLE_DIR/"
cp "$ROOT_DIR/result_view.py" "$BUNDLE_DIR/"
cp "$ROOT_DIR/clickhouse_client.py" "$BUNDLE_DIR/"
cp "$ROOT_DIR/config.py" "$BUNDLE_DIR/"

chmod +x "$BUNDLE_DIR/Install MMP Result Viewer.command"

echo "Bundle prepared at: $BUNDLE_DIR"
