# SOURCE ACQUISITION STATUS — tardigrade_survival_mode

Timestamp: 2026-06-06T10:07:25Z  
Lane: strict WAYS source acquisition only  
Render status: **NO RENDER PERFORMED**  
Paid/credit lanes: **NOT USED**

## What was done

- Re-checked the existing `assets/source_rework/source_manifest.json` and local source directory.
- Verified the previously blocked Commons downloads are now present locally, including the key PLOS/Commons video source `C002`.
- Ran source/provenance probing only; no render/video generation was performed.
- Targeted the open/free search gap for tardigrade rehydration / water-return / reactivation. Wikimedia Commons search surfaced no better zero-text, open/free source for a literal water droplet/meniscus/flow returning in-frame beyond the PLOS/Commons research video already acquired.

## Best right-safe rehydration/reactivation source found

**C002 — `Desiccation-Tolerance-in-the-Tardigrade-Richtersius-coronifer-Relies-on-Muscle-Mediated-Structural-pone.0085091.s001.ogv`**

- Local file: `test_cases/tardigrade_survival_mode/assets/source_rework/C002_Desiccation_Tolerance_in_the_Tardigrade_Richtersius_coronife.ogv`
- Source platform: Wikimedia Commons / PLOS ONE supplement
- License: **CC BY 4.0**
- Authors/source: Halberg K, Jørgensen A, Møbjerg N; PLOS ONE supplemental movie
- Duration from `ffprobe`: **76.52 s**
- Embedded source metadata explicitly says the movie covers entrance into and exit out of anhydrobiosis in four stages:
  - I: active hydrated
  - II: dehydrating / “tucking in”
  - III: anhydrobiotic tun state
  - IV: **rehydration**

This makes C002 the best acquired right-safe source for Beat 04 if Gate B accepts a source-supported rehydration/reactivation sequence showing the animal re-expanding/resuming activity.

Probe frames were extracted for acquisition/QC reference only:

- `test_cases/tardigrade_survival_mode/outputs/gate2_plate_qc/c002_rehydration_probe/C002_t58.jpg`
- `test_cases/tardigrade_survival_mode/outputs/gate2_plate_qc/c002_rehydration_probe/C002_t65.jpg`
- `test_cases/tardigrade_survival_mode/outputs/gate2_plate_qc/c002_rehydration_probe/C002_t72.jpg`

Sampled frames did not show obvious title-card/text in the acquisition probe, but final selected crops still need normal plate QC for scale bars, microscope UI, labels, and anatomy clarity.

## Precise remaining blocker / gap

No better open/free/right-safe source was found that clearly and cleanly shows **literal water returning in-frame** — e.g. a visible droplet, meniscus, or flow entering the microscope field — while also showing a credible tardigrade rehydrating/reactivating and having zero unavoidable text/logos/UI.

So the gap is now narrow and precise:

- **Covered:** source-supported tardigrade desiccation → tun → rehydration/reactivation sequence via C002, CC BY 4.0.
- **Not yet covered:** a clean visible water-return/droplet/meniscus moment in-frame under an open/free license.

## Safe fallback if Gate B requires visible water-return

Do **not** fake or overclaim a literal water-flow shot.

Use a truthful before/after edit only if the script/visual wording is changed to match:

1. Verified tun/desiccated state from `C002` and/or `C004`.
2. Verified active/post-water/reactivated state from `C002`, `C007`, `C001`, `C005`, or `C006`.
3. Avoid visual claims of a visible droplet/meniscus unless an actual selected frame shows it.

Safe wording direction:

- Keep: “Then when water comes back, **some can** wake up again.”
- Adjust visual note from “water returning / droplet flows in” to: “cut from tun state to source-supported post-water active/reactivated state.”

## Manifest update

Updated:

- `test_cases/tardigrade_survival_mode/assets/source_rework/source_manifest.json`

Key changes:

- Marked local downloads as present rather than blocked by HTTP 429.
- Promoted `C002` as the best Beat 04 rehydration/reactivation source.
- Changed Gate B assessment from broad weak coverage to **partial pass with precise visible-water-return gap**.
- Recorded the safe fallback that requires script/visual wording to avoid overclaiming.
