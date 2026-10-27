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
