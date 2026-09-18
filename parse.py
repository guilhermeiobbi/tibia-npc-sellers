import re,glob,json,os
npcs={}
for f in sorted(glob.glob('/home/claude/canary/data-otservbr-global/npc/*.lua')):
    s=open(f,encoding='utf-8',errors='ignore').read()
    m=re.search(r'npcConfig\.shop\s*=\s*\{(.*?)\n\}',s,re.S)
    if not m: continue
    name=re.search(r'internalNpcName\s*=\s*"([^"]+)"',s)
    name=name.group(1) if name else os.path.basename(f)
    items=[]
    for e in re.findall(r'\{([^{}]*)\}',m.group(1)):
        n=re.search(r'itemName\s*=\s*"([^"]+)"',e); c=re.search(r'clientId\s*=\s*(\d+)',e)
        if not n or not c: continue
        b=re.search(r'\bbuy\s*=\s*(\d+)',e); se=re.search(r'\bsell\s*=\s*(\d+)',e)
        items.append(dict(n=n.group(1),id=int(c.group(1)),buy=int(b.group(1)) if b else None,sell=int(se.group(1)) if se else None))
    npcs[os.path.basename(f)]=dict(name=name,items=items)
json.dump(npcs,open('/home/claude/npcs_raw.json','w'))
sellers={k:v for k,v in npcs.items() if any(i['sell'] for i in v['items'])}
ids=set(i['id'] for v in sellers.values() for i in v['items'] if i['sell'])
print(len(npcs),'npcs w/ shop;',len(sellers),'buy from player;',len(ids),'unique sellable items')
for k,v in sorted(sellers.items(), key=lambda kv:-sum(1 for i in kv[1]['items'] if i['sell']))[:45]:
    print(k, v['name'], sum(1 for i in v['items'] if i['sell']))
