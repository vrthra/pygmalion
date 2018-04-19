#!/usr/bin/env python3
import sys
sys.path.append('.')
import pychains.chain
import imp
import time
import taintedstr
import pickle
if __name__ == "__main__":
    arg = sys.argv[1]
    times = int(sys.argv[2])
    fn = sys.argv[3]
    _mod = imp.load_source('mymod', arg)
    results = []
    start = time.perf_counter()
    with open(fn, 'wb') as f:
        for i in range(times):
            e = pychains.chain.Chain()
            (a, r) = e.exec_argument(_mod.main)
            t = time.perf_counter() - start
            print(i, t, repr(a), flush=True)
            pickle.dump((a, t), file=f)

