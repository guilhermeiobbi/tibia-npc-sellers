"""Etapa 3 — junta lojas + sprites no data.json e no atlas.

Um NPC pode aparecer em vários .lua (mesmo nome, arquivos diferentes); aqui
eles viram uma entrada só. Dos preços repetidos fica o melhor para o jogador:
o maior quando o NPC compra, o menor quando vende.

Os itens são referenciados por índice na lista `items`, que é ordenada por
nome — o mesmo índice serve de posição no atlas de sprites.

Saídas: work/data.json, work/atlas.webp, work/atlas.png
"""
import json
import os

from PIL import Image

import config
from sprites import get_sprite

COLS = 48          # sprites por linha no atlas
CELL = 32          # lado da célula, em px
SKIP_FILES = {'rashid_custom.lua'}
FLOOR = 10 ** 12   # sentinela para o menor preço de venda


def load_meta():
    meta = json.load(open(config.NPC_META, encoding='utf-8'))
    return meta['featured'], meta['notes']


def merge_npcs(npcs):
    """Agrupa por nome de NPC: {nome: {'s': {id: preço}, 'b': {id: preço}}}."""
    merged = {}
    for _file, npc in sorted(npcs.items()):
        if not any(i['sell'] for i in npc['items']):
            continue                      # não compra nada do jogador
        m = merged.setdefault(npc['name'], {'s': {}, 'b': {}})
        for i in npc['items']:
            if i['sell']:
                m['s'][i['id']] = max(i['sell'], m['s'].get(i['id'], 0))
            if i['buy']:
                m['b'][i['id']] = min(i['buy'], m['b'].get(i['id'], FLOOR))
    return merged


def build_atlas(ids, idx, objs):
    """Monta a folha única de sprites, na ordem dos índices."""
    missing = [i for i in ids if i not in objs or not objs[i].get('sprites')]
    if missing:
        raise SystemExit(
            '%d itens sem sprite no appearances.dat (ex: %s).\n'
            'O client e os dados do Canary estão em versões diferentes?'
            % (len(missing), missing[:8]))
    rows = (len(ids) + COLS - 1) // COLS
    atlas = Image.new('RGBA', (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for i, n in idx.items():
        s = get_sprite(objs[i]['sprites'][0])
        if s.size != (CELL, CELL):        # itens 64px entram reduzidos
            s.thumbnail((CELL, CELL), Image.LANCZOS)
        # zera o RGB dos pixels transparentes: evita franja clara na borda e
        # comprime bem melhor
        px = s.load()
        for y in range(s.height):
            for x in range(s.width):
                if px[x, y][3] == 0:
                    px[x, y] = (0, 0, 0, 0)
        atlas.paste(s, ((n % COLS) * CELL + (CELL - s.width) // 2,
                        (n // COLS) * CELL + (CELL - s.height) // 2))
    return atlas


def build_payload(merged, names, ids, idx, featured, notes):
    """O objeto que o template consome. Chaves curtas: o JSON vai inline no HTML."""
    known = [n for n in featured if n in merged]
    for n in featured:
        if n not in merged:
            print('  aviso: "%s" está em npc_meta.json mas não nos dados' % n)
    order = known + sorted(n for n in merged if n not in featured)
    out = dict(cols=COLS, items=[names[i] for i in ids], npcs=[])
    for n in order:
        m, note = merged[n], notes.get(n, {})
        e = dict(n=n,
                 s=sorted([idx[i], p] for i, p in m['s'].items()),
                 b=sorted([idx[i], p] for i, p in m['b'].items()))
        if n in known:
            e['f'] = 1
        if 'g' in note:
            e['g'] = note['g']
        if 'note' in note:
            e['t'] = note['note']
        out['npcs'].append(e)
    return out


if __name__ == '__main__':
    config.ensure_work()
    npcs = json.load(open(config.NPCS_RAW, encoding='utf-8'))
    for f in SKIP_FILES:
        npcs.pop(f, None)
    objs = {int(k): v for k, v in json.load(open(config.OBJS, encoding='utf-8')).items()}
    featured, notes = load_meta()

    merged = merge_npcs(npcs)
    names = {}
    for npc in npcs.values():
        for i in npc['items']:
            names.setdefault(i['id'], i['n'])

    # ordem alfabética define o índice, que vale para a lista E para o atlas
    ids = sorted({i for m in merged.values() for d in (m['s'], m['b']) for i in d},
                 key=lambda i: (names[i], i))
    idx = {i: n for n, i in enumerate(ids)}

    atlas = build_atlas(ids, idx, objs)
    atlas.save(config.ATLAS_PNG, optimize=True)
    atlas.save(config.ATLAS_WEBP, lossless=True, quality=100, method=6)

    out = build_payload(merged, names, ids, idx, featured, notes)
    json.dump(out, open(config.DATA, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('%d itens, %d npcs — data %d KB, webp %d KB (png %d KB)'
          % (len(ids), len(out['npcs']),
             os.path.getsize(config.DATA) // 1024,
             os.path.getsize(config.ATLAS_WEBP) // 1024,
             os.path.getsize(config.ATLAS_PNG) // 1024))
