#!/usr/bin/env python3
import os
import pickle
import sys
import pygmalion.grammar as g
import time
import pudb
brk = pudb.set_trace

if __name__ == "__main__":
    max_sym = int(os.getenv('MAXSYM') or '100')
    nout = int(os.getenv('NOUT') or '100')
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammar = pickle.load(fin)
    print(g.grammar_to_bnf(grammar))
