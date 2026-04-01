# MMP Tool User Guide

## What This Tool Does

The tool has two parts:

- `Generate URL`: runs in the hosted Render page
- `View Result`: opens a local Mac result viewer that works only when your Mac is connected to office VPN

## Open the Tool

- Open the hosted URL in your browser.

## Tab 1: Generate URL

### Steps

1. Open the `Generate URL` tab.
2. Paste the base tracking URL.
3. Choose `Android` or `iOS`.
4. Click `Generate URL`.
5. Copy the final URL or scan the QR code.

### Notes

- The tool replaces supported macros automatically.
- AppsFlyer signing is only added for AppsFlyer links.
- The first page load may be slow if the Render app was idle.

## Tab 2: View Result

### First-Time Setup on Your Mac

1. Connect to office VPN.
2. Open Terminal.
3. Go to the project folder:

```bash
cd /Users/inadeem/Documents/mmp_tool
```

4. Run:

```bash
./install_macos_result_launcher.sh
```

5. Enter your Redash API key when prompted.
6. Allow macOS to open the launcher if prompted.

### Daily Use

1. Open the hosted Render page.
2. Go to `View Result`.
3. Click `Launch Local Mac Result Viewer`.
4. Allow the `mmptool://` prompt if your browser asks.
5. In the local result viewer, enter the Advertising ID.
6. Click `Check Result`.

## Troubleshooting

### The hosted page is slow to load

- Wait up to 60 seconds.
- Refresh once.

### Clicking `Launch Local Mac Result Viewer` does nothing

- Confirm the one-time installer was run on this Mac.
- Try:

```bash
open ~/Applications/"MMP Result Viewer Launcher.app"
```

### Localhost opens but no results are returned

- Make sure office VPN is connected.
- Re-enter your Advertising ID carefully.

### The local viewer does not open

- Check the local log:

```bash
tail -n 50 /tmp/mmp_result_viewer.log
```

### I need to reinstall the launcher

- Re-run:

```bash
cd /Users/inadeem/Documents/mmp_tool
./install_macos_result_launcher.sh
```

## Best Practices

- Keep office VPN connected when using `View Result`.
- Use the Render page for URL generation.
- Use the local result viewer only for result lookup.
- If something breaks after a new deployment, report the issue with a screenshot and the time it happened.
