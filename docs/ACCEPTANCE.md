# BLOODSKY Craft107 — release acceptance

- [x] Original APK and decoded source SHA-256 verified.
- [x] Experimental DEX/resource patch produced (14 methods, 6 original entries changed).
- [x] Experimental JAR/v1 signing checked.
- [ ] Security/code review of every activation/billing gate; check original cloud endpoints and unreachable code.
- [ ] Audit all vendor cloud code paths including background services and imported projects (type 4); verify no vendor network traffic.
- [ ] Pin a reproducible build pipeline and ensure no secrets are committed.
- [ ] Sign with supported v2/v3 signature schemes and verify signatures.
- [ ] Install and launch on Android 11 / API 30 and a current Android version.
- [ ] Validate project create/save/reopen/import/export without data loss.
- [ ] Compare interface and widget/FBD behavior against original at identical screen density.
- [ ] Verify local Wi-Fi/Modbus, Bluetooth, USB and device lifecycle.
- [ ] Test airplane/offline use and migration of projects containing Cloud connection type 4 (must fail closed).
- [ ] Review distribution rights and provenance notices.
- [ ] Publish tested release APK and checksums only after all necessary gates pass.

No green check means not yet demonstrated; static patching is not Android acceptance.


## GitHub runner allocation blocker — 2026-10-27

All workflows failed **before any step executed** on the private repository. This is a runner/account service issue, not a measured APK test failure:

- QA run [40535965967](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40535965967), job 122301184993: runner ID zero, no steps or logs.
- QA run [40537282008](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40537282008), job 122305851429: identical failure.
- Minimal [runner probe 40537527808](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40537527808), job 122306709131: also failed with no steps. This probe does not build an APK.

Repository Actions is enabled, `allowed_actions=all`, token permission read-only. Monthly billing usage was reported, but the account's spending cap/runner entitlement was not available through the API. Account owner should check GitHub Settings > Billing and licensing > Actions usage/spending limits and inspect the failed run banner; if account limits allow running, contact GitHub Support with the three run IDs.

Until runner provisioning works (or a trusted self-hosted runner is configured), emulator acceptance and v2/v3 signing **are not passed**. The separate local fixed-input static check reproduced unsigned APK SHA-256 `2649230a43855cf97599ed0ed005f8a3679f280c64e4cf1792c75123629d8a5b`; it does not substitute for Android acceptance. Do not mark a release as ready.

## Added project creation gate

The QA emulator now navigates from the offline main menu through **Create a new project**, types a synthetic project name, confirms the dialog, and asserts entry to original `mbCanvas`. It captures UI, screenshots and AndroidRuntime errors. This is a smoke test only; actual save/reload/export/import, FBD behavior and hardware are not yet covered.

## Verified Android 11 editor navigation — 2026-10-27

Exact-head successful run: [40544090316](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40544090316), commit `499eec2`. Confirmed source-pinned APK, v1/v2/v3 ephemeral QA signatures, offline home activity, absence of the old license banner, local project creation `BLOODSKY_QA`, and foreground `mbCanvas` landscape editor. Project screenshot and UI hierarchy are in `BLOODSKY-Craft107-diagnostics`; no app fatal exceptions in AndroidRuntime. This does **not** prove project persistence/import/export, complete license-free feature availability, or cloud traffic isolation.
