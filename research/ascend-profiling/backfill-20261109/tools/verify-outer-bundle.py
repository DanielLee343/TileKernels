"""Independently verify a transferred outer archive and every inner member."""
import hashlib,subprocess,sys,tarfile,tempfile
from pathlib import Path
bundle=Path(sys.argv[1]).resolve(strict=True);expected=sys.argv[2]
h=hashlib.sha256()
with bundle.open('rb') as f:
 for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
assert h.hexdigest()==expected
with tempfile.TemporaryDirectory(prefix='puma-bundle-verify-') as d:
 root=Path(d).resolve()
 with tarfile.open(bundle,'r:gz') as t:
  for x in t:
   assert (x.isfile() or x.isdir()) and not x.issym() and not x.islnk()
   assert not Path(x.name).is_absolute() and '..' not in Path(x.name).parts
   assert (root/x.name).resolve().is_relative_to(root)
  t.extractall(root,filter='data')
 dirs=[x for x in root.iterdir() if x.is_dir()];assert len(dirs)==1
 subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('verify-archive.py')),str(dirs[0])],check=True)
print('RECEIVED_BUNDLE_VERIFIED',expected)
