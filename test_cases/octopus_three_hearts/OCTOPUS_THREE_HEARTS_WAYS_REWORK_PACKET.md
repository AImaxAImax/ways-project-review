# Octopus Three Hearts — strict WAYS rework packet

Date: 2026-06-06
Slug: `octopus_three_hearts`
Status: **REJECTED / DO NOT PUBLISH / DO NOT RENDER AGAIN UNTIL GATES PASS**

## 1) Rejection summary

Josh rejected the current candidate as **5/10**. It fails the current WAYS bar for these reasons:

- **Not say-dog-see-dog:** the visuals are mostly decorative octopus shots and do not literally prove the three-heart claim beat-by-beat.
- **Bad source images:** current render manifest uses SDXL plate paths for all five shots, not approved premium documentary plates.
- **AI/artifact risk:** current prompt/output lane explicitly relied on generated plates/I2V and must be treated as failed because tentacle/anatomy artifacts were called out.
- **Wrong voice/template:** any rework must use the approved WAYS template and `elevenlabs_george`; no alternate voice, caption system, or layout is acceptable.
- **Public progression blocked:** existing outputs are internal failed artifacts only. Do not upload, publish, or send another below-gate video.

Inspected failure context:

- `script.md` and `storyboard_manifest.json` describe the claim, but do not force literal proof visuals.
- `outputs/wan22_template_v01/manifest.json` uses `assets/sdxl_wan_template_v01_plates/...` for all shots.
- `assets/inat_source_v01/source_manifest.json` includes mixed/licensing/problematic source entries, including one all-rights-reserved entry and CC-BY-NC entries; these are not acceptable as an automatic publish-safe premium source plan.
- `outputs/final_polish_wan22_template_v01/upload_metadata.json` shows a captioned candidate exists; it remains rejected.

## 2) Required say-dog-see-dog beats

The rebuild must make every spoken/captioned claim visible in the shot, with no vague beauty-roll filler.

| Beat | Voice/caption intent | Required literal visual proof |
|---|---|---|
| 1 | “An octopus has three hearts.” | Real premium documentary octopus plate/clip. Three clean visual pulse markers appear on the octopus body area in sync with the line. No anatomy diagram, no labels, no fake organ cutaway. Caption carries the words; image shows exactly three pulses. |
| 2 | “Two hearts push blood through the gills.” | Same or matched real octopus plate. Two side/gill-area pulses only. Motion/graphic treatment must make “two” unmistakable: two synchronized pulse rings/arrows/soft glow paths toward the gill area. No extra third pulse in this beat. |
| 3 | “The third sends blood to the rest of the body.” | One central/systemic-heart pulse only, followed by a subtle body-wide flow/glow spreading through the mantle/arms. Viewer can distinguish “one heart” vs “rest of body” without reading labels. |
| 4 | “When it swims, that body heart can slow down.” | Real octopus swimming/jetting or credible documentary motion. The systemic pulse visibly slows/fades during swimming while captions say the claim. Must not imply all hearts stop. |
| 5 | “That’s why crawling can be easier than swimming.” | Real octopus crawling/walking along seafloor/rock. Pulse returns steadier while crawl motion is visible. This beat must contrast crawling with the prior swim beat; not just another generic octopus shot. |

Minimum sequence rule: **3 hearts → 2 gill hearts → 1 systemic heart → systemic slows during swim → crawling is easier**. If the viewer cannot follow that sequence with sound off except captions, reject before render.

## 3) Source-plate requirements

Hard requirements for every source plate/clip before any render:

- **Premium documentary octopus only:** real underwater octopus footage/stills with intact anatomy, high clarity, natural color, no cartoon/CG/anatomy-diagram look.
- **No fake anatomy:** no cutaway organs, no mislabeled biology, no fabricated internal heart placement pretending to be literal anatomy.
- **No tentacle/body artifacts:** all arms must connect naturally to the body; no duplicated arms, detached tentacles, melted suckers, distorted eyes, warped mantle, or impossible body geometry.
- **Zero non-caption text:** no watermarks, logos, UI, subtitles, species labels, lower thirds, diagram labels, or readable background text. Only the final WAYS captions may contain text.
- **Rights-safe/free lane only:** use public-domain, CC-BY, CC0, or project-owned/permitted sources. Do not use all-rights-reserved, unclear-license, NC-only for monetized/public upload, stock previews, paid libraries, or credit/spend lanes.
- **Vertical crop safe:** source must survive 1080x1920 crop without cutting off key octopus anatomy or proof markers.

## 4) Approved voice/template requirements

The rework is only valid if assembled with the approved WAYS package:

- Voice: **`elevenlabs_george` only**.
- Template: **approved WAYS template only** — large centered creator captions, white text, yellow active/key word, thick black outline, no bottom-block template, no alternate brand style.
- Caption text: punchy WAYS wording; no extra explanatory labels inside the image.
- Audio polish: match current WAYS loudness/pacing standards; do not use an unapproved narrator or generic TTS.
- Runtime target: short-form pacing; no slow documentary explainer drift.

## 5) Concrete no-paid source acquisition / generation plan

Do this before any new render:

1. **Collect real source candidates from free/right-safe lanes only:** Wikimedia Commons, NOAA/public-domain ocean footage, government/science outreach archives with explicit public-domain or CC-BY terms, creator-permitted material, or existing project-owned documentary footage. No paid stock, no credits, no NC-only, no unclear-license downloads.
2. **Build a source manifest first:** for each candidate record URL, license, attribution, local path, resolution, crop notes, and which beat it supports.
3. **Select plates by beat, not by beauty:** pick one plate/clip for each required proof beat above. Reuse a single high-quality octopus plate where continuity helps, but only if each beat remains visually distinct.
4. **Add only minimal proof graphics if needed:** soft pulse rings/glow/flow paths are acceptable if they clarify the claim. They must be abstract overlays, not fake anatomical diagrams, and must contain no text.
5. **Create a plate contact sheet before render:** include all selected plates/crops plus beat IDs and acceptance notes in the packet metadata, not burned into the image.
6. **Human/agent preflight gate:** reject any source with watermark/text, uncertain rights, anatomy issues, poor crop, or inability to show the exact beat.
7. **Only after gates pass:** render using approved WAYS template + `elevenlabs_george`. Do not auto-promote a below-gate render to publish/upload.

## 6) Acceptance gates before render

A new render may start only after all gates pass:

- [ ] Rejection acknowledged: current `wan22_template_v01` / `final_polish_wan22_template_v01` candidate remains failed internal artifact.
- [ ] Script/storyboard revised so each line has a literal say-dog-see-dog visual.
- [ ] Five beat-matched plates/clips selected from rights-safe/free sources only.
- [ ] Source manifest includes license/attribution/provenance for every source.
- [ ] Plate contact sheet reviewed: premium documentary look, no text/watermarks/logos, no fake anatomy, no tentacle artifacts.
- [ ] Proof graphics plan approved: exactly three/two/one pulse logic is clear and non-diagrammatic.
- [ ] Voice locked to `elevenlabs_george`.
- [ ] Assembly locked to approved WAYS template/caption style.
- [ ] No paid/credit lane used.
- [ ] No upload/publish action queued.

## Key next steps

1. Revise `script.md` / `storyboard_manifest.json` to encode the five literal proof beats above.
2. Acquire and manifest rights-safe real octopus source plates/clips from free lanes only.
3. Produce a source contact sheet and gate it before any render.
4. After source gate approval, rebuild with `elevenlabs_george` and approved WAYS template only.
