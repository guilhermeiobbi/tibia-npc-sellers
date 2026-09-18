# Rebuild (quando o Tibia/Canary atualizar)

Fontes:
- Lojas dos NPCs: github.com/opentibiabr/canary -> data-otservbr-global/npc/*.lua (npcConfig.shop)
- Sprites: github.com/dudantas/tibia-client -> assets/ (appearances-*.dat, catalog-content.json, sprites-*.bmp.lzma)

Ordem (precisa de Python 3 + Pillow; os caminhos estão fixos em /home/claude, ajuste pro seu ambiente):
1. parse.py       lê os .lua e gera npcs_raw.json
2. appear.py      decodifica o appearances.dat (protobuf, sem schema) e gera objs.json (item id -> sprite ids)
3. build_data.py  recorta os sprites das sheets, monta atlas.webp e data.json (notas/grupos dos NPCs ficam no dict META)
4. build_html.py  injeta data.json + atlas no template.html -> index.html

Dica: só ~143 das ~4900 sheets são necessárias; use clone com --filter=blob:none e faça checkout só delas.
