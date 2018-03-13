#!/usr/bin/env python3
import induce.refiner as refiner
import induce.miner as miner
import induce.grammar as g
import sys
import pickle
from induce.bc import bc
import pudb; brk = pudb.set_trace


def nt_key_to_s(i):
    v = i.k
    return "[%s:%s]" % (v.func, v.var)

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'w')
    grammar = pickle.load(fin)
    newg = {}
    for key in grammar.keys():
        rules = grammar[key]
        newk = bc(bc.okgreen).o(nt_key_to_s(key))
        if newk not in newg:
            newg[newk] = set()
        newr = newg[newk]
        for r in rules:
            my_str = []
            for i in r.rvalues():
                if type(i) == miner.NTKey:
                    str_var = bc(bc.okblue).o(nt_key_to_s(i))
                else:
                    str_var = str(i)
                my_str.append(str_var)
            newr.add(''.join(my_str))
    x = g.Grammar(newg)
    if len(sys.argv) > 1:
        print(str(x), file=sys.stderr)
    print(str(x), file=fout)
