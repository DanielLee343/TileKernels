import unittest
from overlap import overlap, inspect_trace
class Tests(unittest.TestCase):
 def test_union_intersection_without_double_count(self):
  x=overlap([(0,3),(2,5),(8,10)],[(1,4),(9,12)])
  self.assertEqual(x,{'a':7,'b':6,'intersection':4,'union':9})
 def test_disjoint_and_empty(self):
  self.assertEqual(overlap([(0,1)],[(1,2)])['intersection'],0)
  self.assertEqual(overlap([],[])['union'],0)
 def test_invalid_intervals_rejected(self):
  for x in [[(1,1)],[(2,1)],[(float('nan'),3)],[(True,3)]]:
   with self.assertRaises(ValueError): overlap(x,[])
 def test_task_events_are_not_pipe_activity(self):
  e={'ph':'X','name':'kernel','ts':'1','dur':'3','args':{'Task Type':'MIX_AIC','Task Id':11,'Physic Stream Id':61}}
  x=inspect_trace([e],11,61,'kernel')
  self.assertEqual(x['status'],'reference_insufficient')
  self.assertIn('AIC activity intervals',x['missing'])
 def test_wrong_ambiguous_or_missing_identity(self):
  e={'ph':'X','name':'kernel','ts':'1','dur':'3','args':{'Task Type':'MIX_AIC','Task Id':11,'Physic Stream Id':61}}
  for events,task in [([e,e],11),([e],12),([dict(e, args={})],11)]:
   self.assertEqual(inspect_trace(events,task,61,'kernel')['status'],'reference_insufficient')
 def test_real_pipe_schema_does_not_imply_synchronization(self):
  d={'profilingType':'op','schemaVersion':1,'traceEvents':[{'ph':'X','pid':'core0.veccore0','name':'MTE2','ts':0,'dur':2}]}
  x=inspect_trace(d,11,61,'kernel')
  self.assertEqual(x['schema'],'msopprof-op-v1')
  self.assertEqual(x['status'],'reference_insufficient')
if __name__=='__main__': unittest.main()
