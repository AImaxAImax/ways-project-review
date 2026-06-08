#!/usr/bin/env python3
from pathlib import Path
import json, sys, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

TOKEN=Path.home()/'.hermes/youtube_token.json'
SCOPES=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.force-ssl']
VIDEO_ID='KLwp-KbIr9I'
CAPTIONS=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned/captions.srt')
OUT=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned/youtube_draft_pack_20260606/youtube_verification.json')

def yt_client():
    creds=Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build('youtube','v3',credentials=creds)

def verify(yt):
    r=yt.videos().list(part='snippet,status,processingDetails,contentDetails', id=VIDEO_ID).execute()
    items=r.get('items',[])
    if not items:
        return {'video_id':VIDEO_ID,'found':False}
    item=items[0]
    return {
        'video_id': item['id'],
        'found': True,
        'title': item['snippet'].get('title'),
        'channelId': item['snippet'].get('channelId'),
        'channelTitle': item['snippet'].get('channelTitle'),
        'categoryId': item['snippet'].get('categoryId'),
        'tags': item['snippet'].get('tags'),
        'privacyStatus': item['status'].get('privacyStatus'),
        'uploadStatus': item['status'].get('uploadStatus'),
        'selfDeclaredMadeForKids': item['status'].get('selfDeclaredMadeForKids'),
        'processingStatus': item.get('processingDetails',{}).get('processingStatus'),
        'processingFailureReason': item.get('processingDetails',{}).get('processingFailureReason'),
        'duration': item.get('contentDetails',{}).get('duration'),
        'definition': item.get('contentDetails',{}).get('definition'),
        'caption': item.get('contentDetails',{}).get('caption'),
        'licensedContent': item.get('contentDetails',{}).get('licensedContent'),
        'url': f'https://youtu.be/{item["id"]}',
        'studio_url': f'https://studio.youtube.com/video/{item["id"]}/edit',
    }

def attach_captions(yt):
    media=MediaFileUpload(str(CAPTIONS), mimetype='application/x-subrip', resumable=False)
    body={'snippet': {'videoId': VIDEO_ID, 'language': 'en', 'name': 'English', 'isDraft': False}}
    try:
        resp=yt.captions().insert(part='snippet', body=body, media_body=media).execute()
        return {'caption_inserted': True, 'response': resp}
    except HttpError as e:
        return {'caption_inserted': False, 'error': str(e)}

if __name__=='__main__':
    yt=yt_client()
    result={'before': verify(yt)}
    result['captions_attach']=attach_captions(yt)
    time.sleep(2)
    result['after']=verify(yt)
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
