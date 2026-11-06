import importlib.util, unittest
from pathlib import Path
P=Path(__file__).parent
class PilotTest(unittest.TestCase):
 def test_two_arms_and_no_repeat_scheduler(self):
  spec=importlib.util.spec_from_file_location('runner',P/'runner.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  self.assertEqual(m.CASESET,('I0','I16'))
  self.assertEqual(m.strides('I0'),(4096,4096));self.assertEqual(m.strides('I16'),(4112,4096))
  with self.assertRaises(ValueError):m.strides('D1')
 def test_wrapper_contract(self):
  s=(P/'rms_wrapper.py').read_text(encoding='utf8')
  self.assertIn("'I0': (128,4096,4096)",s);self.assertIn("'I16': (128,4096,4112)",s)
  self.assertIn("out_stride = 4096 if case in ('I0', 'I16')",s)
 def test_no_extra_phases(self):
  s=(P/'runner.py').read_text(encoding='utf8');self.assertNotIn('schedule(',s);self.assertNotIn("choices=['gate','default']",s)
if __name__=='__main__':unittest.main()
