# Higgsfield Video Route QA — Test 01

## Credit preflight
- Route: Higgsfield browser UI
- Model: Seedance 2.0 GENERAL
- Settings before spend: 8s, 9:16, 480p
- Observed button cost: `Generate 48 24`
- Credit-control decision: submitted exactly one minimum-resolution paid test. Reduced from the visible 1080p cost of `72` credits to `24` credits at 480p before generating.

## Output files
- Original download: `higgsfield_mantis_mechanism_test01_480p.mp4`
- Silent working copy: `higgsfield_mantis_mechanism_test01_480p_silent.mp4`
- Contact sheet: `contact_sheet_higgsfield_mantis_test01.jpg`
- Prompt: `higgsfield_mantis_mechanism_test01_prompt.txt`
- Preflight record: `preflight_test01.json`

## Technical verification
`ffprobe` confirmed:
- Original: H.264 MP4, 496x864, 8.08s, includes AAC audio despite silent prompt.
- Silent copy: H.264 MP4, 496x864, 8.04s, video-only.

## Visual QA
Score: **7.2 / 10 as a source plate**

Strengths:
- Very readable underwater macro composition.
- Clear orange striking appendage moving toward a dark shell/target.
- Bubble formation and impact flash read well on a phone-sized contact sheet.
- Clean negative space in the top/center for captions or overlays.
- No visible text/logos/UI in the generated video.

Weaknesses:
- Appendage reads somewhat like a crab claw/pincer rather than a biologically exact mantis shrimp raptorial club.
- Cavitation bubble is visually clear but simplified/stylized.
- Target looks generic shell-like, not a precise prey/shell object.
- Original file unexpectedly includes audio, so use the silent copy.

## Decision
**Keep. Do not spend more credits yet.**

This is good enough to use as a mechanism/background plate or to intercut with our clearer caption/diagram layers. It is not perfect enough to be the sole scientific proof shot, but it gives the needed visual hook: strike → bubble → flash/impact.

Recommended next step: integrate the silent 480p plate into the current mantis short build and use captions/overlays to correct the biology/readability instead of rerolling immediately.
