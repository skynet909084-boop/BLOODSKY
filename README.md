# BLOODSKY Craft107

Public Android modification project based on the user-authorized KaScada Smart Craft 1.0.7 (107). Production signing secrets and original source archives are not stored in this repository.

## Status
**EXPERIMENTAL / NOT RELEASE READY.** Source-pinned APK builds, temporary QA v1/v2/v3 signing, Android 11 offline installation and launch, main menu without legacy license banner, and local project creation, save, saved-list persistence and reopening of the original editor were verified by [run 40553232969](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40553232969). The license-free functional matrix, complete vendor-cloud isolation, widget-rich project roundtrip and import/export, real device/network transports and release signing have **not** passed. See [acceptance checklist](docs/ACCEPTANCE.md).

## Goals
- Keep original HMI visuals, project format, FBD, USB, Bluetooth, local Wi-Fi/Modbus, local import/export.
- Remove KaScada Cloud runtime, cloud import/export and cloud connection type 4 without breaking connection types 1–3.
- Remove original activation and purchase paths under the owner's confirmed modification permission.
- Deliver an independently signed, device-tested BLOODSKY release after successful tests.

## Inputs
- Original version: 1.0.7 (107), package `ru.kascada.modbus`.
- Original APK SHA-256: `11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f`.
- Original decoded archive SHA-256: `92d12206bde746f5a76c89e0c3311119287b14bb26cdc8ca36d515e2fca01f7a`.
- Android-verified, ephemeral QA-signed candidate SHA-256 at run 40553232969: `ce69092ff99474629f4197b1f52dd43c2a43abdc27952c6e79fb7791f47eb31f` (experimental, not a stable release).

## Locale and appearance

The original Russian translations are retained: the Android 11 UiAutomator dump in [QA run 40549513523](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40549513523) shows all six main-menu buttons in Russian when the device locale is `ru-RU`. The test was initially a false failure because labels render uppercase, and has been fixed with Unicode-aware UI checks. Language follows the device locale; this build does not force Russian on every device.

A separate manual [visual-compare.yml](.github/workflows/visual-compare.yml) installs the untouched original and BLOODSKY on the same Android emulator, captures Russian menus, compares button bounds/labels/pixels, and saves differences. The original-versus-patched comparison [passed at run 40553233451](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40553233451): identical button bounds and 0.0 pixel difference on all six main-menu button regions. This covers only the six main-menu controls, **not** all widgets or screens.

## Security
Never commit original licensed binaries, decoded proprietary archives, signing keys, passwords, API keys, devices' project secrets, or build artifacts. Never put secrets or original binaries in Git history. Experimental QA APKs are temporarily published only as GitHub Actions artifacts; they use short-lived, unique keys and cannot upgrade each other. Do not treat them as release packages. The certificate is different from the original; in-place updates of the original app will fail on signature mismatch. Back up projects before testing.

## Release criteria
See [acceptance checklist](docs/ACCEPTANCE.md). No stable release until acceptance tests are actually performed.
