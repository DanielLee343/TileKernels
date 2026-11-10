"""Locate containing intervals in sorted disjoint output ranges."""
from bisect import bisect_right

def locate(groups, starts, lo, hi):
    hits = []
    for i, (intervals, keys) in enumerate(zip(groups, starts)):
        j = bisect_right(keys, lo) - 1
        if j >= 0 and hi <= intervals[j][1]:
            hits.append(i)
    return hits
