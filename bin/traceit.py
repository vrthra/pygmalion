#!/usr/bin/env python3
import taintedstr as tainted
import sys
import os.path
import pygmalion.ftrace as tracer
import pickle
import imp
from contextlib import contextmanager

@contextmanager
def opened_file(f):
    if not f:
        yield sys.stdout.buffer
    else:
        with open(f, 'wb') as f:
            yield f

if __name__ == "__main__":
    m_file = sys.argv[1]
    mod_obj = imp.new_module('example')
    mod_obj.__file__ = m_file
    code = compile(open(m_file).read(), os.path.basename(m_file), 'exec')
    exec(code, mod_obj.__dict__)
    if len(sys.argv) > 2 and sys.argv[2] == '-o':
        fn = None
    else:
        fn = ".pickled/%s.tmp" % os.path.basename(m_file)
    with opened_file(fn) as trace_file:
        # Infer grammar
        for _i in mod_obj.inputs():
            i = tainted.tstr(_i)
            with tracer.Tracer(i, trace_file) as t:
                t._my_files = ['%s' % os.path.basename(m_file)]
                t._skip_classes = mod_obj.skip_classes() if hasattr(mod_obj, 'skip_classes') else []
                o = mod_obj.main(i)
