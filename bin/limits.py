#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import resource
try: resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
except: pass
sys.setrecursionlimit(0x100000)

def execfile(filename, globals=None, locals=None):
    if globals is None:
        globals = sys._getframe(1).f_globals
    if locals is None:
        locals = sys._getframe(1).f_locals
    with open(filename, "r") as fh:
        exec(fh.read()+"\n", globals, locals)

del sys.argv[0]
execfile(sys.argv[0])
