#!/usr/bin/env python3
import sys
import pygmalion.miner as miner
import os
import pickle
import resource

def reconstitute(g):
    def djs_to_string(djs):
        return "\n\t| ".join([i.inputval(g).replace('\n', '\n|\t')
            for i in sorted(djs)])
    def fixline(key, rules):
        fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
        return fmt % (key, djs_to_string(rules))
    return "\n".join([fixline(key, g[key]) for key in g.keys()])

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    defs = pickle.load(fin)

    parse_trees = []
    for j, (i, xins, g) in enumerate(miner.mine_parse_tree(defs)):
        if os.getenv('DEBUG'):
            print(g, file=sys.stderr)
            print("Reconstitued:", file=sys.stderr)
            print(reconstitute(g), file=sys.stderr)
        print("mine:", j, repr(i), flush=True, file=sys.stderr)
        parse_trees.append((i, xins, g))
    pickle.dump(parse_trees, fout)
