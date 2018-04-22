#!/usr/bin/env python3
import sys
import pygmalion.util as u
import pygmalion.config as config
import pygmalion.infer as infer
import os
import pickle
import resource

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    parse_trees = pickle.load(fin)
    grammar = infer.infer_grammar(parse_trees)
    print(u.readable_grammar(grammar._dict), file=sys.stderr)
    pickle.dump(grammar._dict, fout)
