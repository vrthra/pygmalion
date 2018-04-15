#!/usr/bin/env python3
import sys
import resource
resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)
sys.path.append('.')
import os
import pickle
import pygmalion.miner as miner
import pygmalion.refiner as refiner
import time
import pudb
brk = pudb.set_trace

def to_str(i):
    if isinstance(i, miner.NTKey):
        return "'%s" % fmt_key(i.k)
    elif isinstance(i, list):
       return ' ~ '.join([to_str(j) for j in i])
    elif isinstance(i, refiner.Choice):
        if i.a: return "\"%s\".regex " % i.a
        elif i.b: return "\"%s\".regex " % refiner.Not(i.a)
        assert False
    elif isinstance(i, str):
        return "\"%s\"" % i
    else: return str(i)

def elts_to_str(lstrule):
    return ' ~ '.join(to_str(i) for i in lstrule.rvalues())

def djs_to_string(djs):
    vals = [elts_to_str(i).replace('\n', '\n            |  ') for i in djs]
    return "\n            | ".join(vals)

def fmt_key(key):
    func = key.func.replace('@.', '')
    return "%s$%s$%s" % (func, key.var, key.t)

def fixline(key, rules):
    fmt = "'%s := %s," if len(rules) == 1 else "'%s :=  %s,"
    return fmt % (fmt_key(key.k), djs_to_string(rules))

def show_grammar(g):
    return "\n".join([fixline(key, g[key]) for key in g])

if __name__ == "__main__":
    max_sym = int(os.getenv('MAXSYM') or '100')
    nout = int(os.getenv('NOUT') or '100')
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')
    grammar = pickle.load(fin)
    hgrammar = grammar._dict
    print("new GrammarFile(")
    for k in hgrammar:
        print("   ",fixline(k, hgrammar[k]))
    print(")")
    
