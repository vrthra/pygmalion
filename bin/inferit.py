#!/usr/bin/env python3
import pygmalion.infer as infer
import pygmalion.grammar as g
import sys
import pickle

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammarinfo = pickle.load(fin)
    grammar = infer.infer_grammar(grammarinfo)
    if len(sys.argv) > 2:
        print(str(grammar), file=sys.stderr)
    pickle.dump(grammar, fout)
