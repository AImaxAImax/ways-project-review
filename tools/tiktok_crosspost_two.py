#!/usr/bin/env python3
import json, time, requests, sys
from pathlib import Path
from cdp_tiktok_helper import CDP
HOST='http://127.0.0.1:9222'

def win_path(p):
    s=str(Path(p))
    if s.startswith('/mnt/c/'):
        return 'C:\\' + s[len('/mnt/c/'):].replace('/','\\')
    return s

def rel_lines(txt):
    keys=['Uploaded','Uploading','Description','No issues found','Checking','Post','Content under review','Views','Likes','Comments','couldn','failed','violation']
    return [ln for ln in txt.splitlines() if any(k.lower() in ln.lower() for k in keys)]

def new_tab(url):
    t=requests.put(HOST+'/json/new', timeout=10).json(); c=CDP(t); c.call('Page.navigate', {'url':url}); return c

def set_file(c, path):
    root=c.call('DOM.getDocument', {'depth':-1, 'pierce':True})['root']['nodeId']
    node=c.call('DOM.querySelector', {'nodeId':root, 'selector':'input[type=file]'})['nodeId']
    c.call('DOM.setFileInputFiles', {'nodeId':node, 'files':[win_path(path)]})

def set_caption(c, caption):
    for attempt in range(5):
        c.eval('document.querySelector("[contenteditable=true]")?.focus()')
        time.sleep(.2)
        c.call('Input.dispatchKeyEvent', {'type':'keyDown','key':'Control','code':'ControlLeft','windowsVirtualKeyCode':17,'modifiers':2})
        c.call('Input.dispatchKeyEvent', {'type':'keyDown','key':'a','code':'KeyA','windowsVirtualKeyCode':65,'modifiers':2})
        c.call('Input.dispatchKeyEvent', {'type':'keyUp','key':'a','code':'KeyA','windowsVirtualKeyCode':65,'modifiers':2})
        c.call('Input.dispatchKeyEvent', {'type':'keyUp','key':'Control','code':'ControlLeft','windowsVirtualKeyCode':17,'modifiers':0})
        time.sleep(.1)
        c.call('Input.dispatchKeyEvent', {'type':'keyDown','key':'Backspace','code':'Backspace','windowsVirtualKeyCode':8})
        c.call('Input.dispatchKeyEvent', {'type':'keyUp','key':'Backspace','code':'Backspace','windowsVirtualKeyCode':8})
        time.sleep(.4)
        c.call('Input.insertText', {'text':caption})
        time.sleep(.8)
        text=c.eval('document.querySelector("[contenteditable=true]")?.innerText || ""')['result'].get('value','')
        if text.strip()==caption:
            return text.strip()
    return c.eval('document.querySelector("[contenteditable=true]")?.innerText || ""')['result'].get('value','').strip()

def wait_upload(c, max_s=240):
    for i in range(max_s//2):
        time.sleep(2)
        txt=c.eval('document.body.innerText')['result'].get('value','')
        if i%5==0: print('upload_wait',i*2,'|',' | '.join(rel_lines(txt)[:15]), flush=True)
        if 'Uploaded' in txt and 'Uploading...' not in txt:
            return txt
    raise RuntimeError('upload timeout')

def wait_checks(c, max_s=240):
    status='unknown'
    for i in range(max_s//2):
        time.sleep(2)
        txt=c.eval('document.body.innerText')['result'].get('value','')
        if i%5==0: print('check_wait',i*2,'|',' | '.join(rel_lines(txt)[:18]), flush=True)
        if txt.count('No issues found') >= 2:
            return 'no_issues_found'
        if 'Post' in txt and i>=15:
            status='post_button_present_checks_pending'
        if any(bad in txt.lower() for bad in ['failed','violation','couldn\'t be uploaded']):
            return 'possible_issue_'+ '|'.join(rel_lines(txt)[-6:])
    return status

def click_post(c):
    return c.eval('''(() => {
      const buttons=Array.from(document.querySelectorAll('button,[role=button]'));
      const b=buttons.find(x => (x.innerText||'').trim()==='Post' && !x.disabled && x.getAttribute('aria-disabled')!=='true');
      if(!b) return {clicked:false, body:document.body.innerText.slice(-1200)};
      b.scrollIntoView({block:'center'}); b.click(); return {clicked:true};
    })()''')['result']['value']

def wait_final(c, max_s=180):
    last={}
    for i in range(max_s//2):
        time.sleep(2)
        href=c.eval('location.href')['result'].get('value','')
        body=c.eval('document.body.innerText.slice(0,3000)')['result'].get('value','')
        last={'href':href,'lines':' | '.join(rel_lines(body)[:25])}
        if i%5==0: print('post_wait',i*2,href,'|',last['lines'], flush=True)
        if 'Content under review' in body:
            last['final']='content_under_review'; return last
        if '/tiktokstudio/content' in href and ('Views' in body or 'Posts' in body):
            last['final']='accepted_content_page'; return last
        if 'Post' not in body and 'Uploading' not in body and '/tiktokstudio/content' in href:
            last['final']='content_page'; return last
    last['final']='unknown_after_wait'; return last

def upload_post(item, existing_tab_id=None):
    if existing_tab_id:
        t=[x for x in requests.get(HOST+'/json/list',timeout=5).json() if x.get('id')==existing_tab_id][0]
        c=CDP(t)
    else:
        c=new_tab('https://www.tiktok.com/tiktokstudio/upload'); time.sleep(7); set_file(c,item['path'])
    try:
        wait_upload(c)
        cap=set_caption(c,item['caption'])
        print('caption_set',cap, flush=True)
        checks=wait_checks(c)
        print('checks',checks, flush=True)
        click=click_post(c); print('click',json.dumps(click), flush=True)
        final=wait_final(c)
        final.update({'slug':item['slug'],'file':str(item['path']),'caption':item['caption'],'checks':checks})
        return final
    finally:
        try: c.close()
        except Exception: pass

POSTS=[
{'slug':'mantis_shrimp_cavitation_punch','path':Path('/mnt/c/dev/curious-shorts/tmp/tiktok_crosspost/ready/4lnxNc3nKz4_tiktok_ready.mp4'),'caption':'A mantis shrimp punches so fast it makes the water flash. Then the bubble collapse hits again. #waitareyouserious #sciencefacts #mantisshrimp #weirdfacts #animalfacts #marinebiology #learnontiktok'},
{'slug':'wombat_cube_poop','path':Path('/mnt/c/dev/curious-shorts/tmp/tiktok_crosspost/ready/nGopqhC66ls_tiktok_ready.mp4'),'caption':'Wombats poop cubes. The shape forms inside the intestine, then helps mark territory. #waitareyouserious #animalfacts #wombat #weirdfacts #naturefacts #sciencefacts #learnontiktok'}]
if __name__=='__main__':
    results=[]
    # If first arg is a tab id, use it for the first post already uploading.
    existing=sys.argv[1] if len(sys.argv)>1 else None
    for idx,item in enumerate(POSTS):
        print('\n===',item['slug'],'===', flush=True)
        results.append(upload_post(item, existing if idx==0 else None))
    print('RESULTS_JSON')
    print(json.dumps(results,indent=2))
