# v27 Wan2.2 animated pass QA

Updated: 2026-06-05

## Outputs verified

Master:

`outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_audio.mp4`

Discord preview:

`outputs/wan22_v27_animated_frames/sharks_older_than_trees_v27_wan22_animated_discord.mp4`

Contact sheet:

`outputs/wan22_v27_animated_frames/contact_sheet_v27_wan22.jpg`

## ffprobe

Master:

- 1080x1920 H.264 video
- AAC audio at 48 kHz
- duration `23.916s`
- size `17,515,645` bytes

Discord preview:

- 720x1280 H.264 video
- AAC audio at 48 kHz
- duration `23.936s`
- size `7,844,050` bytes

## Clip inventory

7 Wan2.2 clips landed:

- `shot01_wan22_432x768_25f_seed627101.mp4`
- `shot02_wan22_432x768_25f_seed627102.mp4`
- `shot03_wan22_432x768_25f_seed627103.mp4`
- `shot04_wan22_432x768_25f_seed627104.mp4`
- `shot05_wan22_432x768_25f_seed627105.mp4`
- `shot06_wan22_432x768_25f_seed627106.mp4`
- `shot07_wan22_432x768_25f_seed627107.mp4`

## Visual QA from contact sheet

- Shot 01 shark/ocean: coherent shark silhouette, real frame-to-frame drift/water motion. Some softness from 432x768 source, but no obvious catastrophic anatomy melt in sampled frames.
- Shot 02 fossil tooth: stable and readable. Low-motion but appropriate macro proof shot. No text/logos.
- Shot 03 apple/squirrel/nut: visually coherent. Minor source surrealism remains, but no gross morphing in sampled frames.
- Shot 04 deep-time/geology: strongest for educational timeline, layered composition stays readable. No generated text.
- Shot 05 first forest coast: coherent, some painterly/AI texture, but scene holds together.
- Shot 06 aquarium/kid: readable child silhouette and shark; sampled frames look stable.
- Shot 07 final predator: coherent shark head/body across sampled frames, actual I2V movement is subtle. No gore/text/monster drift.

## Gate

This is a successful real local Wan2.2 I2V assembly and proves Comfy is working again.

It is **not yet a final 9/10 publish cut** because:

- no native full-video captions are burned in; this should go through CapCut auto-captions or a proper caption pass,
- the motion clips are only 25 frames stretched to beat length, so some beats may feel slow/subtle,
- source resolution is 432x768 per I2V clip, upscaled to 1080x1920, so visual detail is softer than a final premium render.

Recommended next step: treat this as the real-motion base, then do a captioned CapCut/final-polish pass and selectively rerender only weak shots if full-speed review shows artifacts.
