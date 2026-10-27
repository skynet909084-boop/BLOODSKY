# Experimental QA build

This project reconstructs the signed QA APK from a SHA-256 pinned original, without uploading original APKs or keystore secrets into Git history. Run the manual `build-qa.yml` workflow or set `BLOODSKY_ORIGINAL_APK` to the original path and run `bash tools/build_candidate.sh` with Android SDK 35 build-tools, Java and Python installed. New ephemeral QA key generated per build. The resulting APK is only for experimental validation. A valid production release requires a stable private signing key, complete Cloud isolation audit, verified project saving, and real Android hardware acceptance.


## GitHub runner allocation blocker — 2026-10-27

All workflows failed **before any step executed** on the private repository. This is a runner/account service issue, not a measured APK test failure:

- QA run [40535965967](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40535965967), job 122301184993: runner ID zero, no steps or logs.
- QA run [40537282008](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40537282008), job 122305851429: identical failure.
- Minimal [runner probe 40537527808](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40537527808), job 122306709131: also failed with no steps. This probe does not build an APK.

Repository Actions is enabled, `allowed_actions=all`, token permission read-only. Monthly billing usage was reported, but the account's spending cap/runner entitlement was not available through the API. Account owner should check GitHub Settings > Billing and licensing > Actions usage/spending limits and inspect the failed run banner; if account limits allow running, contact GitHub Support with the three run IDs.

Until runner provisioning works (or a trusted self-hosted runner is configured), emulator acceptance and v2/v3 signing **are not passed**. The separate local fixed-input static check reproduced unsigned APK SHA-256 `2649230a43855cf97599ed0ed005f8a3679f280c64e4cf1792c75123629d8a5b`; it does not substitute for Android acceptance. Do not mark a release as ready.
