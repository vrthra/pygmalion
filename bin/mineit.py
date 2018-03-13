#!/usr/bin/env python3
import induce.miner as miner
import induce.grammar as g
import sys
import pickle

if __name__ == "__main__":
    defs = pickle.load(open(sys.argv[1], "rb" ))
    grammarinfo = []
    for i,g in miner.mine_grammar(defs):
        grammarinfo.append((i, g))
    with open("%s.tmp" % sys.argv[1], "wb") as f:
        pickle.dump(grammarinfo, f)
