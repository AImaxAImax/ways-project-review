# Caption + CapCut final-polish lane

This lane starts after the local Wan base render passes the template gate. It turns a clean no-caption/low-polish master (for example shark v27) into a captioned publish candidate while preserving the clean master for future recuts.

## Non-negotiables

1. Never overwrite the Wan clean master. Import/copy it into a final-polish pack and render new captioned derivatives only.
2. Captions are part of the retention system, not decoration: large centered creator-style captions, white text, thick black outline/drop shadow, yellow emphasis on active/key words.
3. Do not double-caption. Source visuals must have no generated text, labels, lower thirds, UI, logos, or old subtitle burn-in.
4. Audio must be speech-forward and normalized before a publish gate.
5. A script-generated candidate is still HOLD until playback/contact-sheet QA passes.

## Pack layout

Each final-polish run writes a standalone directory:

```text
outputs/final_polish_<slug>/
  clean_master_unmodified.mp4       # copied source; never edited in place
  captions.ass                      # styled editable subtitles
  captions.srt                      # plain upload subtitle file
  publish_candidate_captioned.mp4   # 1080x1920 H.264/AAC upload candidate
  discord_preview_captioned.mp4     # 720x1280 preview
  contact_sheet_final_polish.jpg    # phone-size QA sheet
  ffprobe_clean_master.json
  ffprobe_publish_candidate.json
  ffprobe_discord_preview.json
  upload_metadata.json
  PUBLISH_GATE.md
```

## Automated local pass

Use the helper when the manifest already has shot durations and caption text:

```bash
python3 tools/final_polish_pack.py \
  --input test_cases/sharks_older_than_trees/outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_audio.mp4 \
  --manifest test_cases/sharks_older_than_trees/outputs/wan22_v27_animated_frames/manifest.json \
  --outdir test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned \
  --title sharks-older-than-trees-v27
```

What it does:

- copies the clean master into the pack,
- generates ASS + SRT from manifest shot timing,
- burns centered captions with yellow key-word emphasis,
- normalizes audio with highpass, light compression, and `loudnorm=I=-15:LRA=7:TP=-1`,
- creates master + Discord preview + contact sheet,
- writes ffprobe JSON and a publish-gate checklist.

This is the deterministic agent lane. It is good for turning a v27-style base into a reviewable captioned candidate without opening a GUI.

## CapCut/Whisper upgrade lane

Use this when true spoken active-word karaoke is required, or when the manifest captions differ from the final voiceover.

1. Import `clean_master_unmodified.mp4` into CapCut or run Whisper/faster-whisper on the voiceover.
2. Generate word-level captions. Verify transcript word count against the approved script; rerun with at least `base.en`/`small.en` if words are missing or hallucinated.
3. Style captions:
   - 1080x1920: 90-110 px equivalent, center safe area, no bottom block.
   - White inactive words, yellow current/key word, thick black outline/drop shadow.
   - 3-5 words per chunk, max 2 lines.
4. Export/round-trip `.srt` or `.ass` into the same final-polish pack. If CapCut can only export a burned MP4, also save the project file and keep the clean master in the pack for recaptioning.
5. Run the publish gate again against the CapCut export.

## Publish gate

A candidate may be uploaded only after all checks pass:

- Full playback at phone size: hook readable in first 2 seconds.
- Captions exactly match voiceover; no stale script text.
- Yellow emphasis is correct. If the brief asks for active-word karaoke, the highlighted word must be the spoken word at that timestamp.
- No source text/logos/UI/lower-thirds/double captions.
- Audio clear, normalized, not clipping; speech remains dominant over music/SFX.
- Contact sheet shows readable captions and visual reset/interest every 2-3 seconds.
- Final visual quality still clears the channel's 9/10 bar; if not, rerender only the weak shots from the clean Wan/template lane.
- Clean master remains present and unmodified in the pack.

## Shark v27 proof pack

The first proof run of this lane is:

`test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned/`

It proves the clean Wan v27-style base can be converted into a captioned publish candidate without destroying the clean master. The generated `PUBLISH_GATE.md` remains HOLD until phone-size human/agent playback review checks every box.
