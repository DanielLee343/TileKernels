import unittest
from decimal import Decimal
from calibrate import validate_registry,aggregate,aggregate_cases,calibrate,reference,summarize,check_holdout,segment_reference
class Tests(unittest.TestCase):
 def setUp(self):
  self.base={'device':'950PR/6/81/cann920','condition':'bf16-contiguous','formula':'contiguous_128_v1','response':'difference','cases':[{'id':'d','family':'fd','split':'development'},{'id':'c','family':'fc','split':'calibration'},{'id':'h','family':'fh','split':'holdout'},{'id':'p','family':'fp','split':'positive_control'},{'id':'n','family':'fn','split':'negative_control'}]}
 def test_split_leakage_and_duplicate(self):
  self.base['cases'][2]['family']='fc'
  with self.assertRaises(ValueError):validate_registry(self.base)
  self.base['cases'][2]['family']='fh'; self.base['cases'][2]['id']='c'
  with self.assertRaises(ValueError):validate_registry(self.base)
 def test_mixed_device_formula_and_duplicate_capture(self):
  cases=[{'device':'dev','formula':'contiguous_128_v1','capture_sha256':'a','w':'128','r':'128'},{'device':'other','formula':'contiguous_128_v1','capture_sha256':'b','w':'128','r':'128'}]
  with self.assertRaises(ValueError):aggregate(cases,'dev','contiguous_128_v1','difference')
  cases[1]['device']='dev';cases[1]['capture_sha256']='a'
  with self.assertRaises(ValueError):aggregate(cases,'dev','contiguous_128_v1','difference')
 def test_reference_offset(self):
  self.assertEqual(reference(1,128),256)
 def test_preregistered_segment_fixtures(self):
  for p,extra in ((0,0),(16,12288),(32,8192),(64,0)):
   segments=[(i*(8192+2*p),8192) for i in range(128)]
   self.assertEqual(segment_reference(segments,segments,segments[-1][0]+8192,0,'none_verified'),1048576+extra)
  hc=[(i*10272,10240) for i in range(512)]
  self.assertEqual(segment_reference(hc,hc,hc[-1][0]+10240,0,'none_verified'),5292032)
  self.assertEqual(reference(0,hc[-1][0]+10240),5259264)
 def test_segment_incomplete_overlap_bounds_and_external(self):
  args=([(0,4),(8,4)],[(0,4),(8,4)],12,0,'none_verified')
  self.assertEqual(segment_reference(*args),256)
  for seg,expected,size,offset,external in [([],[],12,0,'none_verified'), ([(0,4)],[(0,4),(8,4)],12,0,'none_verified'), ([(0,5),(4,4)],[(0,8)],12,0,'none_verified'), ([(0,13)],[(0,13)],12,0,'none_verified'), ([(0,4)],[(0,4)],12,0,'unknown'), ([(0,4)],[(0,4)],12,128,'none_verified')]:
   with self.assertRaises(ValueError):segment_reference(seg,expected,size,offset,external)
 def test_case_first_max_and_no_holdout_adjustment(self):
  cases={'x':[Decimal(1),Decimal(3),Decimal(2)],'y':[Decimal(2),Decimal(4),Decimal(1)]}
  self.assertEqual(calibrate(cases),Decimal(4))
 def test_zero_denominator_rejected(self):
  with self.assertRaises(ValueError):aggregate([{'device':'d','formula':'f','capture_sha256':'a','w':'1','r':'0'}],'d','f','ratio')
 def test_same_capture_cannot_appear_in_two_cases(self):
  row={'device':'d','formula':'f','capture_sha256':'abc','w':'128','r':'128'}
  with self.assertRaises(ValueError):aggregate_cases({'x':[row],'y':[row]},'d','f','difference')
 def test_retains_repeats_and_counts_case_failures(self):
  cases={'x':[Decimal(1),Decimal(3),Decimal(2)],'y':[Decimal(2),Decimal(4),Decimal(1)]}
  self.assertEqual(summarize(cases)['x']['repeats'],cases['x'])
  self.assertEqual(check_holdout(cases,Decimal(3))['false_positive_cases'],1)
 def test_cli_refuses_self_declared_numeric_cases(self):
  import tempfile,subprocess,json,hashlib,sys
  from pathlib import Path
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'registry.json'; self.base['formula']='per_verified_segment_128_v1'; self.base['measurements']={'fake':[0,0,0]}; self.base['segments']=[[0,128]]; p.write_text(json.dumps(self.base))
   h=hashlib.sha256(p.read_bytes()).hexdigest(); script=Path(__file__).with_name('calibrate.py')
   r=subprocess.run([sys.executable,'-B',str(script),str(p),'--freeze-sha256',h],capture_output=True,text=True,check=True)
   result=json.loads(r.stdout); self.assertEqual(result['status'],'reference_insufficient'); self.assertIsNone(result['boundary'])
if __name__=='__main__':unittest.main()
