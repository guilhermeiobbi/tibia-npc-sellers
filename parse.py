"""Etapa 1 — lê os .lua de NPC do Canary e extrai as lojas.

Cada arquivo de NPC traz um npcConfig.shop com as linhas de negociação. O que
interessa de cada linha: nome do item, clientId (o id de sprite, que é o que
liga o item ao atlas) e os preços de buy/sell na perspectiva do NPC.

Saída: work/npcs_raw.json
"""
import re
import glob
import json
import os

import config

SHOP = re.compile(r'npcConfig\.shop\s*=\s*\{(.*?)\n\}', re.S)
NAME = re.compile(r'internalNpcName\s*=\s*"([^"]+)"')
ENTRY = re.compile(r'\{([^{}]*)\}')
FIELDS = {
    'n': re.compile(r'itemName\s*=\s*"([^"]+)"'),
    'id': re.compile(r'clientId\s*=\s*(\d+)'),
    'buy': re.compile(r'\bbuy\s*=\s*(\d+)'),
    'sell': re.compile(r'\bsell\s*=\s*(\d+)'),
}


def parse_shop(text):
    """Linhas da loja de um arquivo .lua, ou [] se ele não tiver loja."""
    shop = SHOP.search(text)
    if not shop:
        return []
    items = []
    for entry in ENTRY.findall(shop.group(1)):
        name = FIELDS['n'].search(entry)
        cid = FIELDS['id'].search(entry)
        if not name or not cid:  # linha sem item utilizável
            continue
        buy = FIELDS['buy'].search(entry)
        sell = FIELDS['sell'].search(entry)
        items.append(dict(
            n=name.group(1),
            id=int(cid.group(1)),
            buy=int(buy.group(1)) if buy else None,
            sell=int(sell.group(1)) if sell else None,
        ))
    return items


def parse_all(npc_dir):
    npcs = {}
    for path in sorted(glob.glob(os.path.join(npc_dir, '*.lua'))):
        text = open(path, encoding='utf-8', errors='ignore').read()
        items = parse_shop(text)
        if not items:
            continue
        name = NAME.search(text)
        npcs[os.path.basename(path)] = dict(
            name=name.group(1) if name else os.path.basename(path),
            items=items,
        )
    return npcs


def report(npcs):
    """Quem compra do jogador — é essa lista que alimenta o npc_meta.json."""
    sellers = {k: v for k, v in npcs.items() if any(i['sell'] for i in v['items'])}
    ids = set(i['id'] for v in sellers.values() for i in v['items'] if i['sell'])
    print('%d npcs com loja; %d compram do jogador; %d itens vendáveis distintos'
          % (len(npcs), len(sellers), len(ids)))
    print('\nMaiores compradores:')
    top = sorted(sellers.items(), key=lambda kv: -sum(1 for i in kv[1]['items'] if i['sell']))
    for k, v in top[:45]:
        print('  %-34s %-24s %d' % (k, v['name'], sum(1 for i in v['items'] if i['sell'])))


if __name__ == '__main__':
    config.require(config.NPC_LUA, 'os arquivos de NPC do Canary')
    config.ensure_work()
    npcs = parse_all(config.NPC_LUA)
    json.dump(npcs, open(config.NPCS_RAW, 'w', encoding='utf-8'))
    report(npcs)
