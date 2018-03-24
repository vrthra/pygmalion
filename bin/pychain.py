#!/usr/bin/env python3
import sys
import pychains.chain
import imp
if __name__ == "__main__":
    arg = sys.argv[1]
    times = int(sys.argv[2])
    _mod = imp.load_source('mymod', arg)
    results = []
    for i in range(times):
        e = pychains.chain.Chain()
        (a, r) = e.exec_argument(_mod.main)
        results.append(a)

    for i in results:
        print(i)
