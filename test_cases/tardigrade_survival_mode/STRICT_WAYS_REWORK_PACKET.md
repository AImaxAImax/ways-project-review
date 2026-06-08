# STRICT WAYS REWORK PACKET — tardigrade_survival_mode

Status: **REJECTED / DO NOT PUBLISH / DO NOT RENDER NEW BELOW-GATE VIDEO**

Josh rejected the current candidate as **5/10**. This packet supersedes the current pass and is the gate for any future attempt.

## 1) Rejection summary

Current inspected assets/output references:

- Candidate: `test_cases/tardigrade_survival_mode/outputs/final_polish_wan22_template_v01/publish_candidate_captioned.mp4`
- Preview: `test_cases/tardigrade_survival_mode/outputs/final_polish_wan22_template_v01/discord_preview_captioned.mp4`
- Contact sheet: `test_cases/tardigrade_survival_mode/outputs/final_polish_wan22_template_v01/contact_sheet_final_polish.jpg`
- Base Wan output: `test_cases/tardigrade_survival_mode/outputs/wan22_template_v01/`
- Current source plate lane in manifest/config: `assets/sdxl_wan_template_v01_plates/*.png`

Failure reasons to treat as hard blockers:

1. **Not say-dog-see-dog** — visuals do not plainly show the exact narrated claim as it is spoken.
2. **Bad source images** — source plates are SDXL/generated-looking and not credible microscope/macro tardigrade plates.
3. **AI artifacts / wrong anatomy** — cute/stylized/fake tardigrade body features are not acceptable for WAYS.
4. **Wrong voice/template feel** — future pass must use approved WAYS voice/template only, not an ad-hoc style.
5. Prior internal report called it a pass despite caveat: “stylized/cute tardigrade anatomy.” That caveat is now a rejection blocker.

## 2) Exact say-dog-see-dog beats required

Every beat must visually communicate the spoken claim without relying on abstract graphics or vibes.

### Beat 01 — live/active tardigrade baseline

- VO/caption intent: **“Tardigrades can pause their bodies.”**
- Required visual: credible real microscope/macro tardigrade visible as a tardigrade: barrel body, stubby legs/claws, translucent/soft body, microscope lighting.
- Must show: an active/normal state before the “pause,” preferably slow crawl or water movement.
- Reject if: generic blob, cartoon water bear, monster/cute plush, fake extra limbs, unreadable mush.

### Beat 02 — desiccation into tun state

- VO/caption intent: **“When things get too dry, they curl into a tiny tun.”**
- Required visual: unmistakable before/after or sequential plate of hydrated tardigrade versus contracted tun/barrel state.
- Must show: body curling/contracting, legs withdrawn or less prominent, dry/dehydrated context.
- Acceptable approach: two real/source-supported plates cut in sequence or a very restrained I2V transition from verified hydrated plate to verified tun plate.
- Reject if: random ball, cocoon, egg, alien pod, magical transformation, or invented anatomy.

### Beat 03 — survival/metabolism near pause

- VO/caption intent: **“Their metabolism drops so low it is almost like waiting on pause.”**
- Required visual: real tun-state tardigrade held still, with only microscope focus breathing/particles or an approved caption-only emphasis.
- Must show: the same tun state from Beat 02, visually still and dormant.
- No fake internal organs, heart monitors, HUDs, gauges, labels, or science-text overlays.
- Reject if: abstract motion graphic replaces tardigrade evidence or adds non-caption text.

### Beat 04 — reactivation by water

- VO/caption intent: **“Then when water comes back, some can wake up again.”**
- Required visual: water returning to the microscope field and a tardigrade rehydrating/re-expanding or resuming movement.
- Must show: water droplet/meniscus/flow plus a credible reactivated tardigrade; can use real source sequence or verified microscope clip/stills.
- Wording must preserve **“some can”** to avoid overclaiming.
- Reject if: magic resurrection glow, instant morph, fake tentacles, or impossible anatomy.

### Beat 05 — final survival-trick payoff

- VO/caption intent: **“It is one of nature’s strangest survival tricks.”**
- Required visual: best credible hero tardigrade microscope/macro shot, preferably hydrated and recognizable, with subtle motion.
- Must feel like WAYS: surprising, clean, premium, science-real, no fake documentary UI.
- Reject if: generated creature, plush/cute mascot, or any visible non-caption writing.

## 3) Source-plate requirements

Hard requirements before any render:

- Use **credible microscope/macro tardigrade source plates** only.
- Source must be real/publicly usable/free lane or generated only as a non-final sketch/reference; final plates cannot look AI-generated.
- Plate set must include at minimum:
  1. Hydrated/active tardigrade.
  2. Desiccated/contracted tun-state tardigrade or credible tun-state reference.
  3. Rehydration/reactivation source: real clip/still sequence, water-return plate, or source-supported before/after.
  4. Hero tardigrade plate.
- No fake AI anatomy/artifacts: no extra limbs, melted claws, faces/eyes, tentacles, furry/plush texture, monster mouth, duplicated body segments, impossible symmetry.
- **Zero non-caption text** baked into source plates: no labels, scale bars, watermarks, microscope UI, article captions, logos, lower thirds, subtitles, random letters, or diagram text.
- If a credible source has a scale bar/watermark/text, crop/clean it before plate approval and retain source provenance notes.
- Plates must be vertical 9:16 safe or crop-safe to 1080x1920 without losing the tardigrade/tun.

## 4) Approved voice/template requirements

Hard requirements:

- Voice: **`elevenlabs_george` only**.
- Template: approved WAYS / Wait, Are You Serious? template only; do not use an ad-hoc voice, caption style, or non-WAYS pacing.
- Use the saved approved Wan2.2 A14B I2V short template only after plates pass: `templates/wan22-a14b-i2v-short-template/`.
- Final polish must use WAYS captions: large centered white captions, yellow active/key emphasis, thick black outline; no bottom text block.
- Do not publish/upload. Privacy remains private and Gate 6 remains human-only.

## 5) Concrete free source acquisition / generation plan

No paid/credit lanes.

1. **Real source search first**
   - Search Wikimedia Commons, Internet Archive/public-domain/open-license microscope footage, NASA/ESA/public institutional pages, university microscopy pages, and open-access paper supplements for tardigrade/tun/reactivation visuals.
   - Prefer microscope video/still sequences over single isolated hero images.
   - Record URL, license, author/source, and exact file used in a future `assets/source_stills/source_manifest.json`.

2. **Build a source shortlist**
   - Collect 8–12 candidate source images/clips for hydrated, tun/desiccated, water-return/reactivation, and hero beats.
   - Reject all sources with unavoidable logos/text/UI/watermarks.
   - Reject all sources whose license/provenance is unclear.

3. **Plate prep only after source shortlist passes**
   - Crop/grade real sources to 9:16 WAYS-safe plates.
   - Remove/crop scale bars and captions; do not invent anatomy.
   - Create a contact sheet of candidate plates for human Plate Gate review before any render.

4. **If source coverage is incomplete**
   - Use simple, truthful editing: cuts between real hydrated/tun/rehydrated plates are acceptable.
   - Do not use SDXL/AI-generated final creature plates.
   - Do not fabricate tun anatomy or reactivation if no credible plate exists; instead change/hold the beat until credible source is found.

## 6) Acceptance gates before any future render

A future attempt cannot render until all gates pass:

- [ ] **Gate A — source provenance:** every selected plate/clip has URL, license, author/source, local path, and beat assignment.
- [ ] **Gate B — say-dog-see-dog:** each of the five beats above has a matching credible visual plate/sequence.
- [ ] **Gate C — anatomy QC:** Josh/agent review confirms no AI anatomy/artifacts and tardigrade/tun are recognizable.
- [ ] **Gate D — text QC:** zero non-caption text in plates after crop/cleanup.
- [ ] **Gate E — WAYS lock:** `voice=elevenlabs_george`; approved WAYS template/caption lane only.
- [ ] **Gate F — no paid lanes:** source acquisition and generation use no paid/credit tools.
- [ ] **Gate G — human plate approval:** Josh approves the plate contact sheet before any Wan/static render.
- [ ] **Gate H — render hold:** do not create/send a new candidate until Gates A–G are checked.

## 7) Key next steps

1. Mark the current `final_polish_wan22_template_v01` candidate as rejected/hold in any production tracker.
2. Acquire real/free microscope tardigrade source material with provenance.
3. Build a new real-source plate contact sheet under `test_cases/tardigrade_survival_mode/assets/`.
4. Run Plate Gate only; get human approval before rendering.
5. Only after plate approval: render with `elevenlabs_george` and the approved WAYS/Wan template; then perform full WAYS QA before any publish consideration.
