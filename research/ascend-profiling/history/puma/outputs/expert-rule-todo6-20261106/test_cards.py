import unittest
from cards import evaluate, p05_formula

class CardsTest(unittest.TestCase):
    def test_unknown_identity_is_insufficient(self):
        self.assertEqual(evaluate({'card':'P05'})['status'], 'reference_insufficient')
    def test_other_platform_is_rejected(self):
        self.assertEqual(evaluate({'card':'P05','platform':'910B'})['status'], 'not_applicable')
    def test_other_cards_have_no_threshold(self):
        self.assertEqual(evaluate({'card':'P03'})['status'], 'reference_insufficient')
    def test_p05_exact_scope_and_boundary(self):
        import json
        with open('fixtures/p05.json',encoding='utf8') as f: d=json.load(f)
        self.assertEqual(evaluate(d)['status'],'reference_insufficient')
        self.assertEqual(p05_formula(d)['ratio'], 1)
        d['rows'][0]['kb']='0.250'
        self.assertEqual(evaluate(d)['status'],'reference_insufficient')
        self.assertEqual(p05_formula(d)['excess_bytes'],128)
        d['cann']='9.2.0'
        self.assertEqual(evaluate(d)['status'],'not_applicable')
    def test_p05_self_declared_hash_and_tamper_never_admit(self):
        import json, hashlib, tempfile, subprocess, sys
        from pathlib import Path
        d=json.loads(Path('fixtures/p05.json').read_text(encoding='utf8'))
        d['source_sha256']=hashlib.sha256(b'claimed source').hexdigest()
        d['binary_sha256']=hashlib.sha256(b'claimed binary').hexdigest()
        d['capture_binding_sha256']=hashlib.sha256(b'claimed binding').hexdigest()
        self.assertEqual(evaluate(d)['status'], 'reference_insufficient')
        d['rows'][0]['kb']='1000'
        self.assertEqual(evaluate(d)['status'], 'reference_insufficient')
        del d['rows']
        self.assertEqual(evaluate(d)['status'], 'reference_insufficient')
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source.bin'
            source.write_bytes(b'original')
            d['binary_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
            d['binary_path']=str(source)
            inp=Path(tmp)/'input.json'
            inp.write_text(json.dumps(d),encoding='utf8')
            source.write_bytes(b'tampered')
            out=subprocess.run([sys.executable,'-B','cards.py',str(inp)],capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(out.stdout)['status'],'reference_insufficient')
    def test_p04_only_frozen_source(self):
        import json
        with open('fixtures/bh.json',encoding='utf8') as f: d=json.load(f)
        r=evaluate(d)
        self.assertEqual(r['measurement']['requested_bytes'],4194304)
        self.assertEqual(r['measurement']['repeat_rate'],0)
        d['source_sha256']='unknown'
        self.assertEqual(evaluate(d)['status'],'reference_insufficient')

if __name__ == '__main__': unittest.main()
