# Wood frog freeze survival — feed-hook variants v05 QA

Date: 2026-06-07

## Why this pass exists

After the mantis upload, the next safest active WAYS packet is `wood_frog_freeze_survival` because it already has public-source real frog stills and deterministic/no-credit proof plates. I applied the shark/mantis analytics lesson immediately: optimize the first 0.5-1.5s as its own product before building the full render.

## Current source baseline

Existing Gate 2 v04 source pack:

- 4 public-source real wood frog stills.
- 3 deterministic no-AI proof/composite plates:
  - freeze-through-body proof
  - heart-stop/pulse proof
  - cell-protection proof
- No paid credits used.
- No AI animal bodies generated.

Baseline blocker: v04 was useful but not render-ready because the opening package was not yet deliberately designed and beat 3's heart/pulse motif risked feeling like medical UI.

## v05 first-second hook variants

Contact sheet:
`wood_frog_feed_hook_variants_v05_contact_sheet.jpg`

Manifest:
`feed_hook_variants_manifest_v05.json`

### Variant A — direct_fact_freeze_solid

File:
`wood_frog_hook_direct_fact_freeze_solid.jpg`

Score: **7.2/10**

Pros:
- Best instant sound-off read: real frog, cold/frozen treatment, weird enough for feed.
- Strongest pairing with first caption: `A FROG CAN FREEZE SOLID`.
- No text/logos/UI.
- Uses real frog source as base.

Cons:
- The translucent blue body mask is visibly graphic/composite.
- Frost lines are stylized, not documentary proof.
- Needs motion and caption to become fully clear.

Decision: **best opener seed**.

### Variant B — contradiction_freeze_then_thaw_split

File:
`wood_frog_hook_contradiction_freeze_then_thaw_split.jpg`

Score: **6.6/10**

Pros:
- Communicates freeze/thaw contrast better than one still.
- Useful for a second visual reset or beat 5 thaw callback.

Cons:
- Split-screen reads less cinematic and more template-like.
- At phone size the left/right contrast is not instantly obvious without caption.
- Feels like a later proof/comparison beat, not the strongest first frame.

Decision: useful secondary beat, not opener.

### Variant C — visual_proof_heart_pause

File:
`wood_frog_hook_visual_proof_heart_pause.jpg`

Score: **6.0/10**

Pros:
- Avoids the old explicit heart icon/pause bars.
- Could support the `heart can stop` beat after narration establishes context.

Cons:
- Too subtle for the feed hook.
- Circular pulse motif still risks a light medical/UI feel.
- Does not instantly communicate `frog can freeze solid`.

Decision: keep internal for beat 3 only, not opener.

## Shorts Feed Hook Gate, current best opener

Using Variant A:

- [x] First frame communicates the weird fact without needing prior context.
- [x] First caption can contain the contradiction/payoff: `A FROG CAN FREEZE SOLID`.
- [x] No slow establishing shot before the core fact.
- [x] Phone-size frog read is acceptable.
- [x] No non-caption text.
- [ ] Needs a visual reset by second 2-3 in the final render.
- [ ] Needs VO in approved `elevenlabs_george` lane before final assembly.

## Recommendation

Proceed with **wood frog** as the next packet, seeded from Variant A. Build the next internal candidate as:

1. Frame 1 / first second: Variant A + caption `A FROG CAN FREEZE SOLID`.
2. Reset by second 2-3: real frog source or split freeze/thaw variant.
3. Middle: use deterministic proof plates only where the claim needs them.
4. Avoid the old obvious heart icon/pause bars. If heart-stop stays, use the subtler pulse-freeze motif and let the caption carry the claim.
5. Do not publish or call final until contact-sheet/video QA clears the source/composite risk.
