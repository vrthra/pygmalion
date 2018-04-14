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

    fin = sys.stdin.buffer if len(sys.argv) < 3 else open(sys.argv[2], 'rb')
    fout = sys.stdout if len(sys.argv) < 3 else open("%s.tmp" % sys.argv[2], 'w')
    valid_n = 0
    cov = coverage.Coverage()
    cov.start()
    for j,(i, t) in enumerate(records(fin)):
        try:
            print(j, repr(i))
            v = mod_obj.main(taintedstr.tstr(i))
            print("\t=>",v)
            valid_n += 1
        except:
            pass
        print("%", cov.report(file=fout), ' at ', t, 'seconds')
    cov.stop()
    print("Valid:", valid_n)
    cov.save()
    print(cov.report(file=fout))
    cov.html_report(directory='coverage')
