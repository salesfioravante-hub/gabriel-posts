#!/usr/bin/env python3
"""Publica um post da fila de @gabriel.fioravante.
Uso: python3 scripts/fila_executar.py <id> [--simular]
Cria os conteineres e publica na sequencia (sem esperar horas: o conteiner vale ~24h).
Trava de duplicidade: se o id ja esta em scripts/fila_log.json, nao publica de novo.
O token nao fica aqui: o proxy do ambiente injeta o Authorization em graph.facebook.com.
"""
import sys,os,json,time,glob,urllib.request,urllib.parse,urllib.error
IG='17841400742616978'; BASE='https://graph.facebook.com/v21.0'
RAW='https://raw.githubusercontent.com/salesfioravante-hub/gabriel-posts/main'
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG=os.path.join(ROOT,'scripts','fila_log.json')
def call(method,path,params=None):
    url=f'{BASE}/{path}'; data=None
    if method=='GET' and params: url+='?'+urllib.parse.urlencode(params)
    if method=='POST': data=urllib.parse.urlencode(params or {}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url,data=data,method=method),timeout=120) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: return {'error_http':e.code,'body':e.read().decode()[:800]}
def espera(cid,n=40):
    for _ in range(n):
        r=call('GET',cid,{'fields':'status_code'}); sc=r.get('status_code')
        if sc=='FINISHED': return True
        if sc in('ERROR','EXPIRED'): print('FALHA',r); return False
        time.sleep(4)
    return False
pid=sys.argv[1]; simular='--simular' in sys.argv
pasta=os.path.join(ROOT,pid)
imgs=sorted(os.path.basename(p) for p in glob.glob(os.path.join(pasta,f'{pid}-*.jpg')))
urls=[f'{RAW}/{pid}/{i}' for i in imgs]
leg=open(os.path.join(pasta,'legenda.txt'),encoding='utf-8').read().strip()
log=json.load(open(LOG)) if os.path.exists(LOG) else {}
if simular:
    print(pid,len(urls),'imagens | legenda',len(leg),'caracteres'); print('\n'+leg)
    print('\nja publicado?',pid in log); print('conta:',call('GET',IG,{'fields':'username'}))
    print('cota:',call('GET',IG+'/content_publishing_limit',{'fields':'quota_usage'}))
    for u in urls[:1]+urls[-1:]:
        try: print(u,urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=30).status)
        except Exception as e: print(u,'HEAD falhou (pode ser so o proxy local):',e)
    sys.exit()
if pid in log: sys.exit(f'{pid} ja publicado: {log[pid]}')
# trava 2: se o container foi recriado e o log sumiu, confere a legenda nas ultimas midias da conta
rec=call('GET',IG+'/media',{'fields':'caption,permalink,timestamp','limit':'10'}).get('data',[])
for m in rec:
    if (m.get('caption') or '')[:80]==leg[:80]: sys.exit(f'{pid} ja esta no perfil: {m.get("permalink")}')
assert 2<=len(urls)<=10
filhos=[]
for u in urls:
    r=call('POST',IG+'/media',{'image_url':u,'is_carousel_item':'true'})
    if 'id' not in r: sys.exit(f'falha item {u}: {r}')
    filhos.append(r['id'])
if not all(espera(f) for f in filhos): sys.exit('item nao ficou pronto')
r=call('POST',IG+'/media',{'media_type':'CAROUSEL','children':','.join(filhos),'caption':leg})
if 'id' not in r or not espera(r['id']): sys.exit(f'carrossel falhou: {r}')
p=call('POST',IG+'/media_publish',{'creation_id':r['id']})
if 'id' not in p: sys.exit(f'publicacao falhou: {p}')
info=call('GET',p['id'],{'fields':'permalink,timestamp'})
log[pid]={'media_id':p['id'],'permalink':info.get('permalink'),'timestamp':info.get('timestamp')}
json.dump(log,open(LOG,'w'),indent=1); print('PUBLICADO',pid,info.get('permalink'))
