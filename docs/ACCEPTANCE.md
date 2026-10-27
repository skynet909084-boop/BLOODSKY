# BLOODSKY — release acceptance

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

- QA run [40535965967](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40535965967), job 122301184993: runner ID zero, no steps or logs.
- QA run [40537282008](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40537282008), job 122305851429: identical failure.
- Minimal [runner probe 40537527808](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40537527808), job 122306709131: also failed with no steps. This probe does not build an APK.

Repository Actions is enabled, `allowed_actions=all`, token permission read-only. Monthly billing usage was reported, but the account's spending cap/runner entitlement was not available through the API. Account owner should check GitHub Settings > Billing and licensing > Actions usage/spending limits and inspect the failed run banner; if account limits allow running, contact GitHub Support with the three run IDs.

Until runner provisioning works (or a trusted self-hosted runner is configured), emulator acceptance and v2/v3 signing **are not passed**. The separate local fixed-input static check reproduced unsigned APK SHA-256 `2649230a43855cf97599ed0ed005f8a3679f280c64e4cf1792c75123629d8a5b`; it does not substitute for Android acceptance. Do not mark a release as ready.

## Added project creation gate

The QA emulator now navigates from the offline main menu through **Create a new project**, types a synthetic project name, confirms the dialog, and asserts entry to original `mbCanvas`. It captures UI, screenshots and AndroidRuntime errors. This is a smoke test only; actual save/reload/export/import, FBD behavior and hardware are not yet covered.

## Verified Android 11 editor navigation — 2026-10-27

Exact-head successful run: [40544090316](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40544090316), commit `499eec2`. Confirmed source-pinned APK, v1/v2/v3 ephemeral QA signatures, offline home activity, absence of the old license banner, local project creation `BLOODSKY_QA`, and foreground `mbCanvas` landscape editor. Project screenshot and UI hierarchy are in `BLOODSKY QA diagnostics (historical artifact)`; no app fatal exceptions in AndroidRuntime. This does **not** prove project persistence/import/export, complete license-free feature availability, or cloud traffic isolation.

## Verified offline save/list/reopen — 2026-10-27

On pinned original KaScada 1.0.7 (107) patched to BLOODSKY, Android 11 emulator [run 40546269289](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40546269289), commit `f329cc3e67314b6679dc9d6f847fb2bbe33cf0fe`, **PASS**: offline signed install, no legacy license label, created project `BLOODSKYQA`, opened `mbCanvas`, saved through original exit confirmation, found persisted project in project load list (16 screens, one network device), tapped project and reopened `mbCanvas` successfully. Captured saved-list hierarchy, emulator UI and screenshot; no reported AndroidRuntime fatal exceptions. QA APK hash `ef69277aed617f80b62b13b04d9e7dccc655711e997a04041ed034ec8d2c2424`. This is a single empty project persistence smoke and not a full editor/FBD/media roundtrip.


## Russian UI baseline — 2026-10-27

The source-pinned, QA-signed app **does display Russian** when the Android device locale is `ru-RU`. The UiAutomator hierarchy and screenshot collected on API 30 in [run 40549513523](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40549513523) show `СОЗДАТЬ НОВЫЙ ПРОЕКТ`, `ЗАГРУЗИТЬ ПРОЕКТ`, `УДАЛИТЬ ПРОЕКТ`, `ЭКСПОРТ ПРОЕКТА`, `ИМПОРТ ПРОЕКТА`, `ВЫХОД`. The run was marked failed **only because** the test searched for a mixed-case string and the original interface renders uppercase. This has been replaced by `tests/assert_russian_menu.py` which matches exact UI control resource IDs with Unicode casefold. No Russian resources had to be invented or replaced. Changing the TEST emulator's locale does not force Russian on user devices.

**Important:** a later [run 40550421060](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40550421060) failed when `am start` raced the Package Manager after framework restart; its package manifest and launcher activity were present. The CI test now disables incremental install and waits for launcher resolution. Await exact-head acceptance before declaring all Russian editor and persistence screens passed.

## Russian Android 11 full offline regression — PASSED 2026-10-27

[GitHub Actions #40551320774](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40551320774) at exact tested commit `721d5544ddbb2d51b6dcdd18beca85aeb3a19858` **PASS**: source-pinned APK and static integrity; temporary QA v1/v2/v3 signature; Android 11 set to `ru-RU`; six original Russian main-menu controls verified by real UiAutomator node IDs (Unicode casefold); no legacy license text; local project created, saved through original dialog, found in local saved list and reopened into `mbCanvas`. Original editor screenshot shows localized `Экран: 1`. Signed QA APK SHA-256: `de3257a756f5d1b2a519f83ad63f6735e35733543ed2a26bf5b79520aced3ee4`. The prior package-manager startup race in #40550421060 was resolved using nonincremental ADB install and waiting for the Android launcher resolver.

This **does not** prove full native-device compatibility, localization on devices whose system language is not Russian, FBD widgets, external import/export or KaScada Cloud network isolation. The UI visual comparison of the original and BLOODSKY is tracked separately in the manual `visual-compare.yml` workflow.

## Exact source-code + Russian emulator regression — PASS after visual fix

[run 40553232969](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40553232969) at commit `7bd0080` passed static code integrity, source-pinned build, ephemeral v1/v2/v3 signing, Russian home controls, no license text, offline creation of `BLOODSKYQA`, persistence to saved-project list, and reopening in `mbCanvas`. QA-signed APK SHA-256 `ce69092ff99474629f4197b1f52dd43c2a43abdc27952c6e79fb7791f47eb31f`. Separately the original-vs-patched six-button main-menu visual comparison [run 40553233451](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40553233451) was pixel-exact (0.0 mean RGB channel difference and no significant pixel changes on every button; same rectangles). Full HMI/FBD, complex project roundtrip, Cloud no-traffic, real controllers and production signing remain release blockers.

## HMI palette visibility — verified with pinned experimental APK

[QA run #40555577752](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40555577752) **PASS** on Android 11 ru-RU, using exactly the previously verified binary SHA-256 `ce69092ff99474629f4197b1f52dd43c2a43abdc27952c6e79fb7791f47eb31f` from run #40553232969. After offline installation and original local project create/save/reopen, `menu_bar_component` opened the HMI component palette and UiAutomator found original resource IDs `tab_switch`, `tab_button`, `tab_digital_setters`, `tab_text`, `tab_digital_indicator`. Additional original controls including lamp, alarm, sound, graph and gif were visible in the saved UI dump and screenshot. No AndroidRuntime fatal exception occurred.

The next exact-binary test now additionally toggles the panel's `switch_layout` and validates original FBD controls `tab_var`, `tab_fb_rs`, `tab_fb_timer`. This confirms panel accessibility only; placing, editing, connecting or saving real components is not yet covered.

## FBD component palette — Android 11 PASS

[run #40556295416](https://github.com/skynet909084-boop/BLOODSKY/actions/runs/40556295416) completed **SUCCESS**, using previously verified (not rebuilt) APK SHA-256 `ce69092ff99474629f4197b1f52dd43c2a43abdc27952c6e79fb7791f47eb31f`. On `ru-RU` Android 11, offline project create/save/reopen remained green. The UI first opened the original HMI palette and validated setter/text/indicator controls; tapping source-original `switch_layout` switched to the FBD logic palette. UiAutomator verified `tab_var`, `tab_fb_rs`, `tab_fb_timer`; the captured hierarchy also contains multiple variable, float, counter, trigger, math, MQTT and sensor blocks from the original logic component resource layout. Saved full screenshot and UI hierarchy under `out/emulator/component-palette/logic-*` in the GitHub Actions artifact `BLOODSKY-pinned-APK-palette-QA`.

This is **palette-display acceptance only**. Actual editing/dragging of widget/FBD elements, logic execution, persistence of non-empty project data, and real controller I/O remain unverified. New source rebuilds still require the scoped GitHub secret described in `docs/BUILD.md`.
