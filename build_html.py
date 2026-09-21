"""Etapa 4 — injeta dados e atlas no template e gera o index.html.

O site inteiro cabe num arquivo só: o atlas vira data URI no CSS e o data.json
vai embutido numa tag <script type="application/json">. Sem requisições extras,
sem servidor — é o que permite hospedar direto no GitHub Pages.

Saída: index.html (na raiz do repositório)
"""
import base64
import os

import config

ATLAS_RULE = '.spr{background-image:url(data:image/webp;base64,%s)}'


def build(template, data, atlas_bytes):
    for marker in ('/*ATLAS*/', '/*DATA*/'):
        if template.count(marker) != 1:
            raise SystemExit('template.html deveria ter exatamente um %s' % marker)
    atlas = ATLAS_RULE % base64.b64encode(atlas_bytes).decode()
    # "</" escapado: um "</script>" dentro dos dados fecharia a tag antes da hora
    return template.replace('/*ATLAS*/', atlas).replace('/*DATA*/', data.replace('</', '<\\/'))


if __name__ == '__main__':
    config.require(config.DATA, 'o data.json (rode build_data.py antes)')
    html = build(
        open(config.TEMPLATE, encoding='utf-8').read(),
        open(config.DATA, encoding='utf-8').read(),
        open(config.ATLAS_WEBP, 'rb').read(),
    )
    os.makedirs(os.path.dirname(config.INDEX) or '.', exist_ok=True)
    open(config.INDEX, 'w', encoding='utf-8').write(html)
    print('%s — %d KB' % (config.INDEX, len(html) // 1024))
