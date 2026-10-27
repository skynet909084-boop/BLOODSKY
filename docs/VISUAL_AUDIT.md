# Original 1.0.7 versus BLOODSKY — visual acceptance

## Method

Manual [visual-compare.yml](../.github/workflows/visual-compare.yml) on Android 11 (API 30), one emulator, `ru-RU`, network disabled, original APK with pinned SHA-256 versus newly patched/signed BLOODSKY. It captures both main screens plus UiAutomator hierarchies, then compares six native buttons: create, load, delete, export, import and exit. App branding and removed licensing text are intentionally excluded. A pass proves only these six main-menu controls, **not** complete full-app visual parity.

## First measured difference

In [run 40551998623](https://github.com/skynet909084-boop/BLOODSKY-Craft107/actions/runs/40551998623), all six controls had changed Y coordinates/sizes, while horizontal bounds matched. Original first button `[146,125][934,315]`; BLOODSKY `[146,125][934,324]`. Original exit button `[146,1207][934,1398]`; BLOODSKY `[146,1251][934,1451]`. The original license TextView was removed from layout using `android:visibility=gone`, which collapses its allotted height and alters the layout weight distribution.

The correction in [7bd0080](https://github.com/skynet909084-boop/BLOODSKY-Craft107/commit/7bd008001c8a6a450c911187578aa85b36050b0b) changes only that license TextView to `android:visibility=invisible` (compiled enum value `1`), so the text stays hidden **but its original measured height is preserved**. Cloud-only views retain `gone` (enum value `2`), still removing them from layouts. The static verifier now checks the distinct attribute values.

## Outstanding verification

An exact-head visual rerun and functional Russian-project rerun were dispatched at commit `7bd0080`. Do **not** declare pixel-level parity until both pass. Additional screens, component/widget layouts, FBD and density/device variations require independent visual tests and cannot be inferred from main-menu agreement.
