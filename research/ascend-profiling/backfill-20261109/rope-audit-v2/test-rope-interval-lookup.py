"""Check binary interval lookup matches the exhaustive address containment test."""
import bisect, random
from rope_interval_lookup import locate

def brute(groups,lo,hi):
 return [i for i,intervals in enumerate(groups) if any(a<=lo and hi<=b for a,b in intervals)]
rng=random.Random(2311)
sets=[[],[(10,20)],[(0,4),(8,15),(20,25)],[(2,8),(10,20)]]
groups=[sets[0],sets[1],sets[2],sets[3]];starts=[[a for a,_ in items] for items in groups]
for lo in range(-2,30):
 for hi in range(lo+1,32):assert locate(groups,starts,lo,hi)==brute(groups,lo,hi),(lo,hi)
for _ in range(10000):
 generated=[]
 for _ in range(rng.randrange(1,5)):
  pos=rng.randrange(0,5);items=[]
  for _ in range(rng.randrange(0,16)):
   pos+=rng.randrange(1,5);end=pos+rng.randrange(1,8);items.append((pos,end));pos=end
  generated.append(items)
 lo=rng.randrange(0,120);hi=lo+rng.randrange(1,20);assert locate(generated,[[x for x,_ in seq] for seq in generated],lo,hi)==brute(generated,lo,hi)
print('PASS exhaustive boundaries and 10000 randomized multi-output containment checks')
