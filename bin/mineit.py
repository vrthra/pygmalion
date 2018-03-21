#!/usr/bin/env python3
import pygmalion.miner as miner
import sys
import os
import pickle

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    defs = pickle.load(fin)

    grammarinfo = []
    for i, xins, g in miner.mine_grammar(defs):
        if os.getenv('DEBUG'):
            print(g, file=sys.stderr)
            print("Reconstitued:", file=sys.stderr)
            print(g.reconstitute(), file=sys.stderr)
        print(i, flush=True, file=sys.stderr)
        grammarinfo.append((i, xins, g))
    pickle.dump(grammarinfo, fout)
