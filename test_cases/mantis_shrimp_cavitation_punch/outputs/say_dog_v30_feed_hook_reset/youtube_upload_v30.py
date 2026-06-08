#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, time, shutil, datetime as dt, re, subprocess
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

TOKEN=Path.home()/'.hermes/youtube_token.json'
SCOPES=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.force-ssl']
ROOT=Path('/mnt/c/dev/curious-shorts/test_cases/mantis_shrimp_cavitation_punch')
OUT=ROOT/'outputs/say_dog_v30_feed_hook_reset'
PACK=OUT/'youtube_draft_pack_v30_20260606'
VIDEO=OUT/'mantis_say_dog_v30_feed_hook_reset_captioned_1080.mp4'
CONTACT=OUT/'contact_sheet_mantis_say_dog_v30_feed_hook_reset.jpg'
BEATMAP=OUT/'beat_map_v30.json'
SRT=PACK/'captions_v30.srt'
META=PACK/'youtube_metadata.json'
UPLOAD=PACK/'youtube_upload_result.json'
VERIFY=PACK/'youtube_verification.json'
PUBLIC_EVENT=PACK/'youtube_public_publish_event.json'
TITLE='This Shrimp Punch Makes Water Flash #Shorts'
TAGS=['Wait Are You Serious','WAYS','science','facts','Shorts','mantis shrimp','cavitation','marine biology','weird facts','animal facts']
DESCRIPTION='''A mantis shrimp punches so fast it can make water flash.

That flash is cavitation: a tiny bubble forms, collapses, and creates a second shock.

#Shorts #science #facts #mantisshrimp

Sources:
- Patek & Caldwell, Deadly strike mechanism of a mantis shrimp, Nature, DOI: 10.1038/428819a
- Patek et al., Elastic Energy Powers Mantis Shrimp Punch, Journal of Experimental Biology, DOI: 10.1242/jeb.040691
- A physical model of the extreme mantis shrimp strike, Bioinspiration & Biomimetics, DOI: 10.1088/1748-3182/9/1/016014
'''

def stamp():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def yt_client():
    creds=Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build('youtube','v3',credentials=creds)

def srt_time(sec:float)->str:
    ms=round(sec*1000); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; s=ms//1000; ms%=1000
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def write_srt():
    beats=json.loads(BEATMAP.read_text())
    fps=24.0; t=0.0; lines=[]
    for i,b in enumerate(beats,1):
        dur=b['frames']/fps
        text=b['caption'].replace(' / ','\n')
        lines += [str(i), f'{srt_time(t)} --> {srt_time(t+dur)}', text, '']
        t += dur
    PACK.mkdir(parents=True, exist_ok=True)
    SRT.write_text('\n'.join(lines), encoding='utf-8')

def verify_local():
    if not VIDEO.exists(): raise SystemExit(f'missing video {VIDEO}')
    if not CONTACT.exists(): raise SystemExit(f'missing contact sheet {CONTACT}')
    proc=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size,bit_rate','-show_streams','-of','json',str(VIDEO)], text=True, capture_output=True, check=True)
    info=json.loads(proc.stdout)
    streams=info.get('streams',[])
    v=next(s for s in streams if s.get('codec_type')=='video')
    a=next(s for s in streams if s.get('codec_type')=='audio')
    if (v.get('width'),v.get('height'))!=(1080,1920): raise SystemExit(f'bad dimensions {v.get("width")}x{v.get("height")}')
    if a.get('codec_name')!='aac': raise SystemExit('audio not AAC')
    return info

def build_pack():
    PACK.mkdir(parents=True, exist_ok=True)
    local=verify_local()
    write_srt()
    (PACK/'description_upload.txt').write_text(DESCRIPTION, encoding='utf-8')
    shutil.copy2(CONTACT, PACK/'thumbnail_candidate.jpg')
    metadata={
        'title': TITLE,
        'description_file': str((PACK/'description_upload.txt').resolve()),
        'tags': TAGS,
        'categoryId': '28',
        'privacyStatus': 'private',
        'selfDeclaredMadeForKids': False,
        'audience_note':'Kid-friendly/general audience, not made for kids.',
        'video': str(VIDEO.resolve()),
        'captions_srt': str(SRT.resolve()),
        'thumbnail_candidate': str((PACK/'thumbnail_candidate.jpg').resolve()),
        'gate_6_authorization_text': 'Josh said in Discord thread: Let’s post it on YT!',
        'created_at': stamp(),
        'local_ffprobe': local,
    }
    META.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata

def verify_video(yt, video_id):
    r=yt.videos().list(part='snippet,status,processingDetails,contentDetails', id=video_id).execute()
    if not r.get('items'): return {'video_id':video_id,'found':False}
    item=r['items'][0]
    return {
        'video_id': item['id'], 'found': True,
        'title': item['snippet'].get('title'), 'channelId': item['snippet'].get('channelId'), 'channelTitle': item['snippet'].get('channelTitle'),
        'categoryId': item['snippet'].get('categoryId'), 'tags': item['snippet'].get('tags'),
        'privacyStatus': item['status'].get('privacyStatus'), 'uploadStatus': item['status'].get('uploadStatus'),
        'selfDeclaredMadeForKids': item['status'].get('selfDeclaredMadeForKids'),
        'processingStatus': item.get('processingDetails',{}).get('processingStatus'),
        'processingFailureReason': item.get('processingDetails',{}).get('processingFailureReason'),
        'duration': item.get('contentDetails',{}).get('duration'), 'definition': item.get('contentDetails',{}).get('definition'),
        'caption': item.get('contentDetails',{}).get('caption'),
        'url': f'https://youtu.be/{item["id"]}', 'studio_url': f'https://studio.youtube.com/video/{item["id"]}/edit'
    }

def upload_private(yt, meta):
    # Idempotency: if result exists and has a video id, do not upload another copy.
    if UPLOAD.exists():
        old=json.loads(UPLOAD.read_text())
        vid=old.get('id') or old.get('video_id') or old.get('response',{}).get('id')
        if vid:
            return {'reused_existing_upload': True, 'id': vid, 'response': old}
    body={
        'snippet': {'title': meta['title'], 'description': DESCRIPTION, 'tags': meta['tags'], 'categoryId':'28'},
        'status': {'privacyStatus':'private', 'selfDeclaredMadeForKids':False, 'embeddable':True, 'publicStatsViewable':True}
    }
    media=MediaFileUpload(str(VIDEO), chunksize=-1, resumable=True, mimetype='video/mp4')
    request=yt.videos().insert(part='snippet,status', body=body, media_body=media)
    response=None
    while response is None:
        status,response=request.next_chunk()
        if status:
            print(json.dumps({'upload_progress': round(status.progress()*100,2)}), flush=True)
    UPLOAD.write_text(json.dumps(response, indent=2), encoding='utf-8')
    return {'reused_existing_upload': False, 'id': response['id'], 'response': response}

def attach_captions(yt, video_id):
    media=MediaFileUpload(str(SRT), mimetype='application/x-subrip', resumable=False)
    body={'snippet': {'videoId': video_id, 'language':'en', 'name':'English', 'isDraft':False}}
    try:
        resp=yt.captions().insert(part='snippet', body=body, media_body=media).execute()
        return {'caption_inserted': True, 'response': resp}
    except HttpError as e:
        return {'caption_inserted': False, 'error': str(e)}

def wait_processed(yt, video_id, timeout_s=900):
    start=time.time(); last=None
    while time.time()-start < timeout_s:
        info=verify_video(yt, video_id); last=info
        if info.get('uploadStatus')=='processed' and info.get('processingStatus')=='succeeded':
            return info
        print(json.dumps({'waiting_processing': info}), flush=True)
        time.sleep(20)
    return last

def publish_public(yt, video_id):
    before=verify_video(yt, video_id)
    problems=[]
    if before.get('uploadStatus')!='processed': problems.append(f'uploadStatus={before.get("uploadStatus")}')
    if before.get('processingStatus')!='succeeded': problems.append(f'processingStatus={before.get("processingStatus")}')
    if before.get('categoryId')!='28': problems.append(f'categoryId={before.get("categoryId")}')
    if before.get('selfDeclaredMadeForKids') is not False: problems.append('selfDeclaredMadeForKids not false')
    if problems: raise SystemExit('blocked before public publish: '+'; '.join(problems))
    yt.videos().update(part='status', body={'id': video_id, 'status': {'privacyStatus':'public','selfDeclaredMadeForKids':False,'embeddable':True,'publicStatsViewable':True}}).execute()
    time.sleep(3)
    after=verify_video(yt, video_id)
    event={'executed_at': stamp(), 'authorization_text':'Josh said in Discord thread: Let’s post it on YT!', 'before': before, 'after': after}
    PUBLIC_EVENT.write_text(json.dumps(event, indent=2), encoding='utf-8')
    return event

if __name__=='__main__':
    meta=build_pack()
    yt=yt_client()
    up=upload_private(yt, meta)
    vid=up['id']
    cap=attach_captions(yt, vid)
    processed=wait_processed(yt, vid)
    pub=publish_public(yt, vid)
    verification={'uploaded': up, 'captions_attach': cap, 'processed': processed, 'public_publish': pub, 'final': verify_video(yt, vid)}
    VERIFY.write_text(json.dumps(verification, indent=2), encoding='utf-8')
    print(json.dumps(verification, indent=2))
