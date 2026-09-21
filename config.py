"""Caminhos do pipeline, num lugar só.

Os defaults assumem que as fontes externas foram clonadas em vendor/ dentro
do próprio repositório. Qualquer um deles pode ser trocado por variável de
ambiente, sem editar os scripts:

    CANARY_DIR=~/src/canary CLIENT_DIR=~/src/tibia-client python3 parse.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def _path(env, *parts):
    """Valor de $env, ou ROOT/parts quando a variável não estiver definida."""
    return os.path.abspath(os.environ.get(env) or os.path.join(ROOT, *parts))


# --- entradas: clones das fontes externas (ver README)
CANARY = _path('CANARY_DIR', 'vendor', 'canary')
CLIENT = _path('CLIENT_DIR', 'vendor', 'tibia-client')
NPC_LUA = os.path.join(CANARY, 'data-otservbr-global', 'npc')
ASSETS = os.path.join(CLIENT, 'assets')

# --- intermediários: descartáveis, refeitos a cada rebuild
WORK = _path('WORK_DIR', 'work')
NPCS_RAW = os.path.join(WORK, 'npcs_raw.json')
OBJS = os.path.join(WORK, 'objs.json')
DATA = os.path.join(WORK, 'data.json')
ATLAS_PNG = os.path.join(WORK, 'atlas.png')
ATLAS_WEBP = os.path.join(WORK, 'atlas.webp')

# --- site: fonte e resultado final
TEMPLATE = os.path.join(ROOT, 'template.html')
NPC_META = os.path.join(ROOT, 'npc_meta.json')
INDEX = _path('INDEX_OUT', 'index.html')


def ensure_work():
    os.makedirs(WORK, exist_ok=True)


def require(path, what):
    """Erro com instrução em vez de traceback quando falta uma fonte externa."""
    if not os.path.exists(path):
        raise SystemExit(
            'Não encontrei %s em:\n  %s\n'
            'Clone a fonte em vendor/ ou aponte a variável de ambiente '
            'correspondente (ver README).' % (what, path))
    return path
