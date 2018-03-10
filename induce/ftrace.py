#!/usr/bin/env python3

from typing import Dict, Tuple, Any, Optional, List, BinaryIO

import sys
import pickle
import inspect
from . import tstr

# pylint: disable=multiple-statements,fixme, unidiomatic-typecheck
# pylint: line-too-long

# TODO: Figure out how globals fits into this.
# Globals are like self in that it may also be considered an input.
# However, if there is a shadowing local variable, we should ignore
# the global.


class Tracer:
    """
    Extremely dumb Tracer for tracing the execution of functions
    """
    def __init__(self, in_data: str, tfile: BinaryIO) -> None:
        self.method = self.tracer()
        self.in_data = in_data
        self.trace_file = tfile
        self.trace_i = 0
        self.listeners = {'call', 'return', 'line'}

    def __enter__(self) -> None:
        """ set hook """
        event = {'event': 'start', '$input': self.in_data}
        self.out(event)
        self.oldtrace = sys.gettrace()
        sys.settrace(self.method)

    def __exit__(self, typ: str, value: str, backtrace: Any) -> None:
        """ unhook """
        sys.settrace(self.oldtrace) #type: ignore
        self.out({'event': 'stop'})

    def out(self, val: Dict[str, Any]) -> None:
        pickle.dump(val, self.trace_file)

    def _f_code(self, c: Any) -> Dict[str, Any]:
        return {'co_argcount': c.co_argcount,
                'co_code':c.co_code,
                'co_cellvars':c.co_cellvars,
                'co_consts':[(type(c).__name__,str(c)) for c in c.co_consts],
                'co_filename':c.co_filename,
                'co_firstlineno':c.co_firstlineno,
                'co_flags':c.co_flags,
                'co_lnotab':c.co_lnotab,
                'co_freevars':c.co_freevars,
                'co_kwonlyargcount':c.co_kwonlyargcount,
                'co_name':c.co_name,
                'co_names':c.co_names,
                'co_nlocals':c.co_nlocals,
                'co_varnames':c.co_varnames
                }

    def _f_var(self, v: Dict[str, Any]) -> Dict[str, Any]:
        def process(v: Any) -> Any:
            tv = type(v)
            if tv in [str, int, float, complex, str, bytes, bytearray]:
                return v
            elif tv in [set, frozenset, list, tuple, range]:
                return tv([process(i) for i in v])
            elif tv in [dict]: # or hasattr(v, '__dict__')
                return {i:process(v[i]) for i in v}
            else:
                return tstr.get_t(v)
        return {i:process(v[i]) for i in v}

    def _frame(self, f: Any) -> Dict[str, Any]:
        return {'f_code':self._f_code(f.f_code),
                # 'f_globals':self._f_var(f.f_globals),
                'f_locals':self._f_var(f.f_locals),
                'f_lasti':f.f_lasti,
                'f_lineno':f.f_lineno}

    def tracer(self) -> Any:
        """ Generates the trace function that gets hooked in.  """

        def loc(c: Any) -> Tuple[str, str, int]:
            """ Returns location information of the caller """
            return (c.f_code.co_filename, c.f_lineno, c.f_code.co_name)

        def traceit(frame: Any, event: str, arg: Optional[str]) -> Any:
            """ The actual trace function """
            vself = frame.f_locals.get('self')
            # dont process if the frame is tracer
            # this happens at the end of trace -- Tracer.__exit__
            if type(vself) == Tracer: return
            if event not in self.listeners: return

            frame_env = {'frame': self._frame(frame), 'loc': loc(frame),
                    'i': self.trace_i, 'event': event, 'arg': arg}
            self.out(frame_env)
            self.trace_i += 1
            return traceit
        return traceit
