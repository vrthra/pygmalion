#!/usr/bin/env
import sys
import pickle
import pygmalion.fuzz as fuzz

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammar = pickle.load(fin)
    print(fuzz.produce(grammar, 100))
