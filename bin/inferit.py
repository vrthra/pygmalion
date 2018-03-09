#!/usr/bin/env python3
import induce.miner as miner
import induce.grammar as g
import sys
import pickle

if __name__ == "__main__":
    traces = pickle.load(open(sys.argv[1], "rb" ))
    grammar = miner.infer_grammar(traces)
    print("Merged grammar ->\n" + str(grammar))
