#!/usr/bin/env python3
import pygmalion.miner as miner
import pygmalion.grammar as g
import sys
import pickle

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    defs = pickle.load(fin)

    grammarinfo = []
    for i, xins, g in miner.mine_grammar(defs):
        if len(sys.argv) > 2:
            print(g)
            print("Reconstitued:")
            print(g.reconstitute())
        print(i, flush=True)
        grammarinfo.append((i, xins, g))
    pickle.dump(grammarinfo, fout)
