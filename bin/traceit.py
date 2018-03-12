#!/usr/bin/env python3
import induce.tstr as tstr
import sys
import os.path
import induce.ftrace as tracer
import pickle
import imp

if __name__ == "__main__":
    m_file = sys.argv[1]
    mod_obj = imp.new_module('example')
    mod_obj.__file__ = m_file
    code = compile(open(m_file).read(), os.path.basename(m_file), 'exec')
    exec(code, mod_obj.__dict__)
    with open(".pickled/%s.trace.tmp" % os.path.basename(m_file), 'wb') as trace_file:
        # Infer grammar
        for _i in mod_obj.inputs():
            i = tstr.tstr(_i)
            with tracer.Tracer(i, trace_file) as t:
                t._my_files = ['%s' % os.path.basename(m_file)]
                t._skip_classes = mod_obj.skip_classes() if hasattr(mod_obj, 'skip_classes') else []
                o = mod_obj.main(i)
