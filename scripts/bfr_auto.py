#!/usr/bin/env python3
"""Resposta automatica por palavra-chave nos comentarios do @gabriel.fioravante.
Quem comenta "BFR" recebe, no direct, o passo a passo da troca de assessoria e as condicoes do trader (resposta privada),
e uma resposta publica curta. Uma resposta privada por comentario (regra da Meta, ate 7 dias depois do comentario).
Uso: python3 scripts/bfr_auto.py [--simular]
O token nao fica aqui: o proxy do ambiente injeta o Authorization em graph.facebook.com.
Estado em scripts/auto_state.json (so ids de comentarios). Os nomes de usuario ficam em scripts/leads_local.csv, fora do git."""
import sys,os,re,json,time,csv,urllib.request,urllib.parse,urllib.error
from datetime import datetime,timedelta,timezone
IG='17841400742616978';B='https://graph.facebook.com/v21.0/'
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST=os.path.join(ROOT,'scripts','auto_state.json');LEADS=os.path.join(ROOT,'scripts','leads_local.csv')
EU='gabriel.fioravante'
DM_BFR=("Oi! Aqui é o Gabriel. Passo a passo para trocar para a BFR:\n"
"1. Login na XP pelo site (portal.xpi.com.br), no navegador. Pelo app não é possível.\n"
"2. Atendimento > Troque de assessor > Alterar.\n"
"3. Motivo: o mais adequado, e no texto: \"Assessoria especializada, relacionamento com o assessor solicitado\".\n"
"4. Assessor: 67544 - Lenon Rissardi. Clique em Enviar informações.\n"
"Ainda não é cliente? Abra a conta: https://cadastro.xpi.com.br/v3/cadastro/nome?assessor=A67544\n"
"Condições do trader, por mês: Profit PRO com 1 mini, Automação da Nelogica com 11 minis, corretagem zero em futuros. Podem mudar.\n"
"Me responda aqui com seu nome e quantos minis você opera.")
PUB_BFR="Te enviei o passo a passo no direct. Se não chegou, me chama lá."
REGRAS=[(re.compile(r'\bbfr\b',re.I),'bfr',DM_BFR,PUB_BFR)]
assert len(DM_BFR.encode('utf-8'))<=1000,len(DM_BFR.encode('utf-8'))
def call(method,path,params=None):
    url=B+path;data=None
    if method=='GET' and params: url+='?'+urllib.parse.urlencode(params)
    if method=='POST': data=urllib.parse.urlencode(params or {}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url,data=data,method=method),timeout=60) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return {'erro':json.loads(e.read().decode())['error']}
        except Exception: return {'erro':{'message':str(e),'code':e.code}}
simular='--simular' in sys.argv
estado=json.load(open(ST)) if os.path.exists(ST) else {'feitos':{}}
agora=datetime.now(timezone.utc);corte=agora-timedelta(days=7)
midias=call('GET',IG+'/media',{'fields':'id,timestamp,permalink','limit':'20'}).get('data',[])
novos=0;ok=0;falhas=0
for m in midias:
    cs=call('GET',m['id']+'/comments',{'fields':'id,text,username,timestamp','limit':'100'}).get('data',[])
    for c in cs:
        if c['id'] in estado['feitos'] or (c.get('username')==EU): continue
        t=datetime.fromisoformat(c['timestamp'].replace('+0000','+00:00'))
        if t<corte: continue
        for rx,kw,dm,pub in REGRAS:
            if rx.search(c.get('text') or ''):
                novos+=1
                print(('SIMULA ' if simular else '')+f"comentario {c['id']} de @{c.get('username')} em {m['permalink']}: {c.get('text')!r}")
                if simular: break
                r=call('POST',IG+'/messages',{'recipient':json.dumps({'comment_id':c['id']}),'message':json.dumps({'text':dm})})
                if 'erro' in r:
                    e=r['erro'];print('  FALHA no direct:',e.get('code'),e.get('message','')[:200]);falhas+=1
                    if e.get('code')==200: sys.exit('Acesso a mensagens desativado no Instagram: ative em Configurações > Mensagens e respostas a stories > Ferramentas conectadas.')
                    if e.get('code') in (10903,10900): estado['feitos'][c['id']]={'t':agora.isoformat(),'kw':kw,'ok':False,'motivo':'ja respondido ou janela expirada'}
                    break
                call('POST',c['id']+'/replies',{'message':pub})
                estado['feitos'][c['id']]={'t':agora.isoformat(),'kw':kw,'ok':True};ok+=1
                novo=not os.path.exists(LEADS)
                with open(LEADS,'a',newline='',encoding='utf-8') as f:
                    w=csv.writer(f)
                    if novo: w.writerow(['quando_utc','usuario','palavra','post'])
                    w.writerow([agora.isoformat(),c.get('username'),kw,m['permalink']])
                time.sleep(1.2);break
if not simular: json.dump(estado,open(ST,'w'),indent=1)
print(f'novos: {novos} | enviados: {ok} | falhas: {falhas} | total ja atendidos: {len(estado["feitos"])}')
