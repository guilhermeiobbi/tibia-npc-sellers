# Onde vender?

Catálogo de NPCs compradores do Tibia. Você digita o nome de um item e vê quem
compra, por quanto, e quem paga mais.

**→ https://guilhermeiobbi.github.io/tibia-npc-sellers/**

1.701 itens, 142 NPCs, 4.275 combinações de preço — extraídos dos dados de NPC
do [OpenTibiaBR Canary](https://github.com/opentibiabr/canary), que espelha o
Tibia global.

## O que dá pra fazer

- **Buscar um item** e ver todos os compradores, com o melhor preço em dourado.
- **Abrir um NPC** e ver o catálogo dele inteiro, filtrável e ordenável — tanto
  o que ele compra quanto o que ele vende.
- **Favoritar itens** (★). Ficam salvos no navegador e a lista mostra os preços
  atualizados a cada rebuild.
- **Links diretos**: `#q=giant sword`, `#npc=Rashid`, `#fav`.

Os compradores de loot mais usados — Rashid, os Djinns, Esrik, Yasir, Grizzly
Adams — aparecem separados no topo da lista, com nota explicando onde ficam e
que quest cada um exige.

## Como o site é servido

O site inteiro é **um arquivo só**. O `index.html` carrega o catálogo embutido
numa tag `<script type="application/json">` e todos os sprites num atlas WebP
em base64 dentro do CSS. Sem servidor, sem API, sem uma requisição sequer
depois do load — é o que permite hospedar de graça no GitHub Pages e o que faz
a busca responder instantaneamente.

O custo é o tamanho: 1,2 MB no primeiro acesso (800 KB só de sprites). Para um
catálogo desse porte compensa; se ele crescer muito, vale separar o atlas num
arquivo próprio e deixar o navegador cachear.

O Pages serve a raiz do branch `main`. Push no `main` publica.

## Estrutura

```
index.html        o site gerado — é isso que o Pages publica
template.html     a fonte do site (HTML, CSS e JS), com dois marcadores
                  que o build preenche: /*ATLAS*/ e /*DATA*/
npc_meta.json     curadoria manual: quais NPCs vão em destaque e as notas
                  sobre localização e quests

config.py         todos os caminhos do pipeline, num lugar só
parse.py          etapa 1 — lojas dos NPCs
appear.py         etapa 2 — item id -> sprite ids
sprites.py        módulo — descomprime as sheets e recorta sprites
build_data.py     etapa 3 — junta tudo: data.json + atlas
build_html.py     etapa 4 — injeta no template -> index.html
```

`template.html` é a fonte e `index.html` é o produto. **Editar o `index.html`
direto funciona até o próximo rebuild sobrescrevê-lo** — mudanças de interface
vão no `template.html`.

## Rebuild (quando o Tibia/Canary atualizar)

Precisa de Python 3 e Pillow (`pip install -r requirements.txt`).

### 1. As fontes externas

```bash
# lojas dos NPCs (~100 MB com blob:none)
git clone --filter=blob:none https://github.com/opentibiabr/canary vendor/canary

# sprites e appearances do client
git clone --filter=blob:none https://github.com/dudantas/tibia-client vendor/tibia-client
```

O `--filter=blob:none` importa: o repositório do client tem ~4.900 sprite
sheets e o pipeline usa só ~143 delas. Com blobs sob demanda, o git baixa
apenas as que forem realmente lidas.

Se você já tem os repositórios em outro lugar, não precisa clonar de novo —
aponte as variáveis de ambiente:

```bash
export CANARY_DIR=~/src/canary
export CLIENT_DIR=~/src/tibia-client
```

### 2. O pipeline

```bash
python3 parse.py        # .lua        -> work/npcs_raw.json
python3 appear.py       # .dat        -> work/objs.json
python3 build_data.py   # + sprites   -> work/data.json, work/atlas.webp
python3 build_html.py   # + template  -> index.html
```

```
  canary/…/npc/*.lua ──▶ parse.py ─────▶ npcs_raw.json ─┐
                                                         │
  assets/appearances-*.dat ──▶ appear.py ──▶ objs.json ──┼─▶ build_data.py ──▶ data.json
                                                         │        ▲            atlas.webp
  assets/sprites-*.bmp.lzma ──▶ sprites.py (módulo) ─────┘        │                │
                                                                  │                │
  npc_meta.json ──────────────────────────────────────────────────┘                │
                                                                                   ▼
  template.html ──────────────────────────────────────────▶ build_html.py ──▶ index.html
```

Os intermediários ficam em `work/`, que é descartável e não vai pro git. Só o
`index.html` é versionado.

### 3. Publicar

```bash
git add index.html && git commit -m "Rebuild com dados de <data>" && git push
```

### Rodar só uma etapa

Cada script é independente e lê os intermediários do anterior. Mexeu só nas
notas do `npc_meta.json`? `build_data.py` + `build_html.py` bastam — não
precisa reprocessar os `.lua` nem os sprites.

`python3 sprites.py` gera um `work/test.png` com alguns sprites conhecidos,
útil pra conferir se o recorte continua alinhado depois de um update do client.

## Detalhes que vale saber

**Preços duplicados.** Um mesmo NPC pode aparecer em vários `.lua`. O
`build_data.py` funde por nome e, quando um item repete, fica o preço melhor
para o jogador: o maior quando o NPC compra, o menor quando vende.

**Itens são referenciados por índice.** O `data.json` guarda `[índice, preço]`
em vez de repetir o nome do item 4.275 vezes — e o mesmo índice é a posição do
sprite no atlas. Isso derruba o tamanho do arquivo, mas significa que **os
índices mudam a cada rebuild**: um item novo entra em ordem alfabética e
empurra todos os seguintes.

Por isso os favoritos guardam o **nome** do item, não o índice. Se guardassem o
índice, seus favoritos virariam itens aleatórios na primeira atualização.
Ficam em `localStorage`, na chave `ondevender.fav.v1`; itens que sumirem dos
dados são ignorados na hora de exibir, mas continuam salvos — se voltarem,
voltam sozinhos.

**O `appearances.dat` é protobuf sem schema.** O `.proto` não vem junto, então
o `appear.py` percorre os campos crus pelo número em vez de tentar
reconstruir o schema. Se um update do client mudar a numeração, é ali que
quebra.

## Créditos

Preços extraídos dos dados de NPC do projeto [OpenTibiaBR
Canary](https://github.com/opentibiabr/canary). Sprites e appearances do
[tibia-client](https://github.com/dudantas/tibia-client).

Confira no jogo antes de uma venda grande — o Canary espelha o Tibia global,
mas pode estar atrás de uma atualização.

Sprites, nomes e marcas são propriedade da CipSoft GmbH. Site de fã, sem
vínculo com a CipSoft.
