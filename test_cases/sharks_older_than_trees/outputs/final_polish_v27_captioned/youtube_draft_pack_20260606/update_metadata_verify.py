#!/usr/bin/env python3
from pathlib import Path
import json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
TOKEN=Path.home()/'.hermes/youtube_token.json'
SCOPES=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.force-ssl']
VIDEO_ID='KLwp-KbIr9I'
PACK=Path('/mnt/c/dev/curious-shorts/test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned/youtube_draft_pack_20260606')
OUT=PACK/'youtube_metadata_update_and_verify.json'
meta=json.loads((PACK/'youtube_metadata.json').read_text())
desc=(PACK/'description_upload.txt').read_text()
creds=Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request()); TOKEN.write_text(creds.to_json())
yt=build('youtube','v3',credentials=creds)
body={
  'id': VIDEO_ID,
  'snippet': {
    'title': meta['title'],
    'description': desc,
    'tags': meta['tags'],
    'categoryId': meta['categoryId'],
    'defaultLanguage': 'en',
    'defaultAudioLanguage': 'en'
  }
}
update=yt.videos().update(part='snippet', body=body).execute()
time.sleep(1)
verify=yt.videos().list(part='snippet,status,processingDetails,contentDetails', id=VIDEO_ID).execute()
result={'update': update, 'verify': verify}
OUT.write_text(json.dumps(result, indent=2))
print(json.dumps({
  'video_id': VIDEO_ID,
  'title': verify['items'][0]['snippet'].get('title'),
  'tags': verify['items'][0]['snippet'].get('tags'),
  'categoryId': verify['items'][0]['snippet'].get('categoryId'),
  'privacyStatus': verify['items'][0]['status'].get('privacyStatus'),
  'uploadStatus': verify['items'][0]['status'].get('uploadStatus'),
  'processingStatus': verify['items'][0].get('processingDetails',{}).get('processingStatus'),
  'duration': verify['items'][0].get('contentDetails',{}).get('duration'),
  'definition': verify['items'][0].get('contentDetails',{}).get('definition'),
  'caption': verify['items'][0].get('contentDetails',{}).get('caption'),
  'selfDeclaredMadeForKids': verify['items'][0]['status'].get('selfDeclaredMadeForKids')
}, indent=2))
