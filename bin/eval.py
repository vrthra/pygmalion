#!/usr/bin/env python3
import sys
import taintedstr
import coverage
import linecache
import imp
import os
import pickle
import pudb
import pygmalion.config as c
brk = pudb.set_trace

Branch =  (os.getenv('BRANCH') or 'false') in {'true', '1'}

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
    all_n = 0
    cov = coverage.Coverage(source=['example'], branch=Branch)
    mylst = pickle.load(fin)
    last_t = 0
    for j,(i, t) in enumerate(mylst):
        try:
            #print(j, repr(i), flush=True, end='')
            cov.start()
            all_n += 1
            v = mod_obj.main(taintedstr.tstr(i))
            cov.stop()
            valid_n += 1
        except:
            pass
        last_t = t
        f = cov.report(file=open(os.devnull, 'w'))
        print(j, "coverage: %.2f%%" % f, ' at ', '%.2f seconds' % t, repr(i), flush=True)
    cov.save()
    c = cov.report(file=fout)
    print("Valid: %d/%d with %f coverage at %f seconds" % (valid_n, all_n, c, last_t))
    cov.html_report(directory='coverage')
    cov.erase()
