#!/usr/bin/env python3
from pathlib import Path
import subprocess, json, textwrap, time

CASE=Path('/mnt/c/dev/curious-shorts/test_cases/owl_head_turn')
OUT=CASE/'outputs/owl_draft_v03_neck_safe'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO=Path('/home/joshn/.hermes/audio_cache/tts_20260608_083428.mp3')
DUR=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(AUDIO)],text=True).strip())

# v03 deliberately avoids generated neck twisting. Use clean still/source plates with camera movement.
PLATES=[
    CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/03_seedream_body_front_face_back_01.png',
    CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/01_ref_nano04_turn_01.png',
    CASE/'assets/pending_human_plate_review/higgsfield_v02/nano_clear_270_01.png',
    CASE/'assets/pending_human_plate_review/higgsfield_v02_top_picks/02_ref_seedream01_turn_01.png',
    CASE/'assets/pending_human_plate_review/higgsfield_v02/seedream_clear_270_01.png',
]
SEG_DURS=[3.9,3.9,3.9,3.9,4.0]
clean=OUT/'owl_head_turn_neck_safe_clean_v03.mp4'
captioned=OUT/'owl_head_turn_captioned_draft_v03_neck_safe.mp4'
preview=OUT/'owl_head_turn_discord_preview_v03_neck_safe.mp4'
sheet=OUT/'contact_sheet_owl_draft_v03_neck_safe.jpg'
ass=OUT/'captions_owl_v03_neck_safe.ass'
qa=OUT/'QA_OWL_DRAFT_V03_NECK_SAFE.md'
manifest=OUT/'render_manifest_v03_neck_safe.json'

cmd=['ffmpeg','-y']
for dur, plate in zip(SEG_DURS, PLATES):
    cmd += ['-loop','1','-t',str(dur),'-i',str(plate)]

filters=[]
labels=[]
for i,dur in enumerate(SEG_DURS):
    frames=int(round(dur*24))
    # cover-crop to 9:16, then very slight Ken Burns. No generated anatomy motion.
    zoom_expr=f"min(1.045,1+0.00045*on)" if i%2==0 else f"max(1.0,1.045-0.00045*on)"
    filters.append(
        f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=24,"
        f"trim=duration={dur},setpts=PTS-STARTPTS,format=yuv420p[v{i}]"
    )
    labels.append(f'[v{i}]')
filter_complex=';'.join(filters)+';'+''.join(labels)+f'concat=n={len(SEG_DURS)}:v=1:a=0,trim=duration={DUR:.3f},setpts=PTS-STARTPTS[outv]'
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
# QA — owl_head_turn draft v03 neck-safe

## Purpose
Josh flagged v02 for neck artifacting. v03 intentionally removes generated neck-twist motion and uses clean still/source plates with subtle camera movement.

## Outputs
- Captioned master: `{captioned.name}`
- Discord preview: `{preview.name}`
- Contact sheet: `{sheet.name}`
- Clean edit: `{clean.name}`

## Technical verification
- Master: {probe_master['streams'][0]['width']}x{probe_master['streams'][0]['height']}, H.264 + AAC, {float(probe_master['format']['duration']):.3f}s, {int(probe_master['format']['size'])/1_000_000:.2f} MB
- Preview: {probe_preview['streams'][0]['width']}x{probe_preview['streams'][0]['height']}, H.264 + AAC, {float(probe_preview['format']['duration']):.3f}s, {int(probe_preview['format']['size'])/1_000_000:.2f} MB

## Visual strategy
- No AI-generated neck rotation in final edit, so the v02 neck artifact class is avoided.
- Uses multiple clean owl plates showing over-shoulder/head-turn poses.
- Tradeoff: cleaner anatomy, but less impressive motion. This is safer for review, not a final publish-level motion solution.

## Gate recommendation
Internal review pass for artifact mitigation. For publish, render or source one longer clean wildlife-style head-turn shot before upload.
''').strip()+"\n")
manifest.write_text(json.dumps({'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'strategy':'neck-safe still-plate edit, no generated neck rotation','plates':[str(p) for p in PLATES],'audio':str(AUDIO),'outputs':{'clean':str(clean),'captioned':str(captioned),'preview':str(preview),'sheet':str(sheet),'qa':str(qa)},'ffprobe_captioned':probe_master,'ffprobe_preview':probe_preview},indent=2))
print(json.dumps({'ok':True,'preview':str(preview),'master':str(captioned),'qa':str(qa),'probe_preview':probe_preview},indent=2))
