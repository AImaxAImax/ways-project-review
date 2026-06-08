# v21 caption-clear readable mechanism QA

## What changed

- Started from v20, which made the project-owned club/bubble/target mechanism larger.
- Moved only the three mechanism captions higher on screen so the orange club, vapor bubble, target, and collapse core are not hidden by text at phone/contact-sheet size.
- Kept the v19/v20 premium no-text VFX base and no AI-generated animal bodies.

## Verification

- Preview: `mantis_say_dog_v21_captioned_720.mp4`
- Master: `mantis_say_dog_v21_captioned_1080.mp4`
- Contact sheet: `contact_sheet_mantis_say_dog_v21.jpg`
- ffmpeg decode check passed.
- ffprobe preview: 720x1280 H.264 video + AAC audio, 31.33s, ~8.8 MB.

## Harsh QA

Score: ~7.8/10 direction candidate, maybe borderline Josh-review 8 if the user values the clearer proof lane.

Improves over v19/v20:
- Mechanism beats are easier to read at phone/contact-sheet size because the captions no longer cover the action.
- The cavitation beat now visibly shows the orange club moving toward a vapor bubble/target instead of only generic splash.
- The first-hit beat has more visible club/target relationship.
- No non-caption text, labels, arrows, UI, or generated fake animal bodies.

Still not a clean publish pass:
- The club/target remains a stylized fallback, not true high-speed proof footage.
- The collapse beat still reads somewhat abstract, though clearer than v19.
- Real mantis source repetition remains in hook/final/context beats.
- Caption placement changes on mechanism beats are acceptable, but slightly less uniform than the rest of the cut.

Recommendation: v21 is the best current local candidate to show as the premium mechanism direction. The next real jump requires either licensed/right-safe high-speed footage or a dedicated modeled 3D sequence with a clearer club/bubble/collapse arc.
