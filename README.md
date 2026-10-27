# BLOODSKY Craft107

Public Android modification project based on the user-authorized KaScada Smart Craft 1.0.7 (107). Production signing secrets and original source archives are not stored in this repository.

## Status
**EXPERIMENTAL / NOT RELEASE READY.** Source-pinned APK builds, temporary QA v1/v2/v3 signing, Android 11 offline installation and launch, main menu without legacy license banner, and local project creation into the original editor were verified by [run 40544090316](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40544090316). The license-free functional matrix, complete vendor-cloud isolation, persistent save/reopen/import/export, real device/network transports and release signing have **not** passed. See [acceptance checklist](docs/ACCEPTANCE.md).

## Goals
- Keep original HMI visuals, project format, FBD, USB, Bluetooth, local Wi-Fi/Modbus, local import/export.
- Remove KaScada Cloud runtime, cloud import/export and cloud connection type 4 without breaking connection types 1–3.
- Remove original activation and purchase paths under the owner's confirmed modification permission.
- Deliver an independently signed, device-tested BLOODSKY release after successful tests.

## Inputs
- Original version: 1.0.7 (107), package `ru.kascada.modbus`.
- Original APK SHA-256: `11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f`.
- Original decoded archive SHA-256: `92d12206bde746f5a76c89e0c3311119287b14bb26cdc8ca36d515e2fca01f7a`.
- Android-verified, ephemeral QA-signed candidate SHA-256 at run 40544090316: `38899e7b60ecf050d7f3244c8520d596727808ef0f01e6c4d6aa2c35590117cd` (experimental, not a stable release).

## Security
Never commit original licensed binaries, decoded proprietary archives, signing keys, passwords, API keys, devices' project secrets, or build artifacts. Never put secrets or original binaries in Git history. Experimental QA APKs are temporarily published only as GitHub Actions artifacts; they use short-lived, unique keys and cannot upgrade each other. Do not treat them as release packages. The certificate is different from the original; in-place updates of the original app will fail on signature mismatch. Back up projects before testing.

## Release criteria
See [acceptance checklist](docs/ACCEPTANCE.md). No stable release until acceptance tests are actually performed.
