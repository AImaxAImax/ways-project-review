# Strict WAYS rework packet — Saturn Hexagon Storm

Date: 2026-06-06
Slug: `saturn_hexagon_storm`
Status: **REWORK BLOCKED BEFORE RENDER**
Owner feedback: Josh rejected current candidate as **5/10 at best**.

## 0. Do-not-repeat decision

The existing Saturn candidates are **audit-only** and must not be sent as a new review/publish candidate:

- `outputs/auto_static_v01/publish_candidate_captioned.mp4`
- `outputs/wan22_template_v02_plain/saturn_hexagon_storm_wan22_master_1080.mp4`
- `outputs/final_polish_wan22_template_v02_plain/publish_candidate_captioned.mp4`

No publish/upload. No paid/credit lanes. Do not render again until the acceptance gates below pass.

## 1. Rejection summary

Josh's rejection reasons to treat as hard constraints:

1. **Score: 5/10 at best** — below WAYS review gate.
2. **Not say-dog-see-dog** — visuals did not literally show each spoken claim; they felt like decorative Saturn pictures.
3. **Source images bad** — source plates were not premium/proof-clear enough at phone size.
4. **AI/text artifacts** — any generated text, text-like marks, labels, logos, UI-looking shapes, or fake symbols are hard fails.
5. **Wrong voice/template** — rebuild must use `elevenlabs_george` and the approved WAYS template with no style/timing/caption drift.

## 2. Exact say-dog-see-dog beats required

Every beat needs a unique visual proof/action. If the viewer heard no audio and only watched the picture, they should still understand the claim.

| Shot | Voiceover | Caption | Required literal visual proof | Hard fail examples |
|---|---|---|---|---|
| 01 | `Saturn has a hexagon storm.` | `Saturn has a hexagon storm` | Immediate phone-size read of Saturn's north-pole hexagon. The six-sided outline/jet-stream shape must be visible in the first second, not implied. | Generic Saturn/rings beauty shot; hexagon too small/soft; AI storm blob. |
| 02 | `It is not a drawing. It is a real jet stream around the planet's north pole.` | `not a drawing / a real jet stream` | Real NASA/Cassini source plate of the north-pole hexagon; optional non-text wind-flow motion following the hexagon perimeter. Must feel like documentary proof, not illustration. | Diagram labels; fake UI; random clouds; pure generated art. |
| 03 | `Each side is wider than Earth.` | `each side is wider than Earth` | Clean scale proof without text: one hexagon side visually bracketed/highlighted and a tiny Earth proxy placed beside that side. Earth proxy must be an icon/image only, no lettering/numbers. | Text labels, rulers with numbers, unreadable scale, Earth larger/ambiguous, misleading measurement. |
| 04 | `And inside it, storms keep spinning.` | `storms keep spinning inside` | Close crop of inside the hexagon/polar vortex with visible vortex/storm-cell swirl motion. The motion must communicate spinning weather inside the boundary. | Static decorative crop; lightning/explosions; fake hurricanes not matching Saturn source; text artifacts. |
| 05 | `So one of the strangest shapes in space is weather.` | `a strange shape / made of weather` | Pullback or final composite showing the hexagon as cloud/weather on Saturn, not a solid object or drawn symbol. End on a clean, premium NASA-grounded hero frame. | Abstract polygon, sci-fi portal, drawn logo, or any source text. |

## 3. Source-plate requirements

Minimum plate standard before any render:

- **Zero non-caption text** in the plate itself: no labels, watermarks, logos, UI, NASA insignia, fake glyphs, pseudo-letters, numbers, chart text, or text-like AI debris.
- **NASA/Cassini-first**: primary proof plates should come from public NASA/JPL/Cassini imagery already identified in `research/source_generation_plan.md`.
- **Phone-size proof**: contact sheet must be readable at Discord/phone size. If the hexagon or vortex is not obvious when viewed small, the plate fails.
- **Premium but honest**: enhancement is allowed only for contrast/crop/slow movement; do not invent extra planets, spacecraft UI, impossible lighting, explosions, or land-like surfaces.
- **No double-caption risk**: source plates must be visually clean enough that WAYS captions are the only text-like element on screen.
- **Per-shot uniqueness**: no five-shot reuse of the same generic Saturn image; each shot must demonstrate its specific claim.

## 4. Approved voice/template requirements

Rebuild must match the approved WAYS shark/Wan template exactly:

- Voice: **`elevenlabs_george` only**.
- Category/privacy defaults remain WAYS: `category_id: 28`, `privacy: private` for any future draft metadata.
- Caption system: approved WAYS large centered captions; white text with yellow emphasis, thick black outline, no bottom subtitle block, no extra lower thirds.
- Timing: punchy WAYS short pacing with visual reset every 2-3 seconds; no slow documentary drift that makes claims feel unsupported.
- Template drift is a **hard fail** even if export specs/ffprobe pass.
- Before render, compare against the approved WAYS shark/Wan reference/template settings and record the template check result in the gate packet.

## 5. Concrete source acquisition / generation plan — no paid credits

1. **Acquire NASA originals only from free/public NASA URLs** listed in `research/source_generation_plan.md`:
   - PIA21052 — `Over Saturn's Turbulent North` for hexagon side/Earth-width and central storm proof.
   - PIA17122 — `Stormy North` for inside-hexagon storm/vortex detail.
   - PIA14646 — `Hexagon and Rings` only if it gives a strong opening/closing read.
   - PIA20507 — `Saturn Watercolor Swirls` as secondary texture/reference, not primary hexagon proof unless the hexagon reads clearly.
2. **Create a source manifest** beside downloaded files with NASA ID, title, URL, license/guideline note, downloaded filename, crop usage, and shot assignment.
3. **Build vertical proof plates locally** with crop/contrast/sharpen only. Allowed local tools: Python/PIL/OpenCV/ffmpeg. No paid stock, no paid generation, no credit-spend services.
4. **For scale beat only**, generate a local non-text Earth proxy and simple bracket/edge highlight if needed. It must be clean vector/shape art with no labels or numbers and must not look like a diagram with text.
5. **If NASA plates are not enough**, use only no-credit local generation/compositing grounded in NASA source plates, then submit still plates for Gate 2 before motion. Any AI-looking artifact, text-like mark, or over-stylized sci-fi look fails.
6. **Motion plan after plates pass**: use subtle local animation or approved no-credit Wan/I2V only on accepted plates: slow push, polar rotation, cloud drift, and clean pullback. No new source invention.

## 6. Acceptance gates before render

Do not render a new candidate until all gates pass and are written to `outputs/gate2_plate_qc/` or a successor gate folder.

### Gate A — Script/say-dog-see-dog lock
- [ ] The five beats in Section 2 are unchanged or explicitly reapproved.
- [ ] Each beat has a unique source plate/action mapped to the claim.
- [ ] No beat is covered by generic Saturn beauty footage alone.

### Gate B — Source acquisition proof
- [ ] Source manifest exists with NASA IDs/URLs and local filenames.
- [ ] All sources are free/public/no-credit.
- [ ] No NASA logo/insignia/mission patch is used as a visual element.

### Gate C — Plate QC before motion
- [ ] Contact sheet of still plates exists.
- [ ] Human/agent phone-size check confirms hexagon/jet stream/scale/vortex/weather reads instantly.
- [ ] OCR/text-artifact pass: zero labels, logos, pseudo-text, UI marks, watermarks, or generated glyphs.
- [ ] Source quality is premium enough for WAYS; no blurry/flat/bad-source plate advances.

### Gate D — Template/voice lock before assembly
- [ ] Voiceover generated/selected as `elevenlabs_george` only.
- [ ] WAYS approved shark/Wan template settings copied/verified; no drift in captions, timing, voice, or export ladder.
- [ ] Captions are the only text on screen.

### Gate E — Render permission
- [ ] Gates A-D pass in writing.
- [ ] No paid/credit lane is invoked.
- [ ] New render is explicitly marked as internal until human review; no upload/publish.

## 7. Next required deliverables

1. Download/verify NASA originals and write `assets/source_nasa/source_manifest.json`.
2. Produce five still proof plates and `outputs/gate2_plate_qc/contact_sheet.jpg`.
3. Write `outputs/gate2_plate_qc/PLATE_QC.md` with per-shot pass/fail against Section 2 and Section 3.
4. Only after those pass, rebuild with `elevenlabs_george` and the approved WAYS template.
