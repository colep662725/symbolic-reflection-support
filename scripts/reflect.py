#!/usr/bin/env python3
"""Offline multilingual Tarot/I Ching reading companion for symbolic-reflection-support.

- No accounts, HTTP requests, external Python modules, or personal data storage.
- Original reflection prompts only: NOT classical divination texts or predictions.
- Randomness comes from draw.py's SystemRandom, or an explicit seeded demo.
- User-supplied symbols are never described as randomized.

Usage: python scripts/reflect.py [tarot|iching|card|hexagram|wizard] --help
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
from secrets import SystemRandom
import sys
from typing import Any

import draw

ROOT = Path(__file__).resolve().parents[1]
LANGS = ('en', 'zh', 'ja', 'fr', 'es', 'pt')
ORIENTATION = {
    'en': {'upright': 'upright', 'reversed': 'reversed'},
    'zh': {'upright': '正位', 'reversed': '逆位'},
    'ja': {'upright': '正位置', 'reversed': '逆位置'},
    'fr': {'upright': 'à l’endroit', 'reversed': 'renversée'},
    'es': {'upright': 'al derecho', 'reversed': 'invertida'},
    'pt': {'upright': 'posição normal', 'reversed': 'invertida'},
}
COPY = {
    'en': {'theme':'Reflection cue','question':'Question','source':'Source','no_change':'No moving lines',
           'moving':'Moving lines (bottom first)', 'original':'Original six coin sums (bottom to top)',
           'primary':'Primary hexagram','result':'Resulting hexagram','bounded':'Symbolic reflection, not a prediction'},
    'zh': {'theme':'反思主题','question':'自我提问','source':'来源','no_change':'没有动爻',
           'moving':'动爻（自下而上）','original':'六爻数值（自下而上）',
           'primary':'本卦','result':'变卦','bounded':'象征性反思，不是未来预测'},
    'ja': {'theme':'内省のテーマ','question':'問い','source':'出典','no_change':'変爻なし',
           'moving':'変爻（下から）','original':'六爻の値（下から）',
           'primary':'本卦','result':'変卦','bounded':'象徴的な内省であり予言ではありません'},
    'fr': {'theme':'Piste de réflexion','question':'Question','source':'Source','no_change':'Aucun trait mutant',
           'moving':'Traits mutants (depuis le bas)','original':'Six sommes (du bas vers le haut)',
           'primary':'Hexagramme initial','result':'Hexagramme résultant','bounded':'Réflexion symbolique, non prédiction'},
    'es': {'theme':'Tema para reflexionar','question':'Pregunta','source':'Origen','no_change':'Sin líneas móviles',
           'moving':'Líneas móviles (desde abajo)','original':'Seis sumas (desde abajo)',
           'primary':'Hexagrama inicial','result':'Hexagrama resultante','bounded':'Reflexión simbólica, no predicción'},
    'pt': {'theme':'Tema para reflexão','question':'Pergunta','source':'Origem','no_change':'Sem linhas móveis',
           'moving':'Linhas móveis (de baixo para cima)','original':'Seis somas (de baixo para cima)',
           'primary':'Hexagrama inicial','result':'Hexagrama resultante','bounded':'Reflexão simbólica, não previsão'},
}
QUESTIONS = {
    'en': 'Where does “{theme}” matter in your real life, and what small step is within your control?',
    'zh': '在现实生活中，哪里值得关注「{theme}」？你能自主采取哪一个小行动？',
    'ja': '日常生活で「{theme}」はどこに関わりますか？自分でできる小さな一歩は？',
    'fr': 'Où « {theme} » compte-t-il dans votre vie réelle ? Quel petit pas pouvez-vous choisir ?',
    'es': '¿Dónde importa «{theme}» en tu vida real? ¿Qué pequeño paso puedes elegir?',
    'pt': 'Onde «{theme}» importa na sua vida real? Que pequeno passo você pode escolher?',
}


def read_catalog(kind: str) -> tuple[dict[str, Any], str]:
    if kind not in ('tarot', 'iching'):
        raise ValueError('unknown catalog')
    b = (ROOT / 'data' / f'{kind}.json').read_bytes()
    return json.loads(b.decode('utf-8')), hashlib.sha256(b).hexdigest()


def wrap(outcome: dict[str, Any], source: str, seed: int | None = None) -> dict[str, Any]:
    return {
        'schema_version': draw.SCHEMA_VERSION,
        'tool_version': draw.VERSION,
        **outcome,
        'provenance': draw.provenance(outcome, source, seed),
    }


def card_entries(result: dict[str, Any], lang: str) -> tuple[list[dict[str, Any]], str]:
    catalog, fingerprint = read_catalog('tarot')
    by_id = {card['id']: card for card in catalog['cards']}
    entries = []
    for item in result['cards']:
        card = by_id[item['id']]
        orientation = item['orientation']
        theme = card['cues'][lang][orientation]
        entries.append({
            'id': item['id'], 'name': card['names'][lang], 'canonical_en': card['names']['en'],
            'orientation': orientation, 'orientation_label': ORIENTATION[lang][orientation],
            'theme': theme, 'reflection_question': QUESTIONS[lang].format(theme=theme),
        })
    return entries, fingerprint


def hex_entry(n: int, lang: str) -> dict[str, Any]:
    catalog, _ = read_catalog('iching')
    if not 1 <= n <= 64:
        raise ValueError('hexagram number must be from 1 to 64')
    h = catalog['hexagrams'][n - 1]
    theme = h['themes'][lang]
    return {
        'number': n, 'name_zh': h['name_zh'], 'pinyin': h['pinyin'],
        'theme': theme, 'reflection_question': QUESTIONS[lang].format(theme=theme),
    }


def reflect_tarot(outcome: dict[str, Any], source: str, lang: str,
                  seed: int | None = None) -> dict[str, Any]:
    raw = wrap(outcome, source, seed)
    entries, fingerprint = card_entries(raw, lang)
    return {'reading_version': '1.2.0', 'language': lang, 'type': 'tarot',
            'raw_result': raw, 'reading': {
                'cards': entries, 'catalog_sha256': fingerprint,
                'reading_kind': 'newly authored symbolic prompts, not predictions',
            }}


def reflect_iching(outcome: dict[str, Any], source: str, lang: str,
                    seed: int | None = None) -> dict[str, Any]:
    raw = wrap(outcome, source, seed)
    _, fingerprint = read_catalog('iching')
    primary = hex_entry(outcome['primary']['number'], lang)
    resulting = (hex_entry(outcome['resulting']['number'], lang)
                 if outcome['resulting'] is not None else None)
    return {'reading_version': '1.2.0', 'language': lang, 'type': 'iching',
            'raw_result': raw, 'reading': {
                'primary': primary, 'resulting': resulting,
                'moving_lines_from_bottom': outcome['moving_lines_from_bottom'],
                'catalog_sha256': fingerprint,
                'reading_kind': 'newly authored themes; no classical line texts',
            }}


def render_text(output: dict[str, Any]) -> str:
    lang = output['language']; words = COPY[lang]
    raw = output['raw_result']; reading = output['reading']
    lines = [f'Symbolic Reflection Support v{output["reading_version"]}',
             f'{words["source"]}: {raw["provenance"]["source"]}', '']
    if output['type'] == 'tarot':
        for i, card in enumerate(reading['cards'], 1):
            lines.extend([f'{i}. {card["name"]} ({card["orientation_label"]}) [{card["id"]}]',
                          f'   {words["theme"]}: {card["theme"]}',
                          f'   {words["question"]}: {card["reflection_question"]}', ''])
    else:
        primary=reading['primary']; resulting=reading['resulting']
        lines.extend([f'{words["primary"]}: #{primary["number"]} {primary["name_zh"]} ({primary["pinyin"]})',
                      f'{words["theme"]}: {primary["theme"]}',
                      f'{words["question"]}: {primary["reflection_question"]}', ''])
        if 'line_values_bottom_to_top' in raw:
            lines.append(f'{words["original"]}: {" ".join(map(str,raw["line_values_bottom_to_top"]))}')
        if resulting:
            lines.extend([f'{words["moving"]}: {", ".join(map(str,reading["moving_lines_from_bottom"]))}',
                          f'{words["result"]}: #{resulting["number"]} {resulting["name_zh"]} ({resulting["pinyin"]})',
                          f'{words["theme"]}: {resulting["theme"]}',
                          f'{words["question"]}: {resulting["reflection_question"]}'])
        else:
            lines.append(words['no_change'])
    lines.extend(['',words['bounded']])
    return '\n'.join(lines)


def from_args(args: argparse.Namespace) -> dict[str, Any]:
    lang=args.lang
    if args.method == 'tarot':
        if not 1 <= args.count <= 78:
            raise ValueError('card count must be between 1 and 78')
        rng = random.Random(args.seed) if args.seed is not None else SystemRandom()
        result = draw.draw_tarot(rng, args.count, args.reversals)
        return reflect_tarot(result, 'seeded_demo' if args.seed is not None else 'local_system_random', lang, args.seed)
    if args.method == 'card':
        catalog,_=read_catalog('tarot'); valid={r['id']:r for r in catalog['cards']}
        if args.id not in valid:raise ValueError('unknown card ID (valid: rws-00 through rws-77)')
        row=valid[args.id]
        outcome={'method':'user-supplied Tarot card for interpretation',
                 'cards':[{'id':args.id,'card':row['names']['en'],
                           'card_zh':row['names']['zh'],'orientation':args.orientation}]}
        return reflect_tarot(outcome,'user_supplied_card',lang)
    if args.method == 'iching':
        if args.seed is not None and (args.lines is not None or args.coins is not None):
            raise ValueError('--seed cannot be combined with supplied lines or coins')
        if args.lines is not None:
            outcome={'method':'user-supplied line values','line_values_bottom_to_top':args.lines,
                     **draw.decode_lines(args.lines)}
            source='user_supplied_lines'
        elif args.coins is not None:
            values=args.coins
            outcome=draw.decode_coin_rows([values[i*3:(i+1)*3] for i in range(6)],
                                         'user-supplied coin values, tails=2, heads=3')
            source='user_supplied_coins'
        else:
            rng=random.Random(args.seed) if args.seed is not None else SystemRandom()
            outcome=draw.cast_iching(rng)
            source='seeded_demo' if args.seed is not None else 'local_system_random'
        return reflect_iching(outcome,source,lang,args.seed)
    if args.method == 'hexagram':
        entry=hex_entry(args.number,lang)
        primary=next(draw.describe_hexagram(bits) for bits in itertools.product((0,1), repeat=6)
                     if draw.describe_hexagram(bits)['number']==args.number)
        outcome={'method':'user-supplied King Wen hexagram for interpretation',
                 'moving_lines_from_bottom':[], 'primary':primary, 'resulting':None}
        return reflect_iching(outcome,'user_supplied_hexagram',lang)
    raise ValueError('unsupported method')


def wizard(lang: str) -> None:
    """Human-facing opt-in interactive CLI; never use as an unattended agent call."""
    menus={
        'zh': '选择：1 今日塔罗  2 三张塔罗  3 三枚硬币起卦  4 指定塔罗牌  5 指定卦序  0 退出',
        'en': 'Choose: 1 daily card  2 three cards  3 three-coin I Ching  4 card by ID  5 hexagram by number  0 quit',
        'ja': '選択：1 一枚引き  2 三枚引き  3 易経  4 カード指定  5 卦番号  0 終了',
        'fr': 'Choix : 1 une carte  2 trois cartes  3 Yi Jing  4 carte par ID  5 hexagramme  0 quitter',
        'es': 'Elige: 1 una carta  2 tres cartas  3 I Ching  4 carta por ID  5 hexagrama  0 salir',
        'pt': 'Escolha: 1 uma carta  2 três cartas  3 I Ching  4 carta por ID  5 hexagrama  0 sair',
    }
    print(menus[lang])
    try:
        select=input('> ').strip()
        if select=='0':return
        if select in ('1','2'):
            args=argparse.Namespace(method='tarot',lang=lang,count=1 if select=='1' else 3,
                                    reversals=select=='2',seed=None)
        elif select=='3':
            args=argparse.Namespace(method='iching',lang=lang,seed=None,lines=None,coins=None)
        elif select=='4':
            val=input('Card ID (rws-00..rws-77): ').strip()
            orientation=input('Orientation (upright/reversed): ').strip()
            if orientation not in ('upright','reversed'):
                print('Invalid orientation',file=sys.stderr);raise SystemExit(2)
            args=argparse.Namespace(method='card',lang=lang,id=val,orientation=orientation)
        elif select=='5':
            val=int(input('King Wen number (1..64): ').strip())
            args=argparse.Namespace(method='hexagram',lang=lang,number=val)
        else:
            print('Unknown selection',file=sys.stderr);raise SystemExit(2)
        print('\n'+render_text(from_args(args)))
    except (EOFError,KeyboardInterrupt):
        print('\nCancelled',file=sys.stderr);raise SystemExit(2)
    except ValueError as exc:
        print('Input error: '+str(exc),file=sys.stderr);raise SystemExit(2)


def main() -> None:
    # Windows PowerShell 5.1 commonly launches subprocesses with cp936/cp1252.
    # The six-language JSON/text contract is UTF-8, even when stdout is piped.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest='method',required=True)
    tarot=subs.add_parser('tarot',help='Draw 1..78 actual random or seeded-demo Tarot cards')
    tarot.add_argument('--count',type=int,default=1)
    tarot.add_argument('--reversals',action='store_true')
    tarot.add_argument('--seed',type=int,help='DEMO/TESTS ONLY, never represent as unseeded draw')
    iching=subs.add_parser('iching',help='Three-coin draw or interpret supplied six lines')
    supplied=iching.add_mutually_exclusive_group()
    supplied.add_argument('--lines',type=int,nargs=6,choices=[6,7,8,9])
    supplied.add_argument('--coins',type=int,nargs=18,choices=[2,3])
    iching.add_argument('--seed',type=int,help='DEMO/TESTS ONLY')
    card=subs.add_parser('card',help='Interpret a user-selected card; not a draw')
    card.add_argument('--id',required=True,help='rws-00 through rws-77')
    card.add_argument('--orientation',choices=['upright','reversed'],default='upright')
    hexagram=subs.add_parser('hexagram',help='Interpret a user-selected hexagram; not a cast')
    hexagram.add_argument('--number',type=int,required=True)
    subs.add_parser('wizard',help='Human-operated one-step terminal menu; not for unattended agents')
    for cmd in (tarot,iching,card,hexagram,subs.choices['wizard']):
        cmd.add_argument('--lang',choices=LANGS,default='zh',help='en zh ja fr es pt')
        if cmd is not subs.choices['wizard']:
            cmd.add_argument('--json',action='store_true',help='Full machine-readable source+reading')
    args=parser.parse_args()
    if args.method=='wizard':
        if not sys.stdin.isatty():
            parser.error('wizard requires an interactive terminal; use other commands in agents/CI')
        wizard(args.lang);return
    try:
        output=from_args(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(output,ensure_ascii=False,indent=2) if args.json else render_text(output))

if __name__=='__main__':
    main()
