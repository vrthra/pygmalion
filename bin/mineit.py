#!/usr/bin/env python3
import sys
sys.path.append('.')
import pygmalion.miner as miner
import os
import pickle
import resource
resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    defs = pickle.load(fin)

    grammarinfo = []
    for j, (i, xins, g) in enumerate(miner.mine_grammar(defs)):
        if os.getenv('DEBUG'):
            print(g, file=sys.stderr)
            print("Reconstitued:", file=sys.stderr)
            print(g.reconstitute(), file=sys.stderr)
        print("mine:", j, i, flush=True, file=sys.stderr)
        grammarinfo.append((i, xins, g))
    pickle.dump(grammarinfo, fout)
