#!/usr/bin/env python3

import sys
sys.path.append('.')
import taintedstr
import coverage
import linecache
import imp
import os
import pickle
import resource
import pygmalion.util as u
import pygmalion.learner as learner
resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)

import pygmalion.fuzz as fuzz

def records(f):
    try:
        while not f.closed:
            yield pickle.load(f)
    except EOFError:
        raise StopIteration

if __name__ == "__main__":
    m_file = sys.argv[1]
    mod_obj = imp.new_module('example')
    mod_obj.__file__ = m_file
    mod_obj._MODULE_SOURCE_CODE = open(m_file).read()
    code = compile(mod_obj._MODULE_SOURCE_CODE, os.path.basename(m_file), 'exec')
    exec(code, mod_obj.__dict__)
    # (size, mtime, lines, fullname)
    linecache.updatecache(m_file)
    #linecache.cache[os.path.basename(m_file)] = linecache.cache[m_file]
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[2], 'rb')
    fout = sys.stdout if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[2], 'w')

    grammar = pickle.load(fin)
    new_grammar = learner.learn_grammar(grammar)
    # eval grammar and new_grammar if new_grammar is better, update with
    # new_grammar
    print(u.show_grammar(new_grammar))
    print(u.show_grammar(new_grammar), file=fout)
