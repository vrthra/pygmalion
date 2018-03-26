#!/usr/bin/env python3
import sys
import os
import pickle
import pygmalion.fuzz as fuzz

if __name__ == "__main__":
    max_sym = int(os.getenv('MAXSYM') or '100')
    nout = int(os.getenv('NOUT') or '100')
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammar = pickle.load(fin)
    for i in range(nout):
        v = fuzz.produce(grammar, max_sym)
        print(i, repr(v), file=sys.stderr, flush=True)
        pickle.dump(v, fout)
