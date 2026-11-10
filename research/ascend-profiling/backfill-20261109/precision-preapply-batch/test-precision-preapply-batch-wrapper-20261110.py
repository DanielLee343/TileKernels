"""Check reference failure is recorded and unrelated exceptions propagate."""
import ast,traceback
from pathlib import Path
p=Path(__file__).with_name('precision-preapply-batch-wrapper-20261110.py');tree=ast.parse(p.read_text(encoding='utf-8-sig'));node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='capture_reference');module=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]))
def make(fn):
 ns={'original':fn,'failures':[],'traceback':traceback};exec(compile(module,str(p),'exec'),ns);return ns
ns=make(lambda: [{'passed':True}]);assert ns['capture_reference']()==[{'passed':True}] and not ns['failures']
def mismatch():raise AssertionError('original reference mismatch')
ns=make(mismatch);x=ns['capture_reference']();assert x[0]['passed'] is False and 'original reference mismatch' in x[0]['error'] and len(ns['failures'])==1
def unexpected():raise ValueError('unexpected failure')
ns=make(unexpected)
try:ns['capture_reference']()
except ValueError:pass
else:raise AssertionError('unexpected exceptions must propagate')
print('PASS original CPU mismatch retained; unexpected exceptions propagate')
