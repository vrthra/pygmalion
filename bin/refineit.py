#!/usr/bin/env python3
import pygmalion.refiner as refiner
import pygmalion.config as config
import pygmalion.util as u
import sys
import os
import pickle
from pygmalion.bc import bc
import pudb; brk = pudb.set_trace

if os.getenv('SHOW_COMPARISONS') == 'true':
    config.Show_Comparisons = True

green = bc(bc.green)
blue = bc(bc.blue)
yellow = bc(bc.yellow)
red = bc(bc.red)


if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammar = pickle.load(fin)
    x = refiner.refine_grammar(grammar)
    if len(sys.argv) > 1:
        print(u.show_grammar(x), file=sys.stderr)
    pickle.dump(x, file=fout)
