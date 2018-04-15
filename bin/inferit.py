#!/usr/bin/env python3
import sys
sys.path.append('.')
import pygmalion.grammar as g
import pygmalion.config as config
import os
import pickle
import resource
resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    parse_trees = pickle.load(fin)
    if config.Infer == 'COMPLETE':
        import pygmalion.infer as infer
        grammar = infer.infer_grammar(parse_trees)
        print(str(grammar), file=sys.stderr)
        pickle.dump(grammar, fout)
    elif config.Infer == 'LOSSY':
        import pygmalion.induce as induce
        grammar = induce.induce_grammar(parse_trees)
        print(str(grammar), file=sys.stderr)
        pickle.dump(grammar, fout)
