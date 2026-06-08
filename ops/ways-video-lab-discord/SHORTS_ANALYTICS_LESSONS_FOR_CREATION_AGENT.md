# Shorts Analytics Lessons for the Video Creation Agent

## Context

This note comes from the first published/observed performance pattern for the WAYS shark Short:

- Video: **Sharks Are Older Than Trees #Shorts**
- YouTube video ID: `KLwp-KbIr9I`
- Runtime verified locally: **24.0 seconds**
- Initial observed YouTube Studio analytics screenshot:
  - **Average view duration:** `0:23`
  - **Stayed to watch:** `48.3%`
  - **Swiped away:** `51.7%`
- Updated YouTube Studio analytics observed 2026-06-06:
  - **Views:** `1.3K` (`1,294` realtime last 48 hours)
  - **Average view duration:** `0:25` on a `0:25` Short
  - **Stayed to watch:** `46.7%`
  - **Top traffic sources:** Shorts feed `96.8%`, YouTube search `1.9%`, Other YouTube features `1.0%`, Channel pages `0.3%`, External `0.1%`
  - YouTube Studio note: “Nice work! This video has a part that kept your viewers watching for longer than usual.”

## Key interpretation

The video did **not** fail because people got bored halfway through.

A 23-second average view duration on a 24-second Short means the viewers who accepted the video were watching almost the whole thing. The cliff happened because too many people rejected the video at the initial Shorts-feed decision point.

In plain terms:

```text
Core idea / body retention: promising
Opening frame / first-second hook: not strong enough
```

YouTube likely gave the Short an initial test pool, saw that slightly more viewers swiped away than stayed, and stopped expanding distribution.

## New production rule

For WAYS Shorts, optimize the first **0.5 to 1.5 seconds** as its own product.

Before polishing the full video, the creation agent must answer:

1. Would a stranger understand the contradiction instantly with sound off?
2. Is the first frame visually weird, specific, and curiosity-inducing?
3. Does the first caption state the impossible-sounding fact immediately?
4. Is there any slow scene-setting before the payoff? If yes, remove it.

## Target analytics threshold

Use these as practical targets for future Shorts:

| Metric | Minimum acceptable | Strong target |
|---|---:|---:|
| Stayed to watch | 50%+ | 60%+ |
| Swiped away | Below 50% | Below 40% |
| Average view duration | 80%+ of runtime | 90%+ of runtime |
| First 3 seconds | No sharp drop | Strong hold after hook |

For a 24-second Short, an average view duration around 23 seconds is excellent. If distribution still dies, prioritize the opening package, not the middle/end.

## Opening package requirements

Every future WAYS video should ship with a deliberate opening package:

### 1. First frame

Must show the weird fact immediately.

Bad opening pattern:

```text
Pretty scene -> context -> fact reveal
```

Better opening pattern:

```text
Contradiction/proof image -> fact stated instantly -> explanation
```

For the shark example, stronger first-frame concepts would be:

- shark beside a giant timeline marker: **“Before Trees”**
- shark silhouette crossing ancient ocean with a missing/ghosted forest label
- split image: **SHARKS: 400M+ years ago** vs **TREES: later**
- fossil/prehistoric ocean visual with a bold “NO FORESTS YET” cue

### 2. First spoken line / caption

Lead with the contradiction. Avoid warm-up phrasing.

Good hook lines:

- “Sharks are older than trees.”
- “This animal existed before forests.”
- “Before trees existed, sharks were already swimming.”
- “Sharks were here before the first forest.”

Weaker hook lines:

- “Did you know sharks have been around for a long time?”
- “Let’s talk about one of the oldest animals.”
- “The ocean has some ancient creatures.”

### 3. Captions

The first caption should be large, readable, and centered enough for Shorts-feed viewing.

Recommended first-caption structure:

```text
SHARKS ARE
OLDER THAN TREES
```

or

```text
THIS ANIMAL
PREDATES FORESTS
```

Do not bury the core fact in smaller subtitles or lower-third text.

### 4. Visual reset timing

Even when the opening is strong, keep resets every 2-3 seconds:

- cut
- punch-in
- new proof visual
- timeline marker
- object comparison
- caption emphasis
- sound effect or music accent

But if analytics show high AVD and low stayed-to-watch, do **not** overdiagnose the middle. Fix the opening first.

## Decision tree after publishing

### Case A: Low stayed-to-watch, high AVD among viewers

Example: shark video pattern.

```text
Stayed to watch around 48%
Average view duration almost full runtime
```

Diagnosis:

```text
Opening/feed decision problem
```

Action:

- Make a new variant with a stronger first frame and first caption.
- Keep the core idea and much of the body structure.
- Do not assume the topic is dead.

### Case B: High stayed-to-watch, low retention after 3-8 seconds

Diagnosis:

```text
Hook works, body pacing/clarity fails
```

Action:

- Tighten script.
- Add more visual resets.
- Remove vague explainer filler.
- Make every narration beat literal: say dog, see dog.

### Case C: High retention, low engagement, low distribution

Diagnosis:

```text
Potential audience/channel learning issue or weak engagement signal
```

Action:

- Publish more in the same content lane.
- Improve comment bait naturally with a question or surprising closing line.
- Keep topics clustered so YouTube can learn the audience.

### Case D: Low stayed-to-watch and low AVD

Diagnosis:

```text
Concept, packaging, and/or production are weak
```

Action:

- Rework from script and storyboard, not just visuals.
- Do not publish similar variants until the hook is rebuilt.

## Implementation checklist for the creation agent

Before declaring a Short ready for upload, include this section in the publish gate:

```markdown
## Shorts Feed Hook Gate

- [ ] First frame communicates the weird fact without needing prior context.
- [ ] First caption contains the contradiction/payoff, not a vague teaser.
- [ ] First spoken line lands within the first second.
- [ ] No slow establishing shot before the core fact.
- [ ] Visual/caption is readable on a phone at Shorts size.
- [ ] There is a visual reset by second 2-3.
- [ ] If this is a variant of a prior video, the opening package is materially different.
```

## Practical instruction for future WAYS videos

Treat the first second as the thumbnail, title, and trailer combined.

For each video, generate at least **3 first-second hook variants** before final render:

1. **Direct fact variant**
2. **Contradiction/timeline variant**
3. **Visual proof/comparison variant**

Pick the variant that is most instantly understandable with sound off.

## Shark video specific next step

Do not discard the shark topic. The near-full average view duration suggests the concept can work.

Recommended next version:

```text
0:00 - 0:01
Huge caption: SHARKS ARE OLDER THAN TREES
Visual: shark crossing ancient ocean/timeline, with “NO FORESTS YET” or tree marker appearing later.

0:01 - 0:03
Spoken: “Sharks were swimming before forests existed.”
Visual: timeline snaps from 400M+ years ago to first trees later.

0:03 onward
Proceed into the explanation with fast proof visuals and no repeated generic ocean beauty shots.
```

The main measurable goal for the remake is:

```text
Raise stayed-to-watch from 48.3% to 60%+
while preserving average view duration near full runtime.
```
