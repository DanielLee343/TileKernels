"""Audit repeated JSON-absent/present profiles; this is not a correctness oracle."""
import csv
import json
import math
from pathlib import Path
import statistics
import sys

root = Path(sys.argv[1])
metrics = ['PipeUtilization','ArithmeticUtilization','L2Cache','Memory',
           'ResourceConflictRatio','MemoryL0','MemoryUB']
cases = ['bf16-m1-n576-k7168','bf16-m1-n32768-k512']
report = {}
for case in cases:
    batches = []
    for index, arm in enumerate('ABBAAB', 1):
        folder = root/'runs'/f'{case}-{index}-{arm}'/case
        result = json.loads((folder/'result.json').read_text())
        before = json.loads((folder/'prepare.json').read_text())
        after = json.loads((folder/'profile.json').read_text())
        assert result['status'] == before['status'] == after['status'] == 'passed'
        basic = list((folder/'profile').rglob('OpBasicInfo.csv'))
        assert len(basic) == 1
        batches.append((arm, folder, result, before, after, basic[0].parent))
    for key in ('input_a_sha256','input_b_sha256','reference_sha256','output_sha256'):
        assert len({x[3][key] for x in batches} | {x[4][key] for x in batches}) == 1, key
    assert len({x[2]['capture']['binary_sha256'] for x in batches}) == 1
    assert len({x[2]['capture']['op_type'] for x in batches}) == 1
    output = {'op_type':batches[0][2]['capture']['op_type'], 'metrics':{},'issues':[]}
    for metric in metrics:
        records=[]
        for arm, folder, result, before, after, directory in batches:
            with (directory/(metric+'.csv')).open(newline='') as f:
                reader=csv.DictReader(f); rows=list(reader); fields=reader.fieldnames
            keys=[(r['block_id'],r['sub_block_id']) for r in rows]
            assert len(keys)==len(set(keys))
            records.append((arm, fields, {k:r for k,r in zip(keys,rows)}))
        if any(r[1]!=records[0][1] for r in records[1:]):
            output['issues'].append(metric+': columns differ'); continue
        if any(set(r[2])!=set(records[0][2]) for r in records[1:]):
            output['issues'].append(metric+': block/role keys differ'); continue
        fields={}
        roles=sorted({key[1] for key in records[0][2]})
        for role in roles:
            keys=sorted(k for k in records[0][2] if k[1]==role)
            for col in records[0][1]:
                if col in ('','block_id','sub_block_id'):continue
                name=role+'/'+col
                patterns=[]; totals=[]; per_block=[]
                for arm, _, rows in records:
                    vals=[]; pattern=[]; block_values={}
                    for k in keys:
                        raw=rows[k].get(col,'')
                        try:
                            val=float(raw); available=math.isfinite(val)
                        except (ValueError,TypeError):available=False;val=0
                        pattern.append(available)
                        if available:vals.append(val);block_values[k]=val
                    patterns.append(pattern)
                    totals.append(statistics.mean(vals) if vals else None)
                    per_block.append(block_values)
                if any(p!=patterns[0] for p in patterns[1:]):
                    output['issues'].append(metric+': '+name+' availability differs')
                if all(x is None for x in totals):continue
                if any(x is None for x in totals):
                    output['issues'].append(metric+': '+name+' entirely unavailable in some run');continue
                a=[totals[i] for i in (0,3,4)];b=[totals[i] for i in (1,2,5)]
                meda=statistics.median(a);medb=statistics.median(b)
                scale=max(abs(meda),abs(medb))
                differing_blocks=0
                for key in keys:
                    if all(key in row for row in per_block):
                        av=[per_block[i][key] for i in (0,3,4)]
                        bv=[per_block[i][key] for i in (1,2,5)]
                        differing_blocks += statistics.median(av)!=statistics.median(bv)
                fields[name]={'A':a,'B':b,'median_relative_difference':abs(meda-medb)/scale if scale else 0,
                              'blocks_with_different_medians':differing_blocks,'blocks':len(keys),
                              'within_range_A':max(a)-min(a),'within_range_B':max(b)-min(b),
                              'median_difference':abs(meda-medb)}
        output['metrics'][metric]=fields
    report[case]=output
(root/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
for case,v in report.items():
    print(case,v['op_type'],'issues',len(v['issues']), 'available role-fields',sum(len(x) for x in v['metrics'].values()))
    for issue in v['issues'][:20]:print(' ISSUE',issue)
    for metric,fields in v['metrics'].items():
        print(' ',metric,'fields',len(fields),'varying',sum(x['median_relative_difference']>1e-9 for x in fields.values()),
              'beyond-either-within-range',sum(x['median_difference']>max(x['within_range_A'],x['within_range_B'])+1e-9 for x in fields.values()))
        if metric in ('ArithmeticUtilization','Memory'):
            for key,x in fields.items():
                if any(s in key for s in ('instructions','datas(KB)','instr_number')):
                    print('   ',key,'A',x['A'],'B',x['B'])
