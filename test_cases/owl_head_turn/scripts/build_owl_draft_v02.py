#!/usr/bin/env python3
from pathlib import Path
import subprocess, json, textwrap, time

CASE = Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
OUT = CASE/'outputs/owl_draft_v02'
OUT.mkdir(parents=True, exist_ok=True)
SHOT01 = CASE/'outputs/wan22_owl_head_turn_v01/shot01_owl_head_turn_wan22_432x768_25f_seed812701.mp4'
SHOT02 = CASE/'outputs/wan22_owl_head_turn_v01/shot02_owl_head_turn_wan22_432x768_25f_seed812702.mp4'
PLATE = CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/01_ref_nano04_turn_01.png'
AUDIO = Path('/home/<user>/.hermes/audio_cache/tts_20260608_083428.mp3')
DUR = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(AUDIO)], text=True).strip())

clean = OUT/'owl_head_turn_clean_sequence_v02.mp4'
captioned = OUT/'owl_head_turn_captioned_draft_v02.mp4'
preview = OUT/'owl_head_turn_discord_preview_v02.mp4'
sheet = OUT/'contact_sheet_owl_draft_v02.jpg'
ass = OUT/'captions_owl_v02.ass'
manifest_path = OUT/'render_manifest_v02.json'
qa = OUT/'QA_OWL_DRAFT_V02.md'

# Build a less-looped sequence from both generated motion candidates, plus a slow plate hold.
# Each 1.04s I2V clip is slowed to about 4.17s and interpolated back to 24fps.
# Timeline: side->front, side micro-turn, plate hold, reverse micro-turn, reverse side->front.
filter_complex = r'''
[0:v]fps=24,setpts=4*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v0];
[1:v]fps=24,setpts=4*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v1];
[2:v]scale=1080:1920:flags=lanczos,setsar=1,zoompan=z='min(1.06,1+0.0009*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=100:s=1080x1920:fps=24,trim=duration=4.16,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[v2];
[1:v]reverse,fps=24,setpts=4*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v3];
[0:v]reverse,fps=24,setpts=4*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v4];
[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0,trim=duration=%0.3f,setpts=PTS-STARTPTS[outv]
''' % DUR

subprocess.run([
    'ffmpeg','-y',
    '-i',str(SHOT01),'-i',str(SHOT02),'-loop','1','-t','4.2','-i',str(PLATE),
    '-filter_complex',filter_complex,
    '-map','[outv]','-an','-r','24',str(clean)
], check=True)

ass.write_text(textwrap.dedent(r'''
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: WAYS,Arial,86,&H00FFFFFF,&H000000FF,&H00000000,&HAA000000,-1,0,0,0,100,100,0,0,1,8,3,2,70,70,210,1
Style: SMALL,Arial,64,&H00FFFFFF,&H000000FF,&H00000000,&HAA000000,-1,0,0,0,100,100,0,0,1,7,2,2,70,70,210,1
Style: TOP,Arial,74,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,7,2,8,70,70,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.20,WAYS,,0,0,0,,AN OWL CAN WHIP\NITS HEAD ALMOST
Dialogue: 0,0:00:03.20,0:00:06.20,WAYS,,0,0,0,,THREE QUARTERS\NOF A CIRCLE
Dialogue: 0,0:00:06.20,0:00:08.80,WAYS,,0,0,0,,NOT 360°\NABOUT 270°
Dialogue: 0,0:00:08.80,0:00:12.20,WAYS,,0,0,0,,ITS EYES\NBARELY MOVE
Dialogue: 0,0:00:12.20,0:00:15.40,SMALL,,0,0,0,,SO THE NECK HAS TO AIM\NTHE WHOLE FACE
Dialogue: 0,0:00:15.40,0:00:18.25,SMALL,,0,0,0,,EXTRA NECK BONES +\NROOMY BLOOD VESSELS
Dialogue: 0,0:00:18.25,0:00:19.65,WAYS,,0,0,0,,IMPOSSIBLE?\NREAL.
''').strip()+"\n")

subprocess.run([
    'ffmpeg','-y','-i',str(clean),'-i',str(AUDIO),
    '-vf',f'ass={ass}',
    '-map','0:v:0','-map','1:a:0',
    '-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','160k','-shortest',str(captioned)
], check=True)

subprocess.run([
    'ffmpeg','-y','-i',str(captioned),'-vf','scale=540:960:flags=lanczos',
    '-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac','-b:a','128k',str(preview)
], check=True)

subprocess.run(['ffmpeg','-y','-i',str(captioned),'-vf','fps=1,scale=270:480,tile=5x4','-frames:v','1',str(sheet)], check=True)

probe_master=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=width,height,codec_name,avg_frame_rate,bit_rate','-of','json',str(captioned)], text=True))
probe_preview=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=width,height,codec_name,avg_frame_rate,bit_rate','-of','json',str(preview)], text=True))
manifest = {
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'sources': {'shot01': str(SHOT01), 'shot02': str(SHOT02), 'plate': str(PLATE), 'audio': str(AUDIO)},
    'duration': DUR,
    'outputs': {'clean': str(clean), 'captioned': str(captioned), 'preview': str(preview), 'contact_sheet': str(sheet), 'captions': str(ass), 'qa': str(qa)},
    'ffprobe_captioned': probe_master,
    'ffprobe_preview': probe_preview,
    'edit_note': 'v02 reduces obvious one-second looping by sequencing both I2V candidates, slow/interpolated motion, a plate hold, and reverse passes.'
}
manifest_path.write_text(json.dumps(manifest, indent=2))
qa.write_text(textwrap.dedent(f'''
# QA — owl_head_turn draft v02

## Outputs
- Captioned master: `{captioned.name}`
- Discord preview: `{preview.name}`
- Contact sheet: `{sheet.name}`
- Clean sequence: `{clean.name}`

## Technical verification
- Master: {probe_master['streams'][0]['width']}x{probe_master['streams'][0]['height']}, H.264 + AAC, {float(probe_master['format']['duration']):.3f}s, {int(probe_master['format']['size'])/1_000_000:.2f} MB
- Preview: {probe_preview['streams'][0]['width']}x{probe_preview['streams'][0]['height']}, H.264 + AAC, {float(probe_preview['format']['duration']):.3f}s, {int(probe_preview['format']['size'])/1_000_000:.2f} MB

## Edit changes from v01
- Uses both Wan2.2 I2V head-turn candidates instead of one single repeated loop.
- Adds a slow plate hold during the anatomy/blood-vessel explanation.
- Uses slower/interpolated motion and reverse passes to reduce obvious one-second cycling.
- Re-recorded VO is more natural and closer to the 20s WAYS educational beat.

## Gate recommendation
Still a review draft, not publish-approved. v02 should feel less repetitive than v01, but source motion is still limited by the original 25-frame I2V clips. Publish-level next pass should render a longer true head-turn clip or use an approved higher-end video lane.
''').strip()+"\n")
print(json.dumps(manifest, indent=2))
