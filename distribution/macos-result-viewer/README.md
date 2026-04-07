# MMP Result Viewer for macOS

This folder is a shareable one-time installer for the local Redash result viewer.

## What Users Need

- A Mac
- Office VPN connection when viewing results
- A Redash API key

## Install

1. Download and extract this folder on the Mac.
2. Double-click `Install MMP Result Viewer.command`.
3. If macOS blocks it, open:
   `System Settings -> Privacy & Security`
   and allow it to run.
4. Enter the Redash API key when prompted.

## Daily Use

1. Open the hosted MMP Tool page in the browser.
2. Go to `View Result`.
3. Click `Launch Local Mac Result Viewer`.
4. Allow the `mmptool://` prompt if the browser asks.

The local viewer will open at `http://127.0.0.1:8501`.

## Troubleshooting

- If the launcher does not open, run:

```bash
open ~/Applications/"MMP Result Viewer Launcher.app"
```

- If the local viewer does not load, check:

```bash
tail -n 100 /tmp/mmp_result_viewer.log
```
