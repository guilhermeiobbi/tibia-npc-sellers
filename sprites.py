"""Leitura das sprite sheets do client (módulo, usado por build_data.py).

Cada sheet é um .bmp comprimido em LZMA cru, dentro de um envelope próprio da
CipSoft. O catalog-content.json diz qual sheet contém qual faixa de sprite ids,
então get_sprite(id) localiza a sheet, descomprime (uma vez, com cache) e
recorta o sprite na posição certa.
"""
import lzma
import json
import bisect
import struct
import io
import os

from PIL import Image

import config

# spritetype -> (largura, altura) de cada célula da sheet
SIZE = {0: (32, 32), 1: (32, 64), 2: (64, 32), 3: (64, 64)}

_sheets = {}   # nome do arquivo -> Image já descomprimida
_catalog = None


def load_sheet(filename):
    """Descomprime uma sheet .bmp.lzma e devolve a imagem RGBA."""
    b = open(os.path.join(config.ASSETS, filename), 'rb').read()
    # Envelope da CipSoft antes do stream LZMA: padding de zeros, 5 bytes de
    # cabeçalho, um tamanho em varint (bytes com o bit 8 ligado continuam).
    i = 0
    while b[i] == 0:
        i += 1
    i += 5
    while b[i] & 0x80:
        i += 1
    i += 1
    # Cabeçalho LZMA1 "alone": 1 byte de propriedades + 4 de dict_size + 8 do
    # tamanho descomprimido (que ignoramos) = 13 bytes.
    props = b[i]
    dict_size = struct.unpack('<I', b[i + 1:i + 5])[0]
    i += 13
    lc = props % 9
    rest = props // 9
    lp, pb = rest % 5, rest // 5
    dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{
        'id': lzma.FILTER_LZMA1, 'dict_size': dict_size,
        'lc': lc, 'lp': lp, 'pb': pb,
    }])
    return Image.open(io.BytesIO(dec.decompress(b[i:]))).convert('RGBA')


def catalog():
    """Entradas de sprite do catálogo, ordenadas por firstspriteid."""
    global _catalog
    if _catalog is None:
        path = os.path.join(config.ASSETS, 'catalog-content.json')
        entries = [e for e in json.load(open(path)) if e['type'] == 'sprite']
        entries.sort(key=lambda e: e['firstspriteid'])
        _catalog = (entries, [e['firstspriteid'] for e in entries])
    return _catalog


def get_sprite(sid):
    """Recorta o sprite sid da sheet que o contém."""
    entries, firsts = catalog()
    # busca binária: a sheet certa é a última cujo firstspriteid <= sid
    entry = entries[bisect.bisect_right(firsts, sid) - 1]
    if entry['file'] not in _sheets:
        _sheets[entry['file']] = load_sheet(entry['file'])
    sheet = _sheets[entry['file']]
    w, h = SIZE[entry['spritetype']]
    per_row = sheet.width // w
    k = sid - entry['firstspriteid']
    x, y = (k % per_row) * w, (k // per_row) * h
    return sheet.crop((x, y, x + w, y + h))


if __name__ == '__main__':
    # Sanity check visual: grava work/test.png com alguns sprites conhecidos.
    config.require(config.ASSETS, 'os assets do client')
    config.ensure_work()
    objs = {int(k): v for k, v in json.load(open(config.OBJS)).items()}
    probes = [7414, 3031, 3043, 5917, 3432, 3281]
    im = Image.new('RGBA', (32 * len(probes), 64), (60, 60, 60, 255))
    for n, i in enumerate(probes):
        s = get_sprite(objs[i]['sprites'][0])
        print(i, objs[i]['name'], s.size, s.getpixel((0, 0)))
        im.paste(s, (n * 32, 0), s)
    out = os.path.join(config.WORK, 'test.png')
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(out)
    print('->', out)
