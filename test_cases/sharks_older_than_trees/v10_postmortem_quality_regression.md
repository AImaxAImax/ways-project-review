# v10 Postmortem — Why Quality Regressed

## User reaction
The v10 ControlNet output looked like the earlier POC frames again, not like the higher-quality challenger direction.

## What happened
I over-weighted the old v7 cut-out/PIL layouts as the control source. Canny ControlNet preserved the crude geometry too strongly, so DreamShaper mostly repainted the old simple shapes instead of elevating the frame into the higher-quality style.

In short: **the control reference was too low-quality, so the controlled output inherited the low-quality look.**

## Lesson
Do not use the v7 procedural frames as final control references at high strength. They are useful for story blocking only, not as art-quality control sources.

## Correct next move
Use the higher-quality challenger images as the visual quality target, then control only the semantic layout lightly.

Possible fixes:
1. Lower control strength dramatically and increase denoise, so the model can escape the POC look.
2. Build cleaner high-quality reference sketches/silhouettes, not crude full-color POC frames.
3. Use DreamShaper/SDXL style challengers as style references and only use simple masks/composition guides for layout.
4. Generate one premium hero frame at a time; do not produce a full contact sheet until the first frame is actually better.

## Revised rule
If a control pass looks like the reference too much, the reference is functioning as a ceiling. For premium output, the control image must provide composition only, not visual finish.
