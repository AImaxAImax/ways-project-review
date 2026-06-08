#!/usr/bin/env python3
from pathlib import Path
import subprocess, json, textwrap, time

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
SRC_DIR=CASE/'outputs/wan22_owl_head_turn_v04_all_moving'
OUT=CASE/'outputs/owl_draft_v04_all_moving'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO=Path('/home/<user>/.hermes/audio_cache/tts_20260608_083428.mp3')
DUR=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(AUDIO)],text=True).strip())
CLIPS=[
    SRC_DIR/'shot01_owl_all_moving_wan22_432x768_49f_seed944101.mp4',
    SRC_DIR/'shot02_owl_all_moving_wan22_432x768_49f_seed944102.mp4',
    SRC_DIR/'shot03_owl_all_moving_wan22_432x768_49f_seed944103.mp4',
    SRC_DIR/'shot04_owl_all_moving_wan22_432x768_49f_seed944104.mp4',
]
clean=OUT/'owl_head_turn_all_moving_clean_v04.mp4'
captioned=OUT/'owl_head_turn_captioned_draft_v04_all_moving.mp4'
preview=OUT/'owl_head_turn_discord_preview_v04_all_moving.mp4'
sheet=OUT/'contact_sheet_owl_draft_v04_all_moving.jpg'
ass=OUT/'captions_owl_v04_all_moving.ass'
qa=OUT/'QA_OWL_DRAFT_V04_ALL_MOVING.md'
manifest=OUT/'render_manifest_v04_all_moving.json'

# 4 x 2.04s I2V clips slowed to ~4.9s each. Every segment has source I2V motion.
cmd=['ffmpeg','-y']
for c in CLIPS:
    cmd += ['-i',str(c)]
filters=[]
labels=[]
for i in range(len(CLIPS)):
    filters.append(
        f'[{i}:v]fps=24,setpts=2.52*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,'
        f'scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v{i}]'
    )
    labels.append(f'[v{i}]')
filter_complex=';'.join(filters)+';'+''.join(labels)+f'concat=n={len(CLIPS)}:v=1:a=0,trim=duration={DUR:.3f},setpts=PTS-STARTPTS[outv]'
cmd += ['-filter_complex',filter_complex,'-map','[outv]','-an','-r','24',str(clean)]
subprocess.run(cmd,check=True)

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

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.20,WAYS,,0,0,0,,AN OWL CAN TURN\NITS HEAD ALMOST
Dialogue: 0,0:00:03.20,0:00:06.20,WAYS,,0,0,0,,THREE QUARTERS\NOF A CIRCLE
Dialogue: 0,0:00:06.20,0:00:08.80,WAYS,,0,0,0,,NOT 360°\NABOUT 270°
Dialogue: 0,0:00:08.80,0:00:12.20,WAYS,,0,0,0,,ITS EYES\NBARELY MOVE
Dialogue: 0,0:00:12.20,0:00:15.40,SMALL,,0,0,0,,SO THE NECK HAS TO AIM\NTHE WHOLE FACE
Dialogue: 0,0:00:15.40,0:00:18.25,SMALL,,0,0,0,,EXTRA NECK BONES +\NROOMY BLOOD VESSELS
Dialogue: 0,0:00:18.25,0:00:19.65,WAYS,,0,0,0,,IMPOSSIBLE?\NREAL.
''').strip()+"\n")
subprocess.run([
    'ffmpeg','-y','-i',str(clean),'-i',str(AUDIO),'-vf',f'ass={ass}',
    '-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','160k','-shortest',str(captioned)
],check=True)
subprocess.run([
    'ffmpeg','-y','-i',str(captioned),'-vf','scale=540:960:flags=lanczos',
    '-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac','-b:a','128k',str(preview)
],check=True)
subprocess.run(['ffmpeg','-y','-i',str(captioned),'-vf','fps=1,scale=270:480,tile=5x4','-frames:v','1',str(sheet)],check=True)
probe_master=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=width,height,codec_name,avg_frame_rate,bit_rate','-of','json',str(captioned)],text=True))
probe_preview=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=width,height,codec_name,avg_frame_rate,bit_rate','-of','json',str(preview)],text=True))
qa.write_text(textwrap.dedent(f'''
# QA — owl_head_turn draft v04 all-moving

## Purpose
Josh asked to make it more impressive and avoid the v03 still-plate feel. v04 uses I2V movement in every visual segment and longer 49-frame Wan2.2 clips instead of the earlier 25-frame clips.

## Outputs
- Captioned master: `{captioned.name}`
- Discord preview: `{preview.name}`
- Contact sheet: `{sheet.name}`
- Clean edit: `{clean.name}`

## Technical verification
- Master: {probe_master['streams'][0]['width']}x{probe_master['streams'][0]['height']}, H.264 + AAC, {float(probe_master['format']['duration']):.3f}s, {int(probe_master['format']['size'])/1_000_000:.2f} MB
- Preview: {probe_preview['streams'][0]['width']}x{probe_preview['streams'][0]['height']}, H.264 + AAC, {float(probe_preview['format']['duration']):.3f}s, {int(probe_preview['format']['size'])/1_000_000:.2f} MB

## Visual strategy
- Every shot is sourced from Wan2.2 I2V motion.
- Motion is low-amplitude: blinking, feather breathing, slow camera movement, and small head settles.
- Avoids large generated neck twists, the issue that killed v02.
- 49-frame source clips give more natural motion than 25-frame clips, then are slowed to fit the VO.

## Gate recommendation
Review draft. This should be more impressive than v03 and less neck-risky than v02. It still needs human phone-size review before publish approval.
''').strip()+"\n")
manifest.write_text(json.dumps({'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'strategy':'all segments I2V moving, 49-frame clips slowed to VO','clips':[str(c) for c in CLIPS],'audio':str(AUDIO),'outputs':{'clean':str(clean),'captioned':str(captioned),'preview':str(preview),'sheet':str(sheet),'qa':str(qa)},'ffprobe_captioned':probe_master,'ffprobe_preview':probe_preview},indent=2))
print(json.dumps({'ok':True,'preview':str(preview),'master':str(captioned),'qa':str(qa),'probe_preview':probe_preview},indent=2))
