# v17 premium mechanism lane QA

## What was attempted
User chose option 2: premium 3D/illustrated mechanism sequence.

Image generation via Hermes/FAL was unavailable because `FAL_KEY` is not configured, so the premium lane was attempted through the local ComfyUI server at `127.0.0.1:8188`.

## Generated asset batches
- `assets/premium_mechanism_v17/`: rejected. It generated full fake mantis shrimp bodies with anatomy risk.
- `assets/premium_mechanism_v17b_noanimal/`: rejected. Prompts still produced fake shrimp/crustacean bodies.
- `assets/premium_mechanism_v17c_abstract/`: partially usable. No obvious text or fake animal anatomy in selected frames, but they are abstract water/VFX shots rather than literal mantis strike proof.

## v17 result
- Preview: `outputs/say_dog_v17_premium_abstract_mechanism/mantis_say_dog_v17_captioned_720.mp4`
- Master: `outputs/say_dog_v17_premium_abstract_mechanism/mantis_say_dog_v17_captioned_1080.mp4`
- Contact sheet: `outputs/say_dog_v17_premium_abstract_mechanism/contact_sheet_mantis_say_dog_v17.jpg`

## QA verdict
v17 improves over v14/v16 in visual polish for the mechanism beats. It avoids the previous obvious rings/cards/particle artifacts and avoids generated fake animal anatomy in the selected mechanism frames.

Still not a clean 8/10:
- Mechanism frames are premium-looking but abstract; they do not literally show mantis-shrimp club geometry or bubble collapse as a scientifically clear process.
- Style jump between real mantis footage/photos and abstract VFX frames is visible.
- Source repetition remains in the real animal beats.
- It is closer than v14/v16, but still around 7.3-7.6/10, not 8+.

## Next recommended path
A true 8+ premium mechanism lane likely needs a dedicated 3D render/illustration pass or a stronger image-generation provider/lane. Local Comfy SDXL/DreamShaper could not reliably generate accurate/no-animal mantis mechanism frames beyond abstract VFX.
