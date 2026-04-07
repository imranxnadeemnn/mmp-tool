# Ad Ops Rollout Checklist

## Before Sharing the Render URL

- Confirm the latest Render deploy is live.
- Open the Render URL once and verify the `Generate URL` tab loads.
- Confirm the `View Result` tab shows the `Launch Local Mac Result Viewer` button.
- Make sure the office VPN is working on at least one Mac test machine.
- Make sure the Redash query still returns rows for a known-good Advertising ID.
- Confirm the local launcher install works on one Mac from start to finish.

## One-Time Setup for Each Ad Ops Mac

- Install Python 3 if it is not already installed.
- Open Terminal.
- Go to the project folder:

```bash
cd /Users/inadeem/Documents/mmp_tool
```

- Run the one-time installer:

```bash
./install_macos_result_launcher.sh
```

- Paste the Redash API key when prompted.
- Allow macOS to open the launcher app if Security settings asks for approval.
- Stay connected to office VPN when using the result viewer.

## First-Time Verification Per User

- Open the Render URL.
- In `Generate URL`, generate one known tracking URL.
- In `View Result`, click `Launch Local Mac Result Viewer`.
- Allow the browser to open the `mmptool://` link.
- Confirm one local browser tab opens to `http://127.0.0.1:8501`.
- Search for a known-good Advertising ID and confirm rows appear.

## Team Launch Notes

- Tell users the Render app may be slow on first load after being idle because it is on Render free tier.
- Tell users result viewing depends on office VPN.
- Tell users the local Mac launcher only needs to be installed once per machine.
- Tell users to keep the Render UI for generation and the local viewer for results.

## Support Playbook

- If `Generate URL` is slow on first open, wait up to 60 seconds and refresh.
- If `Launch Local Mac Result Viewer` does nothing, reinstall the local launcher.
- If localhost opens but no data is returned, check office VPN first.
- If localhost does not open, run:

```bash
open ~/Applications/"MMP Result Viewer Launcher.app"
```

- If the viewer still fails, inspect:

```bash
tail -n 50 /tmp/mmp_result_viewer.log
```

## Ongoing Ops

- Re-test the flow after each Render redeploy.
- Keep one known-good Advertising ID for smoke testing.
- Plan to move off Render free tier if the tool becomes a daily dependency.
