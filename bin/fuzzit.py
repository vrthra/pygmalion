#!/usr/bin/env python3
import sys
import os
import pickle
import pygfuzz.fuzz as fuzz
import pygmalion.grammar as g
import time
import string
import collections

All_Characters = set(string.ascii_letters + string.digits + string.punctuation)

class PFuzz(fuzz.GFuzz):
    def is_symbol(self, v):
        if type(v) is g.NTKey:
            return True
        return False

CClass = collections.namedtuple('CClass', 'charset count')

def to_charclass(elt, count):
    mycount = None
    if type(count) is int:
        mycount = (count,)
    elif type(count) is set:
        mycount = tuple(count)
    else:
        assert False
    if type(elt) is g.Choice:
        assert False
    elif type(elt) is g.Box:
        assert type(elt.v) is set
        return CClass(tuple(elt.v), mycount)
    elif type(elt) is g.Not:
        assert type(elt.v) is g.Box
        assert type(elt.v.v) is set
        return CClass(tuple(All_Characters - elt.v.v), mycount)
    assert False

def translate(grammar):
    ng = {}
    for k in grammar:
        alternatives = grammar[k]
        newrules = []
        for rule in alternatives:
            newrule = []
            for elt in rule.rvalues():
                newelt = None
                if type(elt) is tuple:
                    newelt = to_charclass(*elt)
                elif type(elt) is g.NTKey:
                    newelt = elt
                newrule.append(newelt)
            newrules.append(tuple(newrule))
        ng[k] = tuple(newrules)
    return ng

if __name__ == "__main__":
    max_sym = int(os.getenv('MAXSYM') or '100')
    nout = int(os.getenv('NOUT') or '100')
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammar = pickle.load(fin)
    assert type(grammar) is dict
    start = time.perf_counter()
    mylst = []
    fuzzer = PFuzz(translate(grammar))
    start_symbol = g.NTKey(g.V.start())
    for i in range(nout):
        v = fuzzer.produce(start_symbol, max_sym)
        t = time.perf_counter() - start
        print(i, t, repr(v), file=sys.stderr, flush=True)
        mylst.append((v,t))
    pickle.dump(mylst, fout)
