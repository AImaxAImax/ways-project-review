# Source Acquisition Status — Saturn Hexagon Storm

Date: 2026-06-06T02:10:03-07:00  
Lane: **source acquisition only** — no render, no video generation, no paid/credit services.

## Summary

Acquired the NASA/JPL/Cassini source candidates named in the strict WAYS rework packet and `research/source_generation_plan.md`. Both NASA Images JPEGs and Photojournal TIFFs were downloaded where available.

Manifest written:

- `test_cases/saturn_hexagon_storm/assets/source_nasa/source_manifest.json`

Downloaded source files:

- `assets/source_nasa/PIA21052_orig.jpg` — 1024×1024 JPEG, SHA256 `826d33dae2961f3ecf67dc33e6aaedce489d82c4f2aa48453238a98df828d96f`
- `assets/source_nasa/PIA21052_photojournal.tif` — 1024×1024 TIFF, SHA256 `ec4b3416f81cf8906e65b30a98cf3c2a58f67bcc1625bb11d433138df1dfc31a`
- `assets/source_nasa/PIA17122_orig.jpg` — 1016×1016 JPEG, SHA256 `3a8ebaaf774354b75d2fcc0e4812eb0f0a976df08f3ebb7c43eba20a3ee3f09c`
- `assets/source_nasa/PIA17122_photojournal.tif` — 1016×1016 TIFF, SHA256 `784d6c4321fc659d29ebfd3811a8084c37ffe0cab59b54b385116621b627c3bc`
- `assets/source_nasa/PIA14646_orig.jpg` — 1016×1016 JPEG, SHA256 `3e3271e68f28495f9d14a82555ad2b7fc7d4b0fbd424c172405d673b25b7e141`
- `assets/source_nasa/PIA14646_photojournal.tif` — 1016×1016 TIFF, SHA256 `9c270a0170d67ad468f10361653acfa2ce3ee04b14331fdac16e7e80548131ed`
- `assets/source_nasa/PIA20507_orig.jpg` — 1020×1020 JPEG, SHA256 `60be1b2e88eb9810bdc1b754726890a09e0cd322b8828bbd208d267c1915ed28`
- `assets/source_nasa/PIA20507_photojournal.tif` — 1020×1020 TIFF, SHA256 `a021377259c9ce0b466574b32aa870e7cdcda01b4a528087bdf73504032c8022`
- `assets/source_nasa/AS17-148-22727_blue_marble_orig.jpg` — 4579×4579 JPEG, SHA256 `cb4c3d2da98ee72130ebfd2ea472fc84ede6726002c2a8c9cabd86e4deea9f0f`

## Provenance / rights notes

All acquired Saturn candidates are NASA/JPL/Cassini public mission imagery from NASA Images / NASA Science / JPL Photojournal URLs. The Shot 03 Earth scale proxy is NASA/Apollo 17 public-domain imagery from NASA Images (`AS17-148-22727`, the Blue Marble / full-disk Earth view). No paid stock, no paid generation, no credit-spend lanes, and no upload/publish actions were used.

Use NASA/JPL-Caltech/Space Science Institute credit for Cassini assets and NASA/Apollo 17 credit for the Earth proxy in internal descriptions/metadata as appropriate, but **do not burn credits, NASA logos, labels, insignia, UI, or source-page text into plates**. NASA imagery is generally not copyrighted in the U.S.; NASA identity/endorsement restrictions still apply.

## Beat coverage candidates

| Shot | Required visual proof | Candidate source status |
|---|---|---|
| 01 | Immediate phone-size read of Saturn north-pole hexagon | **Candidate found:** PIA21052 primary. PIA14646 secondary only if vertical crop keeps the hexagon instantly readable. |
| 02 | Real NASA/Cassini north-pole hexagon / jet stream proof | **Candidate found:** PIA21052 primary. PIA17122 secondary for documentary polar-weather detail. |
| 03 | One hexagon side bracketed with tiny Earth proxy, no text/numbers | **Source acquisition unblocked:** PIA21052 is the Saturn source plate; `AS17-148-22727_blue_marble_orig.jpg` is a zero-text/right-safe NASA Apollo 17 full-disk Earth proxy. Finished bracket/composite still must be locally created and QC'd. |
| 04 | Inside-hexagon storms/vortex spinning | **Candidate found:** PIA17122 primary. PIA21052 central storm secondary. PIA20507 texture/reference only. |
| 05 | Pullback showing strange shape is weather on Saturn | **Candidate found:** PIA21052 primary. PIA14646/PIA20507 secondary only if they do not dilute the hexagon proof. |

## Zero-text / artifact status

Source candidates are raw planetary image files and should not contain captions, labels, logos, UI, watermarks, or source-page text in the image pixels. However, this lane did **not** produce cropped/enhanced plates and did **not** run a final OCR/manual artifact pass on finished plates.

Current status:

- Source-page text was not used as image material.
- NASA logos/insignia/mission patches were not downloaded as plate material.
- Downloaded source files are image-only Saturn plates plus one image-only Apollo 17 Earth disk proxy for Shot 03.
- Final zero-text pass is still required after crops, contrast/sharpening, bracket overlay, and Earth proxy are built.

## What still fails / blocks Gate 2 plate readiness

Gate B source acquisition is substantially complete, but **plates are not ready for Josh/QA yet**.

Remaining blockers:

1. No five vertical proof plates have been created.
2. No contact sheet exists at `outputs/gate2_plate_qc/contact_sheet.jpg`.
3. No phone-size readability check has been performed on finished plates.
4. No OCR/manual text-artifact check has been performed on finished plates.
5. Shot 03 source acquisition is unblocked by the NASA Apollo 17 Earth disk proxy, but still needs local masking/scale placement plus bracket/side highlight.
6. PIA14646 and PIA20507 remain secondary only; they may fail if the hexagon/claim does not read instantly at phone size.
7. The highest-resolution source assets found in the NASA/JPL lanes are roughly 1k square; crops must be tested carefully for WAYS phone-size clarity.

## Readiness verdict

- **Source manifest ready:** yes.
- **Right-safe/free source candidates acquired:** yes.
- **Shot 03 Earth proxy acquired:** yes — NASA/Apollo 17 `AS17-148-22727`, zero-text full-disk Earth candidate.
- **Gate B:** likely pass pending human/agent confirmation of manifest and rights notes.
- **Gate C / plate QC:** not started.
- **Ready for Josh/QA plate review:** **no** — generate and QC still plates first.
- **Render permission:** **no** — do not render until Gate A-D pass in writing.
