import json,io,base64
from PIL import Image
from sprites import get_sprite
npcs=json.load(open('npcs_raw.json')); npcs.pop('rashid_custom.lua',None)
objs={int(k):v for k,v in json.load(open('objs.json')).items()}
META={
 "Rashid":dict(g="rashid",note="Mercador viajante: seg Svargrond, ter Liberty Bay, qua Port Hope, qui Ankrahmun, sex Darashia, sáb Edron, dom Carlin. Exige a quest The Travelling Trader."),
 "Nah'Bob":dict(g="blue",note="Blue Djinn — equipamentos. Fica em Ashta'daramai. Exige a Blue Djinn Quest (facção Marid)."),
 "Haroun":dict(g="blue",note="Blue Djinn — itens mágicos. Fica em Ashta'daramai. Exige a Blue Djinn Quest (facção Marid)."),
 "Alesar":dict(g="green",note="Green Djinn — equipamentos. Fica em Mal'ouquah. Exige a Green Djinn Quest (facção Efreet)."),
 "Yaman":dict(g="green",note="Green Djinn — itens mágicos. Fica em Mal'ouquah. Exige a Green Djinn Quest (facção Efreet)."),
 "Esrik":dict(note="Farmine. Só negocia depois de avançar na quest The New Frontier."),
 "Yasir":dict(note="Compra produtos de criatura. Aparece aleatoriamente em Ankrahmun, Carlin ou Liberty Bay — não é todo dia."),
 "Grizzly Adams":dict(note="Port Hope (Paw and Fur Society). A lista liberada depende do seu rank na Killing in the Name of…"),
 "Gnomission":dict(note="Gnomos (Bigfoot's Burden). Exige rank na quest."),
 "Flint":dict(note="Rathleton (Oramond)."),
}
FEATURED=["Rashid","Nah'Bob","Haroun","Alesar","Yaman","Esrik","Yasir","Tamoril","Telas","Gnomission","Flint","Grizzly Adams"]
merged={}
for k,v in sorted(npcs.items()):
    if not any(i['sell'] for i in v['items']): continue
    m=merged.setdefault(v['name'],{'s':{},'b':{}})
    for i in v['items']:
        if i['sell']: m['s'][i['id']]=max(i['sell'],m['s'].get(i['id'],0))
        if i['buy']: m['b'][i['id']]=min(i['buy'],m['b'].get(i['id'],10**12))
names={}
for v in npcs.values():
    for i in v['items']: names.setdefault(i['id'],i['itemName'] if 'itemName' in i else i['n'])
ids=sorted({i for m in merged.values() for d in (m['s'],m['b']) for i in d}, key=lambda i:(names[i],i))
idx={i:n for n,i in enumerate(ids)}
COLS=48; rows=(len(ids)+COLS-1)//COLS
atlas=Image.new('RGBA',(COLS*32,rows*32),(0,0,0,0))
for i,n in idx.items():
    s=get_sprite(objs[i]['sprites'][0])
    if s.size!=(32,32):
        s.thumbnail((32,32),Image.LANCZOS)
    px=s.load()
    for y in range(s.height):
        for x in range(s.width):
            if px[x,y][3]==0: px[x,y]=(0,0,0,0)
    atlas.paste(s,((n%COLS)*32+(32-s.width)//2,(n//COLS)*32+(32-s.height)//2))
atlas.save('atlas.png',optimize=True)
atlas.save('atlas.webp',lossless=True,quality=100,method=6)
order=FEATURED+sorted(n for n in merged if n not in FEATURED)
out=dict(cols=COLS,items=[names[i] for i in ids],npcs=[])
for n in order:
    m=merged[n]; meta=META.get(n,{})
    e=dict(n=n,s=sorted([[idx[i],p] for i,p in m['s'].items()]),b=sorted([[idx[i],p] for i,p in m['b'].items()]))
    if n in FEATURED: e['f']=1
    if 'g' in meta: e['g']=meta['g']
    if 'note' in meta: e['t']=meta['note']
    out['npcs'].append(e)
json.dump(out,open('data.json','w'),ensure_ascii=False,separators=(',',':'))
import os
print(len(ids),'items',len(out['npcs']),'npcs; data',os.path.getsize('data.json'),'png',os.path.getsize('atlas.png'),'webp',os.path.getsize('atlas.webp'))
