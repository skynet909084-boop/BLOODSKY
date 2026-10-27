# Experimental QA build

This project reconstructs the signed QA APK from a SHA-256 pinned original, without uploading original APKs or keystore secrets into Git history. Run the manual `build-qa.yml` workflow or set `BLOODSKY_ORIGINAL_APK` to the original path and run `bash tools/build_candidate.sh` with Android SDK 35 build-tools, Java and Python installed. New ephemeral QA key generated per build. The resulting APK is only for experimental validation. A valid production release requires a stable private signing key, complete Cloud isolation audit, verified project saving, and real Android hardware acceptance.


## GitHub runner allocation blocker — 2026-10-27

All workflows failed **before any step executed** on the private repository. This is a runner/account service issue, not a measured APK test failure:

- QA run [40535965967](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40535965967), job 122301184993: runner ID zero, no steps or logs.
- QA run [40537282008](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40537282008), job 122305851429: identical failure.
- Minimal [runner probe 40537527808](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40537527808), job 122306709131: also failed with no steps. This probe does not build an APK.

Repository Actions is enabled, `allowed_actions=all`, token permission read-only. Monthly billing usage was reported, but the account's spending cap/runner entitlement was not available through the API. Account owner should check GitHub Settings > Billing and licensing > Actions usage/spending limits and inspect the failed run banner; if account limits allow running, contact GitHub Support with the three run IDs.

Until runner provisioning works (or a trusted self-hosted runner is configured), emulator acceptance and v2/v3 signing **are not passed**. The separate local fixed-input static check reproduced unsigned APK SHA-256 `2649230a43855cf97599ed0ed005f8a3679f280c64e4cf1792c75123629d8a5b`; it does not substitute for Android acceptance. Do not mark a release as ready.

## Archived original source — required setup after 2026-10-27

The legacy `skynet909084-boop/BLOODSKY-Android` repository is now **PRIVATE + ARCHIVED** at the owner's request. The older unauthenticated `curl` GitHub release URL now returns 404 in public Actions. Example: [QA run 40554934483](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40554934483). Do not make the old repo public merely to restore builds, and do not upload the original APK or plaintext signing keys to this public repository.

To re-enable reproducible builds, the owner must create a fine-grained GitHub personal access token limited to `BLOODSKY-Android` with repository permission **Contents: Read-only**, and add it ONLY as `BLOODSKY_SOURCE_READ_TOKEN` under `BLOODSKY-Craft107 → Settings → Secrets and variables → Actions → New repository secret`. Never put the token in a commit, chat message, issue, artifact or URL. Workflow secret is scoped only to the original-release download step. `tools/fetch_pinned_original.sh` downloads asset `KaScada.Smart.Craft.1.0.7.08.02.2026.apk` from old private release `kascada-analysis-1` via `gh` and independently checks expected SHA-256 `11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f`. For local builds, supply the exact original to `BLOODSKY_ORIGINAL_APK` and `tools/build_candidate.sh` without uploading it.

While the private source token is not set, [qa-pinned-artifact.yml](../.github/workflows/qa-pinned-artifact.yml) can temporarily test the **already-built** experimental candidate from green run [40553232969](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40553232969), verifying exact SHA-256 `ce69092ff99474629f4197b1f52dd43c2a43abdc27952c6e79fb7791f47eb31f` before emulator launch. That GitHub artifact expires **2026-10-30**; it cannot rebuild patched code or replace persistent source access. A green emulator test of that pinned APK is not a green source rebuild.

The earlier private GitHub runner blocker was resolved by making only this new project PUBLIC. Current blocker is **private input retrieval**, not hosted runner quota. Release remains gated by Cloud, FBD, widget import/export, hardware verification and persistent production signing.
