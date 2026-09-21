"""Etapa 2 — lê o appearances-*.dat do client e mapeia item -> sprites.

O arquivo é protobuf, mas o .proto não vem junto. Em vez de tentar reconstruir
o schema, percorremos os campos crus pelo número: protobuf codifica cada campo
como (número, tipo) + valor, então dá pra navegar sabendo só onde olhar.

Campos usados (descobertos por inspeção):
  1  objeto              4  nome
  2  frame group         2.3 sprite info -> 1..4 dimensões, 5 lista de sprite ids

Saída: work/objs.json  ({clientId: {name, sprites, info}})
"""
import glob
import json
import os

import config


def varint(buf, i):
    """Inteiro de tamanho variável: 7 bits por byte, bit 8 diz se continua."""
    result = shift = 0
    while True:
        byte = buf[i]
        i += 1
        result |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            return result, i


def fields(buf):
    """Itera (número do campo, wire type, valor) sobre uma mensagem protobuf."""
    i, n = 0, len(buf)
    while i < n:
        key, i = varint(buf, i)
        num, wire = key >> 3, key & 7
        if wire == 0:                      # varint
            value, i = varint(buf, i)
        elif wire == 2:                    # bytes (string, submensagem, packed)
            length, i = varint(buf, i)
            value = buf[i:i + length]
            i += length
        elif wire == 5:                    # 32 bits
            value, i = buf[i:i + 4], i + 4
        elif wire == 1:                    # 64 bits
            value, i = buf[i:i + 8], i + 8
        else:
            raise ValueError('wire type %d desconhecido' % wire)
        yield num, wire, value


def sprite_info(buf):
    """Dimensões do padrão e os sprite ids, do bloco 2.3."""
    ids, pw, ph, pd, layers = [], 1, 1, 1, 1
    for num, wire, value in fields(buf):
        if num == 5:
            if wire == 0:
                ids.append(value)
            else:                          # packed: vários varints seguidos
                j = 0
                while j < len(value):
                    x, j = varint(value, j)
                    ids.append(x)
        elif num == 1:
            pw = value
        elif num == 2:
            ph = value
        elif num == 3:
            pd = value
        elif num == 4:
            layers = value
    return ids, (pw, ph, pd, layers)


def parse_objects(data):
    objs = {}
    for num, _wire, value in fields(data):
        if num != 1:                       # só os objetos
            continue
        oid = name = sprites = info = None
        for f2, _w2, v2 in fields(value):
            if f2 == 1:
                oid = v2
            elif f2 == 4:
                name = bytes(v2).decode('utf-8', 'ignore')
            elif f2 == 2 and sprites is None:   # primeiro frame group basta
                for f3, _w3, v3 in fields(v2):
                    if f3 == 3:
                        sprites, info = sprite_info(v3)
        objs[oid] = dict(name=name, sprites=sprites, info=info)
    return objs


def find_appearances(assets_dir):
    hits = sorted(glob.glob(os.path.join(assets_dir, 'appearances-*.dat')))
    if not hits:
        raise SystemExit('Nenhum appearances-*.dat em %s' % assets_dir)
    return hits[0]


if __name__ == '__main__':
    config.require(config.ASSETS, 'os assets do client')
    config.ensure_work()
    objs = parse_objects(open(find_appearances(config.ASSETS), 'rb').read())
    json.dump(objs, open(config.OBJS, 'w', encoding='utf-8'))
    print('%d objetos' % len(objs))
    for probe in (3031, 7414, 3043, 3035, 5917):   # gold coin, bag, ...
        print(' ', probe, objs.get(probe))
