# Motion Plan — Avoid Tacky/Bolted-On Still Animation

## Answer
Yes, the end product is a video. The safest path is not generic image wobble. The motion should be designed like a premium natural-history short, not a repeated museum slideshow: restrained camera movement, layered parallax, water/particle overlays, selective exhibit/proof motion only where the story calls for it, and only selective true image-to-video where it adds story.

## Motion rules
- No random AI wobble just to make stills move.
- No aggressive Ken Burns zooms on every shot.
- Movement should feel motivated: camera drift, water current, spotlight, particles, subtle paper-depth parallax.
- Keep motion slow enough for narration and mobile readability.
- Animate subjects only when it helps the beat; otherwise use elegant camera/atmosphere.

## Proposed pipeline
1. Finish/select stills first.
2. Split each selected still into 2.5D layers where possible:
   - foreground subject
   - midground water/slab/props
   - background geology/museum space
   - particles/light overlays
3. Build a restrained motion pass in edit/ffmpeg/After Effects style:
   - 2–4% slow push-in or drift
   - subtle parallax between layers
   - animated dust/water particles
   - gentle light shimmer / caustics for underwater shots
   - captions timed to narrator
4. Use local/paid I2V only for shots that need real subject motion:
   - shark glide / tail movement
   - transformation shots
   - final emotional shark pass
5. Reject I2V if it introduces morphing, identity drift, weird fins, text, or cheap wobble.

## Shot-specific motion direction
### Shot 1 — Sharks were here before trees
- Slow underwater push-in.
- Tiny drifting particles.
- Very subtle water-caustic shimmer.
- Slight parallax: shark foreground moves a touch faster than distant barren coast.
- Optional: minimal fin/tail movement only if I2V preserves the image.

### Shot 2 — Seriously
- Almost still, like a museum proof reveal.
- Slow spotlight sweep or soft camera push.
- Dust motes drifting.
- Avoid subject morphing; this can be a premium still-motion shot.

### Later literal prop/timeline shots
- Use physical-camera style moves: slide, push, rack-focus, spotlight reveal.
- Timeline can animate with editor-built graphic motion rather than AI video.
- Apple/squirrel/acorn gag can use small stage-camera move, not AI character animation unless it looks excellent.

## Quality gate
Before full production, make a 6–8 second motion test using Shot 1 + Shot 2:
- render with parallax/particles/caption timing
- compare against I2V version only if needed
- choose the less tacky lane

## Current recommendation
Use stills as premium keyframes, not as final static images. Start with an editor-controlled 2.5D/parallax motion test because it preserves art direction better than blind I2V. Add I2V selectively later only where subject motion is essential.