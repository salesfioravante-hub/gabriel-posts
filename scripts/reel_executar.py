#!/usr/bin/env python3
"""Publica um Reel de @gabriel.fioravante. Uso: python3 scripts/reel_executar.py <id> [--simular]
Espera em reels/<id>/: <id>.mp4 (com a voz), capa.jpg (1080x1920) e legenda.txt, no repositorio.
O token nao fica aqui: o proxy injeta o Authorization em graph.facebook.com."""
import sys,os,json,time,urllib.request,urllib.parse,urllib.error
IG='17841400742616978'; BASE='https://graph.facebook.com/v21.0'
RAW='https://raw.githubusercontent.com/salesfioravante-hub/gabriel-posts/main'
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LOG=os.path.join(ROOT,'scripts','fila_log.json')
def call(method,path,params=None):
    url=f'{BASE}/{path}'; data=None
    if method=='GET' and params: url+='?'+urllib.parse.urlencode(params)
    if method=='POST': data=urllib.parse.urlencode(params or {}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url,data=data,method=method),timeout=180) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: return {'error_http':e.code,'body':e.read().decode()[:800]}
pid=sys.argv[1]; simular='--simular' in sys.argv
pasta=os.path.join(ROOT,'reels',pid)
leg=open(os.path.join(pasta,'legenda.txt'),encoding='utf-8').read().strip()
video=f'{RAW}/reels/{pid}/{pid}.mp4'; capa=f'{RAW}/reels/{pid}/capa.jpg'
log=json.load(open(LOG)) if os.path.exists(LOG) else {}
rec=call('GET',IG+'/media',{'fields':'caption,permalink','limit':'10'}).get('data',[])
if simular:
    print(pid,'| legenda',len(leg),'caracteres | ja publicado?',pid in log or any((m.get('caption') or '')[:80]==leg[:80] for m in rec))
    print('arquivos locais:',[f for f in ('%s.mp4'%pid,'capa.jpg','legenda.txt') if os.path.exists(os.path.join(pasta,f))]);print('\n'+leg); sys.exit()
if pid in log: sys.exit(f'{pid} ja publicado: {log[pid]}')
for m in rec:
    if (m.get('caption') or '')[:80]==leg[:80]: sys.exit(f'{pid} ja esta no perfil: {m.get("permalink")}')
r=call('POST',IG+'/media',{'media_type':'REELS','video_url':video,'cover_url':capa,'caption':leg,'share_to_feed':'true'})
if 'id' not in r: sys.exit(f'falha ao criar o Reel: {r}')
cid=r['id']
for _ in range(60):
    st=call('GET',cid,{'fields':'status_code,status'})
    if st.get('status_code')=='FINISHED': break
    if st.get('status_code') in('ERROR','EXPIRED'): sys.exit(f'processamento falhou: {st}')
    time.sleep(10)
else: sys.exit('timeout no processamento do video')
p=call('POST',IG+'/media_publish',{'creation_id':cid})
if 'id' not in p: sys.exit(f'publicacao falhou: {p}')
info=call('GET',p['id'],{'fields':'permalink,timestamp'})
log[pid]={'media_id':p['id'],'permalink':info.get('permalink'),'timestamp':info.get('timestamp')}
json.dump(log,open(LOG,'w'),indent=1); print('PUBLICADO',pid,info.get('permalink'))
