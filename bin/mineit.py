#!/usr/bin/env python3
import induce.miner as miner
import induce.grammar as g
import sys
import pickle

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    defs = pickle.load(fin)
    grammarinfo = []
    for i, ins, g in miner.mine_grammar(defs):
        if len(sys.argv) > 2:
            print(g)
            print()
            print(g.reconstitute())
        grammarinfo.append((i, ins, g))
    pickle.dump(grammarinfo, fout)
