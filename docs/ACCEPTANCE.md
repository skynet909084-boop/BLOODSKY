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

## Verified offline save/list/reopen — 2026-10-27

On pinned original KaScada 1.0.7 (107) patched to BLOODSKY, Android 11 emulator [run 40546269289](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40546269289), commit `f329cc3e67314b6679dc9d6f847fb2bbe33cf0fe`, **PASS**: offline signed install, no legacy license label, created project `BLOODSKYQA`, opened `mbCanvas`, saved through original exit confirmation, found persisted project in project load list (16 screens, one network device), tapped project and reopened `mbCanvas` successfully. Captured saved-list hierarchy, emulator UI and screenshot; no reported AndroidRuntime fatal exceptions. QA APK hash `ef69277aed617f80b62b13b04d9e7dccc655711e997a04041ed034ec8d2c2424`. This is a single empty project persistence smoke and not a full editor/FBD/media roundtrip.


## Russian UI baseline — 2026-10-27

The source-pinned, QA-signed app **does display Russian** when the Android device locale is `ru-RU`. The UiAutomator hierarchy and screenshot collected on API 30 in [run 40549513523](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40549513523) show `СОЗДАТЬ НОВЫЙ ПРОЕКТ`, `ЗАГРУЗИТЬ ПРОЕКТ`, `УДАЛИТЬ ПРОЕКТ`, `ЭКСПОРТ ПРОЕКТА`, `ИМПОРТ ПРОЕКТА`, `ВЫХОД`. The run was marked failed **only because** the test searched for a mixed-case string and the original interface renders uppercase. This has been replaced by `tests/assert_russian_menu.py` which matches exact UI control resource IDs with Unicode casefold. No Russian resources had to be invented or replaced. Changing the TEST emulator's locale does not force Russian on user devices.

**Important:** a later [run 40550421060](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40550421060) failed when `am start` raced the Package Manager after framework restart; its package manifest and launcher activity were present. The CI test now disables incremental install and waits for launcher resolution. Await exact-head acceptance before declaring all Russian editor and persistence screens passed.

## Russian Android 11 full offline regression — PASSED 2026-10-27

[GitHub Actions #40551320774](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40551320774) at exact tested commit `721d5544ddbb2d51b6dcdd18beca85aeb3a19858` **PASS**: source-pinned APK and static integrity; temporary QA v1/v2/v3 signature; Android 11 set to `ru-RU`; six original Russian main-menu controls verified by real UiAutomator node IDs (Unicode casefold); no legacy license text; local project created, saved through original dialog, found in local saved list and reopened into `mbCanvas`. Original editor screenshot shows localized `Экран: 1`. Signed QA APK SHA-256: `de3257a756f5d1b2a519f83ad63f6735e35733543ed2a26bf5b79520aced3ee4`. The prior package-manager startup race in #40550421060 was resolved using nonincremental ADB install and waiting for the Android launcher resolver.

This **does not** prove full native-device compatibility, localization on devices whose system language is not Russian, FBD widgets, external import/export or KaScada Cloud network isolation. The UI visual comparison of the original and BLOODSKY is tracked separately in the manual `visual-compare.yml` workflow.
