#!/usr/bin/env python3
"""Relatorio semanal de @gabriel.fioravante (somente leitura). Uso: python3 scripts/relatorio_semanal.py
Imprime o relatorio em texto e guarda o snapshot de seguidores em scripts/relatorio_historico.json."""
import os,json,time,statistics as st,urllib.request,urllib.parse,urllib.error
from datetime import datetime,timedelta,timezone
IG='17841400742616978';BASE='https://graph.facebook.com/v21.0'
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));HIST=os.path.join(ROOT,'scripts','relatorio_historico.json')
BASE_MEDIANA=764; BASE_SEGUIDORES=5240   # linha de base medida em 21/11/2026 (50 midias)
def get(path,params=None):
    url=f'{BASE}/{path}'+('?'+urllib.parse.urlencode(params) if params else '')
    try:
        with urllib.request.urlopen(urllib.request.Request(url),timeout=90) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: return {'erro':e.code,'corpo':e.read().decode()[:200]}
def chave(mid):
    r=get(mid+'/comments',{'fields':'text','limit':'100'});t=[(c.get('text') or '').lower() for c in r.get('data',[])]
    return sum('bfr' in x for x in t),sum('sala' in x for x in t),len(t)
def ins(mid):
    r=get(mid+'/insights',{'metric':'reach,saved,shares,total_interactions,views'})
    if 'erro' in r: r=get(mid+'/insights',{'metric':'reach,saved,shares,total_interactions'})
    return {d['name']:d['values'][0]['value'] for d in r.get('data',[])}
BRT=timezone(timedelta(hours=-3));agora=datetime.now(BRT)
perfil=get(IG,{'fields':'followers_count,media_count'})
if 'erro' in perfil: print('ERRO ao ler a conta (token expirou?):',perfil); raise SystemExit(1)
lista=get(IG+'/media',{'fields':'id,media_type,media_product_type,timestamp,like_count,comments_count,permalink,caption','limit':'50'}).get('data',[])
limite=agora-timedelta(days=7)
posts=[]
for m in lista:
    t=datetime.fromisoformat(m['timestamp'].replace('+0000','+00:00')).astimezone(BRT)
    if t>=limite:
        b,sa,nc=chave(m['id']);posts.append({**m,'t':t,'kbfr':b,'ksala':sa,'ncom':nc,**ins(m['id'])})
hist=json.load(open(HIST)) if os.path.exists(HIST) else []
ant=hist[-1] if hist else {'data':'21/11/2026','seguidores':BASE_SEGUIDORES}
seg=perfil['followers_count']
hist.append({'data':agora.strftime('%d/%m/%Y'),'seguidores':seg,'posts_semana':len(posts)});json.dump(hist,open(HIST,'w'),indent=1)
print(f"RELATORIO SEMANAL @gabriel.fioravante | {agora.strftime('%d/%m/%Y')} (7 dias)\n")
print(f"Seguidores: {seg} ({seg-ant['seguidores']:+d} desde {ant['data']}) | linha de base 21/11: {BASE_SEGUIDORES}")
if not posts: print('\nNenhum post nos ultimos 7 dias.'); raise SystemExit
def f(p,k): return p.get(k,0) or 0
rs=[f(p,'reach') for p in posts]; med=st.median(rs)
print(f"Posts: {len(posts)} | alcance mediano {med:.0f} (base {BASE_MEDIANA}: {med/BASE_MEDIANA-1:+.0%})")
print(f"Salvamentos: {sum(f(p,'saved') for p in posts)} | compartilhamentos: {sum(f(p,'shares') for p in posts)} (base mediana: 1 por post)\n")
print('Por post (alcance | salvos | compart. | interacoes | taxa de interacao):')
for p in sorted(posts,key=lambda p:-f(p,'reach')):
    r=f(p,'reach');er=f(p,'total_interactions')/r if r else 0
    print(f"- {p['t'].strftime('%d/%m %Hh')} {p['media_product_type']:<5} {r:>5} | {f(p,'saved'):>3} | {f(p,'shares'):>3} | {f(p,'total_interactions'):>4} | {er:.1%} | {(p.get('caption') or '')[:40]!r} {p['permalink']}")
top=sorted(posts,key=lambda p:-f(p,'reach'))
if len(top)>=3: print(f"\nMelhores: {top[0]['permalink']} e {top[1]['permalink']}\nPiores:   {top[-1]['permalink']} e {top[-2]['permalink']}")
abaixo=[p for p in posts if f(p,'reach')<0.7*BASE_MEDIANA]
print(f"\nPosts abaixo de 70% da mediana-base (<{0.7*BASE_MEDIANA:.0f} de alcance): {len(abaixo)} de {len(posts)}")
print('ALERTA: 3 ou mais abaixo do piso -> propor ajuste de formato/horario/gancho (so com OK do Gabriel).' if len(abaixo)>=3 else 'Sem alerta de ajuste.')

# contas BFR: meta de 30 ate 31/01/2027, a partir de 26/11/2026 (o Gabriel informa as contas migradas)
import csv
arq=os.path.join(ROOT,'scripts','contas_bfr.csv')
if os.path.exists(arq):
    L=list(csv.DictReader(open(arq,encoding='utf-8')));ac=sum(int(r['novas']) for r in L)
    d0=datetime(2026,11,26,tzinfo=BRT);d1=datetime(2027,1,31,tzinfo=BRT);prev=30*min(1,max(0,(agora-d0)/(d1-d0)))
    print(f"\nContas BFR: {ac} de 30 (ritmo linear previsto hoje: {prev:.0f})")
