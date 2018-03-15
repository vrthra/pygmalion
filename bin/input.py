#!/usr/bin/env python3
import induce.tstr as tstr
import sys
import os.path
import pickle
import json
import imp
from contextlib import contextmanager
import pychains.execfile
from  pychains.vm import Op
import pudb
brk = pudb.set_trace

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
        fn = ".pickled/%s.i.tmp" % os.path.basename(m_file)
    with opened_file(fn) as trace_file:
        # Infer grammar
        for x,i in enumerate(mod_obj.inputs()):
            pychains.execfile.PrefixArg = i
            e = pychains.execfile.ExecFile()
            e.cmdline(i)
            outputs = {}
            for o in e.cmp_output:
                op = o.opA.x()
                if op not in outputs: outputs[op] = []
                outputs[op].append(o)
            pickle.dump(outputs, trace_file)
            #pickle.dump(e.cmp_output, trace_file)
            #for o in e.cmp_output:
            #    opB = o.opB if type(o.opB) not in [set, list, dict] else [o for o in o.opB]
            #    print(json.dumps({"pos": o.opA.x(),
            #                      "opA":str(o.opA),
            #                      "opB":opB,
            #                      "op":Op(o.opnum).name}))

