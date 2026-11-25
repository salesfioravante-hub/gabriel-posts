#!/usr/bin/env python3
"""Le a fila (fila.csv) e diz o que tem para hoje, o que esta atrasado e quais reels dos proximos dias ainda precisam de voz.
Uso: python3 scripts/proximo_post.py                 # relatorio de hoje (horario de Brasilia)
     python3 scripts/proximo_post.py --marcar <id> <campo> <valor>   # ex.: --marcar reel1 voz recebida | --marcar e3 status publicado
Campos: status (pronto, atualizar dados, aguarda voz, publicado, pulado, produzir) e voz (pendente, recebida, n/a)."""
import csv,os,sys,json
from datetime import datetime,timedelta,timezone
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));F=os.path.join(ROOT,'fila.csv')
rows=list(csv.DictReader(open(F,encoding='utf-8')))
if len(sys.argv)>1 and sys.argv[1]=='--marcar':
    pid,campo,valor=sys.argv[2:5];ok=False
    for r in rows:
        if r['id']==pid: r[campo]=valor;ok=True
    if not ok: sys.exit('id nao encontrado: '+pid)
    w=csv.DictWriter(open(F,'w',newline='',encoding='utf-8'),fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows);print('ok',pid,campo,valor);sys.exit()
BRT=timezone(timedelta(hours=-3));hoje=datetime.now(BRT).date()
log=json.load(open(os.path.join(ROOT,'scripts','fila_log.json'))) if os.path.exists(os.path.join(ROOT,'scripts','fila_log.json')) else {}
def feito(r): return r['status'] in('publicado','pulado') or r['id'] in log
def linha(r):
    pasta=os.path.join(ROOT,r['id'] if r['formato']=='carrossel' else r['fonte_local'])
    return f"{r['id']} | {r['formato']} | {r['hora_brt']} | {r['titulo']} | status: {r['status']} | voz: {r['voz']} | pasta no repo: {'sim' if os.path.isdir(pasta) else 'NAO (preparar)'} | nota: {r['nota'][:120]}"
print('HOJE',hoje.isoformat(),hoje.strftime('%A'))
h=[r for r in rows if r['data']==hoje.isoformat() and not feito(r)]
print(*(['  '+linha(r) for r in h] or ['  nenhum post para hoje']),sep='\n')
at=[r for r in rows if r['data']<hoje.isoformat() and not feito(r)]
if at: print('ATRASADOS (nao publicados):');print(*['  '+linha(r) for r in at],sep='\n')
fim=(hoje+timedelta(days=7)).isoformat()
prox=[r for r in rows if hoje.isoformat()<r['data']<=fim and not feito(r)]
print('PROXIMOS 7 DIAS:');print(*(['  '+r['data']+' '+linha(r) for r in prox] or ['  nenhum']),sep='\n')
voz=[r for r in rows if r['formato']=='reel' and r['voz']=='pendente' and hoje.isoformat()<=r['data']<=(hoje+timedelta(days=10)).isoformat() and not feito(r)]
print('REELS COM VOZ PENDENTE NOS PROXIMOS 10 DIAS:');print(*(['  '+r['data']+' '+r['id']+' | '+r['titulo'] for r in voz] or ['  nenhum']),sep='\n')
