# BLOODSKY Craft107

Private Android application modification project based on the user-authorized KaScada Smart Craft 1.0.7 (107).

## Status
**EXPERIMENTAL / NOT RELEASE READY.** The existing candidate was patched and JAR/v1-signed, but it has **not** been installed, launched, or tested on Android. Android APK v2/v3 signing, device/network tests, offline operation, and complete audit of vendor cloud/licensing are outstanding.

## Goals
- Keep original HMI visuals, project format, FBD, USB, Bluetooth, local Wi-Fi/Modbus, local import/export.
- Remove KaScada Cloud runtime, cloud import/export and cloud connection type 4 without breaking connection types 1–3.
- Remove original activation and purchase paths under the owner's confirmed modification permission.
- Deliver an independently signed, device-tested BLOODSKY release after successful tests.

## Inputs
- Original version: 1.0.7 (107), package `ru.kascada.modbus`.
- Original APK SHA-256: `11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f`.
- Original decoded archive SHA-256: `92d12206bde746f5a76c89e0c3311119287b14bb26cdc8ca36d515e2fca01f7a`.
- Locally prepared candidate SHA-256: `08b4e42ba69e56de69650a753966ebcf4e21c97502760c981130bff22d67a357` (experimental; not validated on device).

## Security
Never commit original licensed binaries, decoded proprietary archives, signing keys, passwords, API keys, devices' project secrets, or build artifacts. Keep signed candidates outside Git history until acceptance and distribution review. The certificate is different from the original; in-place updates of the original app will fail on signature mismatch. Back up projects before testing.

## Release criteria
See [acceptance checklist](docs/ACCEPTANCE.md). No stable release until acceptance tests are actually performed.
