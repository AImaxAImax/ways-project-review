#!/usr/bin/env python3
import json, time, itertools
import requests
import websocket

HOST='http://127.0.0.1:9222'
_counter=itertools.count(1)

def tabs():
    return requests.get(HOST+'/json/list', timeout=5).json()

def get_tab(url_contains=None, title_contains=None):
    for t in tabs():
        if t.get('type')!='page': continue
        if url_contains and url_contains in t.get('url',''): return t
        if title_contains and title_contains.lower() in t.get('title','').lower(): return t
    return None

def new_tab(url='about:blank'):
    # Chrome remote debugging supports PUT /json/new?url
    r=requests.put(HOST+'/json/new?'+requests.utils.quote(url, safe=':/?=&'), timeout=5)
    return r.json()

class CDP:
    def __init__(self, tab):
        self.ws=websocket.create_connection(tab['webSocketDebuggerUrl'], timeout=60)
    def call(self, method, params=None):
        i=next(_counter)
        self.ws.send(json.dumps({'id':i,'method':method,'params':params or {}}))
        while True:
            msg=json.loads(self.ws.recv())
            if msg.get('id')==i:
                if 'error' in msg:
                    raise RuntimeError(msg['error'])
                return msg.get('result')
    def eval(self, expr, awaitPromise=False):
        return self.call('Runtime.evaluate', {'expression':expr,'returnByValue':True,'awaitPromise':awaitPromise})
    def close(self):
        self.ws.close()

def ensure_tiktok(path='/'):
    tab=get_tab(url_contains='tiktok.com') or get_tab(title_contains='TikTok') or new_tab('https://www.tiktok.com'+path)
    c=CDP(tab)
    c.call('Page.enable')
    c.call('Runtime.enable')
    if 'tiktok.com' not in tab.get('url',''):
        c.call('Page.navigate', {'url':'https://www.tiktok.com'+path})
    return c

if __name__=='__main__':
    print(json.dumps(tabs(), indent=2)[:2000])
