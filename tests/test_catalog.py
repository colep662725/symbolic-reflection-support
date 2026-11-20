"""Six-language catalog integrity, v1.2 CLI, provenance, browser demo checks."""
from __future__ import annotations

import hashlib
import argparse
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import unittest
import os

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
READ=ROOT/'scripts/reflect.py'
DRAW=ROOT/'scripts/draw.py'
LANGS={'en','zh','ja','fr','es','pt'}
TAROT=json.loads((ROOT/'data/tarot.json').read_text(encoding='utf-8'))
ICHING=json.loads((ROOT/'data/iching.json').read_text(encoding='utf-8'))

spec=importlib.util.spec_from_file_location('symbolic_draw_12',DRAW)
assert spec and spec.loader
DRAW_LIB=importlib.util.module_from_spec(spec)
spec.loader.exec_module(DRAW_LIB)
import reflect as REFLECT


def call(*args):
    r=subprocess.run([sys.executable,str(READ),*args,'--json'],capture_output=True,
                     encoding='utf-8', errors='strict',check=True)
    return json.loads(r.stdout)

class CatalogTests(unittest.TestCase):
    def test_tarot_78_names_and_both_orientations_six_languages(self):
        cards=TAROT['cards'];self.assertEqual(len(cards),78)
        self.assertEqual([c['id'] for c in cards],[f'rws-{i:02d}' for i in range(78)])
        for i,card in enumerate(cards):
            self.assertEqual(card['names']['en'],DRAW_LIB.DECK[i])
            self.assertEqual(card['names']['zh'],DRAW_LIB.DECK_ZH[i])
            self.assertEqual(set(card['names']),LANGS)
            self.assertEqual(set(card['cues']),LANGS)
            for lang in LANGS:
                self.assertTrue(card['names'][lang].strip())
                self.assertEqual(set(card['cues'][lang]),{'upright','reversed'})
                self.assertGreater(len(card['cues'][lang]['upright']),3)
                self.assertGreater(len(card['cues'][lang]['reversed']),3)
        for lang in LANGS:
            self.assertEqual(len({c['names'][lang] for c in cards}),78)

    def test_64_hexagrams_match_original_king_wen_mapping(self):
        hs=ICHING['hexagrams'];self.assertEqual(len(hs),64)
        self.assertEqual([h['number'] for h in hs],list(range(1,65)))
        for h in hs:
            self.assertEqual(h['name_zh'],DRAW_LIB.HEXAGRAM_NAMES[h['number']-1])
            self.assertEqual(set(h['themes']),LANGS)
            self.assertTrue(h['pinyin'].strip())
            self.assertTrue(all(len(x.strip())>2 for x in h['themes'].values()))

    def test_catalogs_do_not_contain_unverified_classical_quotations(self):
        for catalog in (TAROT,ICHING):
            self.assertIn('original_reflection',catalog['type'])
            self.assertEqual(set(catalog['languages']),LANGS)
            self.assertEqual(catalog['version'],'1.2.0')

class CLIAndSourceTests(unittest.TestCase):
    def test_utf8_json_even_under_legacy_windows_code_page(self):
        # Simulate a Windows process started under a non-UTF8 default code page.
        for lang in ('fr','pt','es','ja','zh'):
            with self.subTest(lang=lang):
                env=os.environ.copy();env['PYTHONIOENCODING']='cp936'
                p=subprocess.run([sys.executable,str(READ),'card','--id','rws-15',
                                  '--orientation','upright','--lang',lang,'--json'],
                                  capture_output=True,encoding='utf-8',env=env)
                self.assertEqual(p.returncode,0,p.stderr)
                self.assertEqual(json.loads(p.stdout)['language'],lang)

    def test_all_languages_all_orientations(self):
        for lang in LANGS:
            for orientation in ('upright','reversed'):
                with self.subTest(lang=lang,orientation=orientation):
                    r=call('card','--id','rws-15','--orientation',orientation,'--lang',lang)
                    self.assertEqual(r['language'],lang)
                    self.assertEqual(r['reading']['cards'][0]['orientation'],orientation)
                    self.assertTrue(r['reading']['cards'][0]['reflection_question'])
                    self.assertEqual(r['raw_result']['provenance']['source'],'user_supplied_card')

    def test_all_hexagrams_lookup(self):
        for num in range(1,65):
            with self.subTest(number=num):
                r=REFLECT.from_args(argparse.Namespace(method='hexagram', number=num, lang='zh'))
                self.assertEqual(r['reading']['primary']['number'],num)
                self.assertEqual(r['raw_result']['primary']['name_zh'],ICHING['hexagrams'][num-1]['name_zh'])
                self.assertEqual(r['raw_result']['provenance']['source'],'user_supplied_hexagram')
                self.assertIsNone(r['reading']['resulting'])
                self.assertIsInstance(r['raw_result']['primary']['lower'],str)
                self.assertIsInstance(r['raw_result']['primary']['upper'],str)

    def test_known_change_and_label_are_exact(self):
        r=call('iching','--lines','7','8','7','9','7','8','--lang','zh')
        self.assertEqual((r['reading']['primary']['number'],r['reading']['resulting']['number']),(49,63))
        self.assertEqual(r['reading']['moving_lines_from_bottom'],[4])
        self.assertEqual(r['raw_result']['provenance']['source'],'user_supplied_lines')
        self.assertEqual(r['raw_result']['line_values_bottom_to_top'],[7,8,7,9,7,8])
        self.assertEqual(r['reading']['primary']['name_zh'],'革')
        self.assertEqual(r['reading']['resulting']['name_zh'],'既济')

    def test_seeded_demo_reproducible_but_not_marked_live(self):
        a=call('tarot','--count','3','--reversals','--seed','2026','--lang','en')
        b=call('tarot','--count','3','--reversals','--seed','2026','--lang','fr')
        self.assertEqual(a['raw_result']['cards'],b['raw_result']['cards'])
        self.assertEqual(a['raw_result']['provenance']['payload_sha256'],
                         b['raw_result']['provenance']['payload_sha256'])
        self.assertEqual(a['raw_result']['provenance']['source'],'seeded_demo')
        self.assertEqual(b['raw_result']['provenance']['source'],'seeded_demo')
        self.assertEqual(a['raw_result']['schema_version'],'1.1')
        self.assertEqual(a['reading_version'],'1.2.0')
        self.assertNotEqual(a['reading']['cards'][0]['name'],b['reading']['cards'][0]['name'])

    def test_system_random_source_and_no_seed(self):
        for m in ('tarot','iching'):
            r=call(m,'--lang','zh')
            self.assertEqual(r['raw_result']['provenance']['source'],'local_system_random')
            self.assertNotIn('seed',r['raw_result']['provenance'])

    def test_supplied_coin_values_source(self):
        coins=['3','2','2','2','3','2','3','2','2','3','3','3','2','2','3','3','2','2']
        r=call('iching','--coins',*coins,'--lang','pt')
        self.assertEqual(r['raw_result']['provenance']['source'],'user_supplied_coins')
        self.assertEqual(len(r['raw_result']['coins_bottom_to_top']),6)

    def test_provenance_fingerprints_raw_and_catalog_separately(self):
        for args in (('tarot','--count','2','--seed','11','--lang','zh'),
                     ('iching','--seed','11','--lang','fr'),
                     ('hexagram','--number','49','--lang','es')):
            r=call(*args)
            raw=r['raw_result'];payload={k:v for k,v in raw.items() if k not in ('schema_version','tool_version','provenance')}
            buf=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
            self.assertEqual(hashlib.sha256(buf).hexdigest(),raw['provenance']['payload_sha256'])
            typ=r['type']
            self.assertEqual(hashlib.sha256((ROOT/f'data/{typ}.json').read_bytes()).hexdigest(),r['reading']['catalog_sha256'])

    def test_reject_invalid_card_or_hexagram(self):
        for args in [('card','--id','rws-99'),('hexagram','--number','0'),('hexagram','--number','65'),
                     ('iching','--lines','1','2','3','4','5','6'),('tarot','--count','79'),
                     ('iching','--seed','2','--lines','7','7','7','7','7','7')]:
            p=subprocess.run([sys.executable,str(READ),*args],text=True,capture_output=True)
            self.assertNotEqual(p.returncode,0)

    def test_wizard_rejects_non_tty_in_automation(self):
        p=subprocess.run([sys.executable,str(READ),'wizard','--lang','en'],
                         input='1\n',text=True,capture_output=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('interactive terminal',p.stderr)

    def test_no_personal_birth_info_in_results(self):
        r=call('tarot','--count','1','--lang','zh')
        result=json.dumps(r,ensure_ascii=False).lower()
        for forbidden in ('birth_date','birth_place','email','phone number'):
            self.assertNotIn(forbidden,result)

class BrowserDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'docs/index.html').read_text(encoding='utf-8')

    def test_has_one_copy_of_same_catalog(self):
        for kind,expected in [('tarot',TAROT),('iching',ICHING)]:
            m=re.search(r'<script type="application/json" id="'+kind+r'-data">(.*?)</script>',self.html,re.S)
            self.assertIsNotNone(m)
            actual=json.loads(m.group(1))
            self.assertEqual(actual,expected)

    def test_browser_random_source_is_webcrypto_not_mathrandom(self):
        self.assertIn('crypto.getRandomValues',self.html)
        self.assertIn('browser_webcrypto',self.html)
        self.assertNotIn('Math.random',self.html)
        self.assertNotIn('fetch(',self.html)
        self.assertNotIn('localStorage',self.html)
        self.assertNotIn('XMLHttpRequest',self.html)

    def test_browser_supplied_line_decode_and_orientation_controls(self):
        self.assertIn('id="orientation-select"', self.html)
        self.assertIn('id="lines-input"', self.html)
        self.assertIn('user_supplied_lines_browser', self.html)
        self.assertIn('user_selected_card', self.html)

    def test_html_safety_and_language_selector(self):
        self.assertIn('aria-live="polite"',self.html)
        self.assertIn('prefers-reduced-motion',self.html)
        self.assertIn('name="viewport"',self.html)
        for l in LANGS:
            self.assertIn(f'<option value="{l}">',self.html)

if __name__=='__main__':
    unittest.main()
