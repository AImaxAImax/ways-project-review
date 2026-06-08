# Octopus Three Hearts — Source Acquisition Status

Date: 2026-06-06  
Lane: source acquisition only (no render, no paid/credit sources)

## Status

Started the strict WAYS rebuild source-acquisition lane and created a rights-safe candidate manifest. The current rejected `wan22_template_v01` / `final_polish_wan22_template_v01` artifacts remain failed internal artifacts; no rendering or upload action was performed.

## Files created

- `assets/source_rework/source_manifest.json`
- Downloaded candidate stills in `assets/source_rework/`:
  - `octo_baseline_inat_cc0.jpg` — 2048x1365, CC0, iNaturalist Open Data
  - `octo_baseline_inat_cc0_2.jpg` — 2048x1536, CC0, iNaturalist Open Data
  - `octo_vulgaris_dimsis_ccby.jpg` — 1024x768, CC BY reported by Openverse/Flickr
  - `octo_swim_jurvetson_ccby.jpg` — 1024x846, CC BY reported by Openverse/Flickr
  - `octo_crawl_montereydiver_ccby.jpg` — 1023x682, CC BY reported by Openverse/Flickr

## Beat coverage candidates

| Beat | Candidate IDs | Notes |
|---|---|---|
| 1 — three hearts external baseline | `octo_baseline_inat_cc0`, `octo_baseline_inat_cc0_2`, `octo_vulgaris_dimsis_ccby`, `octo_baseline_ifremer_ccby_url_only` | Real external octopus stills for non-diagrammatic three-pulse overlay. |
| 2 — two gill hearts | `octo_baseline_inat_cc0`, `octo_baseline_inat_cc0_2`, `octo_vulgaris_dimsis_ccby`, `octo_baseline_ifremer_ccby_url_only` | Same/matched real plate candidates for exactly two side/gill-area pulse overlays. |
| 3 — one systemic heart | `octo_baseline_inat_cc0`, `octo_baseline_inat_cc0_2`, `octo_baseline_ifremer_ccby_url_only` | Real external plate candidates for one central/body pulse plus body-wide abstract flow. |
| 4 — swimming/systemic slows | `octo_swim_jurvetson_ccby` | Candidate found via Openverse query for octopus swimming/reef; needs visual QC before selection. |
| 5 — crawling easier | `octo_crawl_montereydiver_ccby` | Explicit walking/crawling octopus candidate from Flickr/Openverse; needs visual QC before selection. |

## Rights decisions

- Used only free/right-safe candidate lanes: CC0 and CC BY.
- Avoided all-rights-reserved, unclear-license, noncommercial/NC, paid stock/previews, and credit/spend sources.
- Avoided CC BY-SA for this pass to keep the lane conservative against the packet requirement wording.
- No AI anatomy or generated source imagery was used.
- No anatomy/circulatory diagram was accepted; available diagram/anatomy search results were label/text-heavy or not suitable. Recommended approach remains real octopus plates with abstract pulse/flow overlays only.

## Strict anatomy/proof-source search update

Decision time: 2026-06-06T10:06:01Z

I re-checked free/right-safe anatomy/proof lanes specifically for a text-free octopus heart/circulatory source. No candidate passed the hard gate.

Searches performed:

- Wikimedia Commons API queries: `octopus anatomy heart diagram`, `octopus circulatory system`, `octopus hearts diagram`, `cephalopod circulatory system octopus`, `octopus dissected heart`, `octopus anatomy`, `octopus internal anatomy`, `Octopus vulgaris anatomy`, `octopus diagram`.
- Openverse API queries: `octopus anatomy heart`, `octopus circulatory system`, `octopus three hearts`, `octopus heart anatomy`, `cephalopod anatomy heart`.

Notable rejected examples:

- `Main features of the anatomy of Octopus vulgaris in relation to the pallial nerve` — Wikimedia Commons, CC BY 4.0; rejected because it is a labeled/text anatomy figure and not a clean three-heart proof plate.
- `Ornate octopus anatomy vintage poster` / `Sea octopus anatomy vintage poster` — Wikimedia Commons/Rawpixel, CC BY 2.0; rejected because they are poster/anatomy-art sources with visible typography/labels.
- `Octopus sucker operation EN.svg` — Wikimedia Commons, CC BY-SA 4.0; rejected because it is a labeled/text diagram, not heart anatomy, and share-alike is avoided in this pass.
- Openverse `circulatory system: dissections aortic arch` — CC0; rejected because it is not octopus heart anatomy/proof.

Safe overlay alternative for the three-hearts claim:

- Use a rights-safe real octopus still from `assets/source_rework/` only after plate/contact-sheet QC passes.
- Add agent-created simple abstract pulse dots/rings after QC. These are claim markers, not literal/fake organ drawings.
- Beat 1: exactly three small soft pulse dots/rings on the visible mantle/body area; no labels or cutaway.
- Beat 2: exactly two synchronized side/gill-area pulse dots/rings with optional subtle flow glow toward the gill region; no third marker.
- Beat 3: exactly one central/body pulse dot/ring followed by a subtle body-wide glow/flow through mantle/arms; no labels.
- Do not use a fake labeled anatomy diagram, visible text, AI anatomy, or invented internal heart placement presented as literal biology.

The manifest `assets/source_rework/source_manifest.json` now records this rejection/search log and overlay plan under `anatomy_reference_status`.

## Issues / blockers

- Wikimedia Commons API/direct media began returning HTTP 429 during acquisition. The Ifremer/Wikimedia CC BY 4.0 octopus candidate is therefore included as a URL-only manifest entry (`octo_baseline_ifremer_ccby_url_only`) and was not downloaded in this pass.
- Flickr/Openverse CC BY candidates must have license/attribution rechecked on the landing pages before final render approval.
- All downloaded candidates still require the next gate: contact sheet + visual QC for no text/watermarks/logos, premium documentary quality, vertical crop safety, and no anatomy/tentacle artifacts.

## Render gate

Not passed yet. Source candidates are acquired, but none are marked accepted for render in the manifest. Next step is contact-sheet review and human/agent preflight before any WAYS rebuild render.
