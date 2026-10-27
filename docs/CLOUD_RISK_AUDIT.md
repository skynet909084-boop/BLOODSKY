# Remaining KaScada Cloud / licensing risk audit

Source: user-provided decoded KaScada Smart Craft 1.0.7 (107) archive, SHA-256 `92d12206bde746f5a76c89e0c3311119287b14bb26cdc8ca36d515e2fca01f7a`.

The current 15-method patch disables the three Cloud connector thread `run()` methods and upload entry points, hides cloud-specific UI and removes kind-4 entries from the connection-type resource array. **This is not proof that all cloud dependencies are removed.**

Additional source references requiring review:

- `smali/ru/himik/nightscream/kascada/mbCanvas.smali` instantiates `CloudConnector` and `Connections/Cloud/b`; the cloud constructors and cleanup methods must be reviewed, not just thread `run()`.
- `smali_classes2/ru/himik/nightscream/kascada/CustomComponents/d.smali` constructs and starts `Connections/Cloud/a`; check constructor side effects and the original link from settings.
- `smali_classes2/ru/himik/nightscream/kascada/Firebase/MyFirebaseMessagingService.smali` has a push handler for `connect_web_socket_to_kascadacloud`; it broadcasts `hmikascada.ru.broadcast` with extra `webSocket=true`. The 15th patch makes this `q(...)` callback a no-op, preventing this message-handler path. Firebase SDK registration and other vendor service initialization still need separate review.
- `smali/ru/himik/nightscream/kascada/Bd/Export/ExportPresenter.smali` embeds `http://kascada-cloud.fvds.ru/projects/upload.php`; verify dead code or prevent all caller access.
- `smali/ru/himik/nightscream/kascada/Bd/h$a.smali` exports `kascadaCloudSlave` and `kascadaCloudRemoteControl` flags in project JSON. Preserve old data safely but do not activate either feature.
- Cloud `connectionsId=4` and `idServer=4` may still occur in imported projects. Reject or quarantine them before runtime dispatch.
- Audit any Google Play billing, Firebase initialization, remote update checks and license/count checks independently of main-menu hiding.

## Acceptance

A stable release requires a runtime network audit showing zero connection attempts to KaScada Cloud/vendor endpoints and no activation dependence, including first launch, project reopen/import, app restart, foreground/background, reconnect, and old project data. Run UI tests plus actual I/O hardware gates. Do not report `Cloud fully removed` based only on bytecode and string searches.
