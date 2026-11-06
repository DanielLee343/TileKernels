import json, hashlib, importlib.util, sys
from pathlib import Path
from decimal import Decimal, InvalidOperation
ROOT=Path(__file__).resolve().parents[2]
BH='cdd36cdd76a08b92b8aab1136461467e41164617b031aa7ef44556fa6b01886b'
BUILD='884ac969494a186a9c63ac45c4c39ad7289b3215'
def result(status, reason, **kw): return dict(status=status, reason=reason, **kw)
def p05_formula(d):
    """Pure arithmetic on supplied values; does not establish their provenance."""
    o,L=d.get('offset'),d.get('logical_bytes')
    if type(o) is not int or not 0<=o<128 or type(L) is not int or L<=0: raise ValueError('invalid output address offset or size')
    rows=d.get('rows')
    if not isinstance(rows,list) or len(rows)!=56: raise ValueError('56 rows required')
    try:
        seen=set(); W=0
        for row in rows:
            b=row['block']; sub=row['sub']; x=Decimal(str(row['kb']))*1024
            if type(b) is not int or not 0<=b<56 or sub!='vector0' or b in seen or not x.is_finite() or x<0 or x%128: raise ValueError('invalid or duplicate rows')
            seen.add(b); W+=int(x)
    except (KeyError,TypeError,InvalidOperation) as e: raise ValueError('invalid rows') from e
    R=128*((o+L+127)//128)
    return {'W_bytes':W,'R_bytes':R,'ratio':W/R,'excess_bytes':max(0,W-R)}
def evaluate(d):
    card=d.get('card')
    if card not in [f'P{i:02}' for i in range(1,11)]: return result('reference_insufficient','unknown card')
    if d.get('platform') not in (None,'950PR'): return result('not_applicable','platform mismatch')
    if card=='P04':
        if d.get('platform')!='950PR' or d.get('source_sha256')!=BH or d.get('scope')!='frozen-bh-input': return result('reference_insufficient','B-H identity or scope missing')
        p=ROOT/'outputs/expert-rule-todo4-20261106/expert-bh/input.json'
        if hashlib.sha256(p.read_bytes()).hexdigest()!=BH: return result('reference_insufficient','frozen input hash mismatch')
        spec=importlib.util.spec_from_file_location('repeat_metric',ROOT/'outputs/expert-rule-todo4-20261106/repeat_metric.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        m=mod.calculate(json.loads(p.read_text(encoding='utf-8-sig')))['overall']
        return result('measurement_only','B-H input only; no performance threshold',measurement=m)
    if card!='P05': return result('reference_insufficient','no independently calibrated threshold')
    expected={'platform':'950PR','pci':'0000:0D:00.0','cann':'9.2.1','collector':'26.2.0','build':BUILD,'profile':'Default','replay':'kernel','clear_l2':True,'app_warmup':5,'tool_warmup':5,'target_calls':1,'kernel_type':'AIV','blocks':56,'output_count':1,'output_independent':True,'output_contiguous':True,'output_complete':True}
    for k,v in expected.items():
        if k not in d or d[k] is None: return result('reference_insufficient',f'missing {k}')
        if type(d[k]) is not type(v) or d[k]!=v: return result('not_applicable',f'mismatch {k}')
    return result('reference_insufficient','no verified per-capture executable binding; self-declared hashes cannot establish identity')
def main():
    if len(sys.argv)!=2: raise SystemExit('usage: python cards.py INPUT.json')
    try: print(json.dumps(evaluate(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))),ensure_ascii=False,indent=2))
    except (OSError,ValueError,TypeError) as e: print(str(e),file=sys.stderr); raise SystemExit(2)
if __name__=='__main__': main()
