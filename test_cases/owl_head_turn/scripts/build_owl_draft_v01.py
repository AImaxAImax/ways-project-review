#!/usr/bin/env python3
from pathlib import Path
import subprocess, json, textwrap, time
CASE=Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
OUT=CASE/'outputs/owl_draft_v01'
OUT.mkdir(parents=True, exist_ok=True)
SRC=CASE/'outputs/wan22_owl_head_turn_v01/shot02_owl_head_turn_wan22_432x768_25f_seed812702.mp4'
AUDIO=Path('/home/<user>/.hermes/audio_cache/tts_20260607_143729.mp3')
DUR=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(AUDIO)],text=True).strip())
clean=OUT/'owl_head_turn_clean_loop_1080x1920.mp4'
captioned=OUT/'owl_head_turn_captioned_draft_v01.mp4'
preview=OUT/'owl_head_turn_discord_preview_v01.mp4'
sheet=OUT/'contact_sheet_owl_draft_v01.jpg'
ass=OUT/'captions_owl_v01.ass'
# Build a looped clean master from the 1.04s I2V clip. Scale to 1080x1920.
subprocess.run([
 'ffmpeg','-y','-stream_loop','30','-i',str(SRC),'-t',f'{DUR:.3f}',
 '-vf','scale=1080:1920:flags=lanczos,format=yuv420p','-an','-r','24',str(clean)
],check=True)
ass.write_text(textwrap.dedent(r'''
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: WAYS,Arial,92,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,8,3,2,70,70,210,1
Style: SMALL,Arial,70,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,7,2,2,70,70,210,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.70,WAYS,,0,0,0,,OWLS CAN TURN\NTHEIR HEADS WAY AROUND
Dialogue: 0,0:00:02.70,0:00:05.05,WAYS,,0,0,0,,NOT 360°\NABOUT 270°
Dialogue: 0,0:00:05.05,0:00:07.75,WAYS,,0,0,0,,THEIR EYES\NBARELY MOVE
Dialogue: 0,0:00:07.75,0:00:10.10,WAYS,,0,0,0,,SO THE NECK\NDOES THE WORK
Dialogue: 0,0:00:10.10,0:00:13.15,SMALL,,0,0,0,,SPECIAL NECK VESSELS\NKEEP BLOOD FLOWING
Dialogue: 0,0:00:13.15,0:00:15.40,WAYS,,0,0,0,,LOOKS IMPOSSIBLE\NBUT IT'S REAL
''').strip()+"\n")
# Caption + audio master
subprocess.run([
 'ffmpeg','-y','-i',str(clean),'-i',str(AUDIO),
 '-vf',f"ass={ass}",'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','160k','-shortest',str(captioned)
],check=True)
# Discord preview smaller
subprocess.run([
 'ffmpeg','-y','-i',str(captioned),'-vf','scale=540:960:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac','-b:a','128k',str(preview)
],check=True)
subprocess.run(['ffmpeg','-y','-i',str(captioned),'-vf','fps=1,scale=270:480,tile=4x4','-frames:v','1',str(sheet)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=width,height,codec_name,avg_frame_rate','-of','json',str(captioned)],text=True))
manifest={'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source_i2v':str(SRC),'audio':str(AUDIO),'duration':DUR,'outputs':{'clean':str(clean),'captioned':str(captioned),'preview':str(preview),'contact_sheet':str(sheet),'captions':str(ass)},'ffprobe_captioned':probe}
(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
