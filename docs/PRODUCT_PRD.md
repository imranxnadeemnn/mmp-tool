# MMP Tool PRD

## Product Name

MMP Test Tool

## Purpose

Provide Ad Ops with a lightweight internal tool to:

- generate platform-specific tracking URLs for test campaigns
- create QR codes for generated URLs
- view result records tied to Advertising IDs through Redash

## Problem Statement

Ad Ops needs a simple way to generate test tracking links and validate outcomes without manually editing macros or directly using Redash for every step. The existing workflow is error-prone, requires technical familiarity, and is slowed down by VPN-only Redash access.

## Goals

- Reduce manual editing of tracking URLs.
- Standardize macro replacement for supported tracking links.
- Make test-link generation accessible through a simple hosted UI.
- Preserve result-viewing capability for VPN-only Redash access.
- Support a small internal team on macOS.

## Non-Goals

- Public customer-facing deployment.
- Full analytics workflow management.
- Multi-tenant authentication and permissioning.
- Centralized server-side Redash access from Render.

## Users

- Primary users: Ad Ops team members
- Secondary users: internal marketing ops or QA users

## Key Constraints

- Redash is reachable only through office VPN.
- Render free tier is used for the hosted web UI.
- Ad Ops users are on macOS.
- Result viewing must happen locally on VPN-connected machines.

## Core User Flows

### 1. Generate Tracking URL

- User opens the hosted Render URL.
- User pastes a base tracking URL.
- User selects platform.
- System replaces supported macros such as `{bundle_id}` and `{click_id}`.
- System applies AppsFlyer signing only for AppsFlyer URLs.
- System returns a final URL and QR code.

### 2. View Result

- User opens the hosted Render URL.
- User selects the `View Result` tab.
- User clicks `Launch Local Mac Result Viewer`.
- Browser triggers the installed local macOS launcher.
- Launcher starts the local Streamlit result viewer if needed.
- User enters Advertising ID in the local viewer.
- Local viewer queries Redash from the VPN-connected Mac and shows results.

## Functional Requirements

- Hosted UI must expose `Generate URL` and `View Result` tabs.
- Generate flow must support Android and iOS bundle substitution.
- Generate flow must generate a new click ID per request.
- AppsFlyer signing must only apply to AppsFlyer URLs.
- View Result flow must launch a local macOS helper via custom protocol.
- Local installer must configure and register the macOS launcher once per machine.
- Local result viewer must support searching by Advertising ID.

## Non-Functional Requirements

- Hosted UI should be simple, low-maintenance, and easy to explain.
- Hosted UI should tolerate Render free-tier cold starts.
- Local result viewer should open within a few seconds after launch.
- Errors should be understandable by non-engineering users.

## Success Metrics

- Ad Ops can generate links without engineering help.
- Ad Ops can launch the local result viewer in one click after one-time setup.
- Reduction in malformed test URLs.
- Reduction in manual Redash usage for routine validation.

## Risks

- Render free tier cold starts and service sleep behavior.
- Local setup friction on first use.
- Redash API key management on user laptops.
- Dependence on office VPN for result viewing.
- Local launcher issues due to macOS security prompts.

## Mitigations

- Provide a simple rollout checklist and user guide.
- Keep the local installer to a single command.
- Use a one-click launcher from the hosted UI.
- Test on one pilot Mac before sharing broadly.

## Future Enhancements

- Signed macOS installer package for easier rollout.
- Better macro coverage and template presets by MMP/vendor.
- In-app health check for local launcher presence.
- Move hosted UI off Render free tier if adoption grows.
